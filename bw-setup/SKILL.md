---
name: bw-setup
description: Primeira conversa. Confirma a caixa de recibos, a hora do relatorio, e liga a vigilancia.
---

# Colocar o vigia de pe

O IMAP ja esta no `.env` e a busca ja roda. Nao pergunte senha, servidor nem
porta, e **nunca peca uma senha pelo chat**.

Se `$HERMES_HOME/billwatch/config.json` ja existe, isto e um ajuste.

## O que perguntar

1. **Que horas mandar o relatorio.** Um horario, padrao 09:00. Explique que na
   maioria dos dias nao vai chegar nada -- isso e o normal, nao e defeito.
2. **Se ele quer que voce ignore algum comerciante.** Aluguel, mensalidade da
   faculdade, coisas que ele ja decidiu e nao quer ouvir sobre. Opcional.
3. **Se ele tem o Plow Latch no Mac.** Se tiver, voce pode conduzir um
   cancelamento no navegador dele com cada acao aprovada na maquina. Se nao
   tiver, voce entrega o roteiro exato e ele faz -- e isso ja resolve o problema
   principal, que e nao saber que a cobranca ia acontecer.

Nao pergunte mais nada. Nada de cartao, banco, CPF ou valor de renda -- voce nao
precisa de nenhum deles e nao deve guardar nenhum.

## Uma coisa que vale explicar

O livro-caixa comeca vazio, e ele so enxerga o que chega POR E-MAIL a partir de
agora. Um recibo de tres meses atras nao esta na caixa nova. Diga isso: o vigia
fica bom depois do primeiro ciclo de cobranca, e prometer menos agora e o que
faz ele confiar no que voce disser depois.

## Escrever a configuracao

```json
{"report_hour": 9, "ignore": ["aluguel", "ufmg"], "has_latch": false}
```

Em `$HERMES_HOME/billwatch/config.json`.

## Registrar o cron

```
hermes cron create "0 9 * * *" \
  "Rode o bw-report agora: se houver sinal nao avisado, avise. Se nao houver, responda exatamente quiet." \
  --name bw-report --skill bw-report
```

Sem `--deliver`, de proposito: este agente fica quieto na maioria dos dias, e
`--deliver` repassaria toda resposta final -- inclusive as silenciosas. Quem
manda mensagem e o `notify.py`, so quando ha sinal.

`hermes cron list` antes; se ja existe, nao crie de novo.
