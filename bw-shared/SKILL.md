---
name: bw-shared
description: Scripts compartilhados do vigia: busca somente leitura, livro-caixa, e o canal de mensagem.
---

# Ferramentas do vigia

Este diretorio nao e um procedimento -- e a caixa de ferramentas que os outros
sheets deste agente chamam. Nada aqui deve ser executado "porque o skill foi
carregado"; cada script tem um chamador nomeado.

## `scripts/mailbox.py`
A busca IMAP, **somente leitura**. Roda a cada 6h sob o s6 pela copia de
`/opt/plow`.

## `scripts/ledger.py`
Transforma recibos em livro-caixa e livro-caixa em sinais, tudo determinista,
sem modelo. Roda logo depois da busca no mesmo tick. A primeira passada de um
livro vazio e linha de base: ela aprende e nao emite `cobranca-nova`.

## `scripts/notify.py`
A mensagem condicional. Chamado por `bw-report`, e por mais ninguem.

## O caminho importa

Chame sempre por `$HERMES_HOME/skills/bw-shared/scripts/...`.

A imagem entrega os sheets em `/opt/hermes/skills`, o runtime os reconcilia
para `$HERMES_HOME/skills`, e e o segundo que um agente em execucao encontra.
Um sheet que nomeia o caminho da imagem funciona no dia do build e falha depois.

A copia root-owned em `/opt/plow/` existe para o que roda sozinho sob o
supervisor. Ela nao e sua para chamar: o que voce roda dentro de um turno vem da
casa; o que roda sem ninguem olhando vem de `/opt/plow`, e essa separacao e o
que impede uma unica edicao por prompt-injection de virar codigo agendado.
