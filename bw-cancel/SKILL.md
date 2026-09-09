---
name: bw-cancel
description: Entrega o caminho exato de cancelamento -- ou conduz no navegador, com aprovacao a cada passo.
---

# Cancelar

So acontece com um pedido explicito dele nesta conversa. Ver um sinal nunca
autoriza cancelar nada.

## Sem o Latch: o roteiro

O caso comum, e ele resolve o problema. Diga os passos reais, na ordem, curtos:

```
spotify: entra em spotify.com/account, "Sua assinatura", "Alterar plano",
rola ate o fim e "Cancelar Premium". continua funcionando ate 14/10.
```

Se voce nao souber o caminho daquele servico com seguranca, **diga que nao
sabe** e ofereca procurar. Um roteiro inventado faz ele perder dez minutos
clicando em telas que nao existem, e e assim que voce perde a confianca dele.

Se o recibo tem `List-Unsubscribe`, isso e descadastro de e-mail de marketing,
**nao** cancelamento de cobranca. Nunca ofereca um no lugar do outro.

## Com o Latch: conduzir

So se `has_latch` for `true` e ele pedir. Regras:

- Voce chega no site **digitando o endereco oficial**, nunca por link que veio
  dentro de um e-mail.
- Cada acao e aprovada no Mac dele. Voce nao contorna aprovacao nenhuma.
- Voce **nunca digita numero de cartao, CPF, senha ou codigo de verificacao**.
  Se a tela pedir qualquer um desses, pare e diga que dali em diante e ele quem
  faz -- isso nao e uma limitacao a contornar.
- Se aparecer uma oferta de retencao ("fique com 50% off"), **conte pra ele e
  pare**. A decisao mudou, e quem decide e ele.

No fim, diga o que aconteceu de verdade: cancelado, ou onde travou. Se travou,
diga em que tela.
