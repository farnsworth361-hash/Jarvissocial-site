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

## RATCHET — RETIRED 2026-11-06

**The account no longer runs RATCHET.** On 2026-11-06 the holder instructed the
Core sleeve closed and rolled into SpaceX: sold 3.358353 SPY @ $740.705, bought
19.003746 SPCX @ $131.2899 — then, three hours later, sold that and went **all
in on SPCH, a 2x leveraged fund on SPCX**. Core-is-SPY was the charter's first
rule, so the framework no longer describes this account. It had already been
unfunded from 2026-09-08 and **unimplementable** from 2026-09-10, when a live
order revealed this account rejects multi-leg options orders and therefore cannot
place the debit verticals the Convexity sleeve is built from.

**Current position: 349.519410 SPCH @ $7.2099, cost $2,520.00, ~99.9% of the
account** (bought 2026-11-06, order `6aee1d90-4104-4ff4-a347-cf3779f0b920`).
SPCH is **not SpaceX** — it is a 2x daily-reset leveraged fund on SPCX, which
itself runs 79.7% annualized volatility with a −46.3% worst drawdown in five
months of listed history. Consequences, all verified and all still true:

- **Volatility drag at k=2 is σ², i.e. −63.5%/yr of log return** at SPCX's vol —
  roughly **−47% over a flat year.** SPCX can end a year unchanged and this
  position still halves.
- **A ~50% adverse move in SPCX is a wipeout.**
- **The final SpaceX lockup tranche clears 2026-12-08** (verified 2026-11-09;
  staggered S-1 schedule, not a single 180-day cliff; ~40% of the company
  tradable after it; Musk locked until ~June 2027). Past unlocks have **not**
  reliably been down days — the largest, 2026-08-06, saw the stock rally — so
  this is a dated supply event taken at 2x, not a prediction.

There is no sleeve structure, no position cap, no stop and no stated holding
period. **Nothing in `strategy/` describes a leveraged single-stock position** —
in particular the expectancy and break-even figures in `RATCHET.md` §7 assume
debit verticals and **must not be cited for this position.** It was recommended
against; the holder overrode that on the numbers, which is their call.

**What still applies, and why it was expensive to learn:**

- **Verify, never recall.** This model's training ends May 2026. SPCX listed
  2026-06-12 and on 2026-11-06 it was asserted here that SpaceX was private and
  untradable — wrong, and corrected only by calling the tools. Any claim about
  what exists or is tradable comes from a tool call. The same day a lockup date
  was *guessed* as "around Dec 9" and happened to land within a day of the real
  Dec 8 — a correct unsourced claim is still an unsourced claim. Cite the source
  or do not state it.
- **Multi-leg options orders are rejected on this account**, opening or closing.
  `review_option_order` accepts multi-leg previews, so only a live
  `place_option_order` surfaces it. Any options exit plan here must be
  **single-leg by construction**; if a spread ever exists, leg out **short leg
  first** so the interim position is long-only and needs no collateral.
- **PDT binds** below $25,000: three day trades per rolling five business days.
- `human_must_approve_trades` has read **false** since 2026-08-26. Only the
  holder can change it, in the Robinhood app.
- Two agentic orders on 2026-09-08 and 2026-09-17 did not originate from this
  session. Another agent connection holds trade authority here.

**Account: ONLY ••••8464, nicknamed "Agentic."** Never touch another account,
even read-only, without an explicit request. There is no account nicknamed
"Claude" — the holder confirmed on 2026-09-03 that "Agentic" is the one they
mean. Confirm the account and buying power at the start of every session.

**Selling Core, changing the account's instrument, or any new strategy still
needs an explicit instruction from the holder.** The 2026-09-04 "fire within the
rails" grant below is kept for the record, but there are no rails now: it
authorises nothing until a new framework exists.

<details>
<summary>Historical — the retired RATCHET rules</summary>

**AUTHORITY — FIRE WITHIN THE RAILS (set 2026-09-04).** When every rail passes,
place the order. Do not wait for per-order approval; report the fill afterwards.
This resolves the conflict with the withdrawn 0DTE framework's "never place an
order I haven't approved" — **that clause is dead.** Still needs an explicit
instruction: any other account, selling Core, anything that is not a debit
vertical on a whitelisted name, or any change to the rails themselves. Authority
is to act *inside* the rails, never to relax one — a failing gate is still a
no-trade day.

**SIZING — SIZE EVERY ENTRY TO THE CAP (set 2026-09-04).** Take the largest
whole number of contracts whose total debit is ≤ $150. Never default to 1
contract when 2 or 3 fit under the cap. If one contract exceeds $150, narrow the
width; if it still exceeds, stand down. Check bid/ask **size** on both legs
against the contract count, not just open interest.

The full specification is in `strategy/`. Start at `strategy/README.md`.
Summary:

- **Core sleeve (70%):** broad index ETF, bought and held, never sold to fund a
  trade. Currently **1.367545 SPY**. The holder considered rotating Core into a
  tech fund on 2026-09-03 and decided against it — **Core stays in SPY.**
- **Convexity sleeve (30%, $450 charter):** debit verticals only, 30–45 DTE,
  ~30 delta long leg, **$5 strike grid**, ≤$150 per position **and sized to that
  cap**, max 3 concurrent, max 2 entries per week.
- **Universe:** SPY, NVDA, PLTR. TSLA and MSTR are watchlist only.
- **Setups:** Compression Break, Trend Pullback, Post-Earnings Drift. All fire
  on a **close**, never intraday.
- **Exits:** GTC target at +100% of debit and GTC stop at −50%, placed at fill.
  Time exit at 10 DTE.
- **Day trades are exit insurance only, never entries.** 3 per rolling 5
  business days under PDT; LOCKDOWN at ≤1 remaining.
- **Weekly ratchet click** Friday 15:45 ET; monthly resize of the sleeve
  charter from the equity high-water mark.

**Execution decides the outcome more than the signal does.** Never a market
order on a spread, never leg in, limit at mid and walk at most one tick. On
SPY the $5-grid strikes quote a penny wide against ten cents on the $1 grid,
which moves the break-even hit rate from 34.3% to 47.5%.

**Journal every session**, including no-trade days. Declined signals go in
`strategy/journal/DECISIONS.md` with the failing condition named; fills go in
`trades.csv` with both `debit_mid` and `debit_filled`, because realized
slippage is the earliest testable claim in the strategy.

</details>

## SPY 0DTE — TRIED AND DROPPED 2026-09-03

A single-leg SPY 0DTE framework was specified and then withdrawn the same day;
the holder judged it a poor fit for the account size. **Do not trade 0DTE.**

Worth keeping for the reasoning: every 0DTE round trip is a day trade, so at
sub-$25k equity the PDT rule caps it at 3 per rolling 5 business days — the
framework's "3 trades per day" would have consumed the week's budget on day one
and flagged the account into closing-only for 90 days on the fourth. Robinhood
Gold does not change this: PDT is keyed to $25,000 of equity, borrowed margin
does not count toward it, and long options cannot be bought on margin anyway.

All order-placing triggers from that framework were deleted.
