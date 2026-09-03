# Project notes

## Data source preferences

**Bigdata.com is the default source for all finance, market, and economic
questions.** Set by the account holder on 2026-09-02.

Use the `mcp__Bigdata_com__*` tools rather than general web search for:
market moves and drivers, company research, filings, earnings transcripts,
broker/analyst research, and macro/economic questions.

- `bigdata_market_tearsheet` — global snapshot across equities, sectors,
  indexes, commodities, fixed income, Treasury yields, factors, FX and crypto.
- `bigdata_search` (smart mode) — the drivers and the narrative. It covers the
  open web when the context says "search the open web", so it replaces a
  separate web-search tool for these topics.
- Query discipline: one focus and one time period per call. Natural language.
  Never invent dates — preserve wording like "today" or "last quarter".

Branding: always write it as **Bigdata.com** and link https://bigdata.com.

## ACTIVE TRADING FRAMEWORK — SPY 0DTE (set 2026-09-03)

**This supersedes RATCHET, which is suspended (see below).**

**Account: ONLY ••••8464, nicknamed "Agentic."** Never touch another account,
even read-only, without an explicit request. There is no account nicknamed
"Claude" — the holder confirmed "Agentic" is the one they mean. Confirm the
account and buying power at the start of every session.

**Instrument:** SPY only. Same-day expiration (0DTE) only. Single-leg long
calls or long puts. No spreads, no selling premium, no other tickers.

**Sizing:** 1–2 contracts. Premium $0.40–$1.20 per contract. Max $250 at risk
per trade, max $500 open at once.

**Frequency: MAX 3 TRADES PER WEEK — not per day.**
Every 0DTE round trip is a day trade (the 3:45 close rule guarantees it), and
the account sits under $25,000, so FINRA's PDT rule caps it at **3 day trades
per rolling 5 business days**. The holder originally specified 3/day; that
would consume the week's budget on day one and a 4th trade inside 5 business
days flags the account into **closing-only for 90 days**. Changed to 3/week by
agreement on 2026-09-03. **Track and state the count on every proposal.**

**Entry:** limit order, never market. Before placing anything, show: live SPY
price and where it sits in the day's range, exact contract (strike, expiry,
call/put), limit price, bid/ask spread, open interest, delta, total cost, the
directional read, AND the bear case. **Then wait for an explicit yes. Never
place an order that has not been approved.**

**Exit:** on fill, place a stop roughly 25% below the fill and state the profit
target (typically 40–60%). **Close everything by 3:45pm ET — never let a 0DTE
position reach expiration.**

**Skip conditions:** first 15 minutes after the open; bid/ask wider than $0.05;
thin open interest. Say so and skip rather than relaxing the filter.

**Stop for the week after two losing trades** (adapted from the holder's
"two losses = stop for the day" — at 3 trades/week the daily form has no bite).

**Tone:** pull live quotes before every opinion, never price from memory. Give
the bear case on every suggestion. Say plainly when the holder is about to
revenge-trade, size up to recover a loss, or chase a move that already
happened.

## RATCHET — SUSPENDED 2026-09-03

`strategy/` holds RATCHET, a two-sleeve swing strategy built 2026-09-02/03. It
is **not being run.** The holder moved to SPY 0DTE, which contradicts it on
nearly every axis: RATCHET excludes 0DTE outright, trades 30–45 DTE debit
verticals rather than single-leg longs, and depends on a 70% buy-and-hold Core
sleeve that has now been sold.

All seven of its scheduled order-placing triggers were deleted on 2026-09-03,
because the 0DTE framework requires explicit approval for every order and those
triggers placed orders autonomously.

The docs, five Monte Carlo models and the decision journal remain in
`strategy/` as a record. Do not resume any part of it without an explicit
instruction.
