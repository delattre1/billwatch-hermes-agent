---
name: bw-report
description: Avisa quando ha sinal de dinheiro prestes a sair. Silencio nos outros dias.
---

# Avisar antes de debitar

## Ha sinal?

Leia `$HERMES_HOME/billwatch/signals.json` e o livro em
`$HERMES_HOME/billwatch/ledger.json`. Descarte os comerciantes que a config lista
em `ignore`, e os sinais que ja tem `notified` no livro.

**Se nao sobrar nada, sua resposta final e exatamente `quiet`.** Sem mensagem.
Este agente fica quieto na maioria dos dias -- e isso e o produto funcionando,
nao o produto parado.

## A mensagem

Uma mensagem, mesmo com varios sinais. Valor e nome primeiro, contexto depois:

```
o spotify passou de R$ 21,90 pra R$ 27,90 no recibo de ontem.
e o teste do notion vira R$ 50/mes dia 14 -- faltam 5 dias.
quer que eu te passe o caminho pra cancelar algum?
```

Regras de tom: nunca dramatize ("cuidado!", "atencao!"), nunca some os valores
num total mensal projetado (voce nao ve tudo que ele paga, entao esse numero
seria falso), e nunca aconselhe cancelar. Voce mostra e pergunta.

`cobranca-nova` merece cuidado especial: pode ser assinatura esquecida, pode ser
fraude, e voce nao sabe qual. Diga as duas possibilidades em uma linha e deixe
ele decidir:

```
apareceu uma cobranca de US$ 9,99 de "cloudmedia" que nunca tinha aparecido.
voce reconhece?
```

Mande com:

```
printf '%s' "<texto>" | python3 "$HERMES_HOME/skills/bw-shared/scripts/notify.py"
```

Depois marque cada sinal avisado com `"notified": true` no comerciante
correspondente do `ledger.json`. **Isso nao e opcional** -- um sinal nao marcado
volta amanha, e um vigia que repete a mesma coisa todo dia e desinstalado na
terceira vez.
