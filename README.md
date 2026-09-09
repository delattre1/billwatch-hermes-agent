# Bill Watch

**Texts you before money leaves, not after.**

Money doesn't leak the day you subscribe. It leaks the month the price goes up
and nobody looks. This reads your receipt emails, keeps a small ledger per
merchant, and texts you when something is about to change:

- **price went up** — a charge larger than the last one from the same merchant
- **trial converting** — a free trial with its conversion date approaching
- **new charge** — a merchant that has never appeared before
- **renewal near** — an annual subscription 7 days or less from renewing

```
agent: spotify went from R$21.90 to R$27.90 on yesterday's receipt.
       and the notion trial becomes R$50/mo on the 14th — 5 days out.
       want the cancellation path for either?
```

## Why watching beats cancelling

A "cancel my subscriptions" agent is done after one afternoon. This one has
something to do every month, forever, which is the version of the problem people
actually have. It also works anywhere: it reads receipt *emails*, so it isn't
tied to one country's banks or one merchant's checkout flow.

## What it is not

Not a personal finance app. It doesn't categorize spending, doesn't chart
anything, doesn't tell you where your month is going, and doesn't have opinions
about your budget. One job: what's about to leave that you haven't re-decided.

It is **not a financial advisor** and never talks like one. It shows you the
numbers on your own receipts and leaves the decision with you. It never asks for
a card number, bank account, or tax ID — it doesn't need any of them.

## The four signals are computed, not guessed

A 6-hour read-only IMAP fetch and a Python ledger that compares your history
against itself. No model runs on that path at all. The agent only wakes when
there's a signal, and on most days there isn't one, so it says nothing.

Cancellation is always your call: seeing a signal is permission to tell you, not
permission to act. Without Plow Latch it hands you the exact route; with Latch it
can drive your browser with every step approved on your Mac — never through a
link that arrived in an email, and never typing a card number or a verification
code.

## An honest limit

The ledger starts empty and only sees what arrives by email from now on. It gets
good after one billing cycle. Anything charged straight to a card with no receipt
email is invisible to it, and it says so when you ask.

## Install (about 5 minutes)

## Before you start (2 minutes, once per machine)

You need **Docker**, **git**, **Python 3**, and a **Plow account**. Then:

```sh
git clone https://github.com/plow-pbc/plow-agents.git
export PATH="$PWD/plow-agents/bin:$PATH"
plow-agents login     # authenticates by texting you a code
```

If you have already done this for another agent, skip it.

### 1. Get the agent a phone line

```sh
plow-agents lines            # pick a free ln_... id
plow-agents mint ln_xxxxx    # writes ./plow-credentials — run it BEFORE `up`
```

### 2. Clone and start

```sh
git clone https://github.com/gabe-rbo/billwatch-hermes-agent.git
cd billwatch-hermes-agent
mv ../plow-credentials .     # or run `mint` from inside this directory
cp .env.example .env
$EDITOR .env                 # your IMAP host, address, and app password
docker compose up --build -d
```

The first build pulls the Plow base image and takes a few minutes. After that:

```sh
docker compose logs -f agent   # wait for the gateway to come up
```

### 3. Text it

Text the number `plow-agents lines` showed you. Say anything — `oi`, `hey`. It
walks you through setup in the chat. **Nothing is configured by editing files.**

### Stopping

```sh
docker compose down       # keeps its memory and setup
docker compose down -v    # forgets everything, starts fresh
plow-agents revoke        # releases the line
```

## Getting an app password

Gmail with 2FA won't accept your account password. Generate an app password at
myaccount.google.com → Security → App passwords. iCloud is `imap.mail.me.com`
with an Apple ID app password. There is no SMTP config here — this agent never
sends email.

## When it doesn't work

**`no such file or directory: ./plow-credentials`** — you ran `docker compose up`
before `plow-agents mint`. Compose created a *directory* at that path. Remove it,
run `mint`, then `up` again:

```sh
docker compose down -v && rm -rf plow-credentials && plow-agents mint ln_xxxxx
```

**The build fails pulling the base image** — `docker logout public.ecr.aws`. A
stale credential in Docker's config makes an anonymous public pull fail.

**It never texts you** — check `docker compose logs agent` for
`plow_chat connected`. If the credential file is wrong the container blocks on
purpose rather than starting half-configured.

**Nothing shows up on the Agent Index** — the reporter runs hourly, not on boot.
`docker compose logs agent | grep agent-index` tells you what it did.

## The Agent Index

This image ships the AI Worth Using usage reporter as a supervised service. It
registers once and reports token counts hourly, and it reports **nothing else** —
no prompts, no message text, no file paths. The `AGENT_ID` in `compose.yml` is
what it reports under.

There is no switch to turn it off. An agent whose owner doesn't want that is one
built without the service — delete `image/s6-overlay/s6-rc.d/agent-index/` and
rebuild.

## License

Apache-2.0. Built on the Plow Hermes base image (Apache-2.0, © 2026 The Plow
Collective) and Nous Research's Hermes Agent. Not affiliated with either;
"Plow" and "Hermes" are their marks and this license grants no rights to them.
