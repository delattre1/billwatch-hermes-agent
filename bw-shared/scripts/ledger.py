#!/usr/bin/env python3
# Copyright 2026 Gabriel Ribeiro
# SPDX-License-Identifier: Apache-2.0
"""ledger.py -- transforma recibos em um livro-caixa, e o livro-caixa em sinais.

Roda sob o s6, sem modelo nenhum. Le a fila que o mailbox.py escreveu, extrai
valor e comerciante de cada recibo, e mantem um historico por comerciante. Depois
compara o historico com ele mesmo e escreve SINAIS -- e so quando ha sinal o
agente gasta um turno.

Essa e a correcao que o agente inteiro existe pra fazer. "Cancele minhas
assinaturas" e uma tarefa de uma vez so: depois de feita, nao ha mais nada. "Me
avise quando algo mudar" acontece todo mes, pra sempre, e e o que uma pessoa
realmente precisa -- porque o dinheiro nao vaza no dia que voce assina, vaza no
dia que o preco sobe e ninguem olha.

Os quatro sinais, todos deterministas:
  preco-subiu       cobranca maior que a anterior do mesmo comerciante
  trial-vai-virar   recibo de teste gratis com data de conversao chegando
  cobranca-nova     comerciante que nunca apareceu antes
  renovacao-perto   assinatura anual a 7 dias ou menos de renovar
"""
import json, os, re, sys, time
from datetime import datetime, timedelta, timezone

HOME = os.environ.get("HERMES_HOME", "/var/lib/hermes")
BASE = os.path.join(HOME, "billwatch")
QUEUE = os.path.join(BASE, "queue")
LEDGER = os.path.join(BASE, "ledger.json")
SIGNALS = os.path.join(BASE, "signals.json")

RENEWAL_WINDOW_DAYS = 7

# Moeda antes ou depois do numero, com separador brasileiro ou americano.
AMOUNT = re.compile(
    r"(?:(R\$|US\$|\$|€|£)\s*([\d.,]{1,12})|([\d.,]{1,12})\s*(BRL|USD|EUR|GBP|reais))",
    re.I)

RECEIPT_TERMS = (
    "recibo", "receipt", "invoice", "fatura", "cobranca", "cobrança", "pagamento",
    "payment", "charged", "renovacao", "renovação", "renewal", "subscription",
    "assinatura", "your order", "confirmacao de pagamento", "nota fiscal",
)
TRIAL_TERMS = (
    "teste gratis", "teste grátis", "free trial", "trial ends", "periodo de teste",
    "período de teste", "trial will end", "avaliacao gratuita", "avaliação gratuita",
)
ANNUAL_TERMS = ("anual", "annual", "yearly", "por ano", "/ano", "/year", "12 meses")

DATE_PATTERNS = (
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), ("y", "m", "d")),
    (re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b"), ("d", "m", "y")),
)


def read_json(path, fallback):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return fallback
    except (OSError, ValueError):
        return fallback


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def to_float(raw):
    """`1.234,56` e brasileiro; `1,234.56` e americano. O ultimo separador
    manda -- se o que vem depois dele tem 1 ou 2 digitos, ele e decimal."""
    raw = raw.strip().rstrip(".,")
    if not raw:
        return None
    last_dot, last_comma = raw.rfind("."), raw.rfind(",")
    cut = max(last_dot, last_comma)
    if cut >= 0 and len(raw) - cut - 1 in (1, 2):
        whole = re.sub(r"[.,]", "", raw[:cut])
        return float(f"{whole}.{raw[cut + 1:]}") if whole.isdigit() else None
    digits = re.sub(r"[.,]", "", raw)
    return float(digits) if digits.isdigit() else None


def amount_in(text):
    best = None
    for match in AMOUNT.finditer(text):
        symbol, first, second, word = match.groups()
        value = to_float(first or second or "")
        if value is None or value <= 0:
            continue
        currency = (symbol or word or "").upper().replace("REAIS", "BRL")
        currency = {"R$": "BRL", "US$": "USD", "$": "USD", "€": "EUR", "£": "GBP"}.get(
            symbol or "", currency)
        # O maior valor da mensagem: recibos citam subtotal, imposto e total, e
        # o total e o que foi debitado.
        if best is None or value > best[0]:
            best = (value, currency or "?")
    return best


def future_date_in(text, horizon_days=90):
    today = datetime.now(timezone.utc).date()
    limit = today + timedelta(days=horizon_days)
    found = []
    for pattern, order in DATE_PATTERNS:
        for match in pattern.finditer(text):
            parts = dict(zip(order, match.groups()))
            try:
                candidate = datetime(int(parts["y"]), int(parts["m"]), int(parts["d"])).date()
            except (ValueError, KeyError):
                continue
            if today <= candidate <= limit:
                found.append(candidate)
    return min(found).isoformat() if found else None


def merchant_of(record):
    addr = (record.get("from_addr") or "").lower()
    domain = addr.split("@")[-1] if "@" in addr else addr
    parts = [p for p in domain.split(".") if p not in ("com", "br", "www", "co", "net", "org")]
    return (parts[0] if parts else domain) or "desconhecido"


def has_any(text, terms):
    low = text.lower()
    return any(term in low for term in terms)


def classify(record):
    text = record.get("untrusted") or ""
    if not has_any(text, RECEIPT_TERMS) and not has_any(text, TRIAL_TERMS):
        return None
    money = amount_in(text)
    return {
        "merchant": merchant_of(record),
        "from_addr": record.get("from_addr"),
        "date": record.get("date"),
        "uid": record.get("uid"),
        "amount": money[0] if money else None,
        "currency": money[1] if money else None,
        "annual": has_any(text, ANNUAL_TERMS),
        "trial": has_any(text, TRIAL_TERMS),
        "next_date": future_date_in(text),
        "unsubscribe": bool(record.get("list_unsubscribe")),
        "seen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


def signals_from(ledger, previously_known):
    """`previously_known` vazio significa PRIMEIRA passada: o livro acabou de
    nascer e todo comerciante e novo. Emitir `cobranca-nova` ali mandaria uma
    mensagem listando tudo que o dono ja sabe que assina, no primeiro dia, que
    e o dia em que ele decide se mantem o agente. A primeira passada e a linha
    de base -- ela aprende e nao fala. Os outros tres sinais continuam valendo,
    porque um aumento ou um trial vencendo sao noticia mesmo no dia um."""
    out = []
    today = datetime.now(timezone.utc).date()
    baseline = not previously_known
    for merchant, entry in ledger.items():
        charges = entry.get("charges") or []
        latest = charges[-1]
        if not baseline and merchant not in previously_known:
            out.append({"kind": "cobranca-nova", "merchant": merchant,
                        "amount": latest.get("amount"), "currency": latest.get("currency"),
                        "detail": "primeiro recibo deste comerciante"})
        paid = [c for c in charges if c.get("amount")]
        if len(paid) >= 2 and paid[-1]["amount"] > paid[-2]["amount"]:
            before, after = paid[-2]["amount"], paid[-1]["amount"]
            out.append({"kind": "preco-subiu", "merchant": merchant,
                        "amount": after, "currency": paid[-1].get("currency"),
                        "detail": f"era {before:.2f}, virou {after:.2f}"})
        if latest.get("trial") and latest.get("next_date"):
            out.append({"kind": "trial-vai-virar", "merchant": merchant,
                        "amount": latest.get("amount"), "currency": latest.get("currency"),
                        "detail": f"o teste vira cobranca em {latest['next_date']}"})
        if latest.get("annual") and latest.get("next_date"):
            try:
                when = datetime.fromisoformat(latest["next_date"]).date()
            except ValueError:
                when = None
            if when and 0 <= (when - today).days <= RENEWAL_WINDOW_DAYS:
                out.append({"kind": "renovacao-perto", "merchant": merchant,
                            "amount": latest.get("amount"),
                            "currency": latest.get("currency"),
                            "detail": f"assinatura anual renova em {latest['next_date']}"})
    return out


def main():
    ledger = read_json(LEDGER, {})
    known_before = set(ledger)
    if not os.path.isdir(QUEUE):
        print("billwatch: fila ainda vazia -- nada a ler")
        return 0

    added = 0
    for name in sorted(os.listdir(QUEUE)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(QUEUE, name)
        record = read_json(path, None)
        if not record or record.get("state") != "novo":
            continue
        charge = classify(record)
        record["state"] = "lido"
        write_json(path, record)
        if not charge:
            continue
        entry = ledger.setdefault(charge["merchant"],
                                  {"from_addr": charge["from_addr"], "charges": []})
        if any(c.get("uid") == charge["uid"] for c in entry["charges"]):
            continue
        entry["charges"].append(charge)
        # O historico serve pra comparar, nao pra arquivar: doze recibos bastam
        # pra ver uma tendencia anual e mantem o arquivo pequeno.
        entry["charges"] = entry["charges"][-12:]
        added += 1

    write_json(LEDGER, ledger)
    found = signals_from(ledger, known_before)
    # Sinais sao substituidos, nunca acumulados: o agente le uma foto do que e
    # verdade agora. Um sinal ja avisado e reescrito com o mesmo conteudo, e o
    # `notified` no proprio livro e o que impede avisar duas vezes.
    write_json(SIGNALS, {"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "signals": found})
    print(f"billwatch: {added} recibos novos, {len(found)} sinais")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
