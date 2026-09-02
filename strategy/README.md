# RATCHET — trading strategy for Robinhood account ••••8464

An original strategy designed specifically for the "Agentic" account
(limited margin · options level 3 · $1,500 · no open positions).
Not derived from any existing published model or third-party system.

## Contents

| File | What it is |
|---|---|
| [`RATCHET.md`](RATCHET.md) | The full specification. Start here. |
| [`ratchet_rules.json`](ratchet_rules.json) | Machine-readable rulebook for the agent to enforce |
| [`sim/ratchet_sim.py`](sim/ratchet_sim.py) | 20,000-path Monte Carlo backing the claims in §7 |
| [`sim/RESULTS.txt`](sim/RESULTS.txt) | Committed output of that simulation |

Run the simulation with `python3 sim/ratchet_sim.py` (pure stdlib, no deps).

## The idea in one paragraph

Split the account 70/30. The **Core** sleeve buys and holds a broad index ETF and
is never sold to fund a trade. The **Convexity** sleeve trades defined-risk debit
verticals on two setups only — a volatility-compression break and a
post-earnings drift entered *after* the IV crush. Every Friday the **ratchet
clicks**: profits above the sleeve's charter size are swept permanently into
Core, and losses are refilled only slowly, capped at 2% of equity per week and
20% of equity per year. Bet size therefore tracks *banked* equity and nothing
else — not recent P&L, not conviction. Winning cannot scale you up; losing
cannot scale you up either. The account's day-trade budget (3 per 5 sessions,
because equity is under $25,000) is rationed as insurance for exits only, never
spent on entries — which forces every position to be built to survive overnight.

## On the "2x daily" goal

It was requested and it cannot be built. 100%/day compounds to 2^252 ≈ 7.2×10^75
in a year, which exceeds all world financial assets by ~60 orders of magnitude
around day 60. This account is also blocked by rule: under $25,000 it is capped
at 3 day trades per 5 business days, and a daily-doubling scheme needs ~5 a week.

The simulation makes the deeper point. A full-size daily bet with proper
stop-losses and a **flat arithmetic edge** still goes to zero in **100% of
20,000 paths**, median 13 sessions — because betting the whole account drives
the *geometric* return to −21% per trade even when the average trade is fine.
That is volatility drag, and no amount of skill or discipline fixes it. Only
sizing does.

RATCHET's realistic target is **≈ +22%/yr** at a 45% hit rate — doubling the
account in about **3.5 years**, with a simulated probability of ruin of **0.0%**
and a 5th-percentile outcome of about **−32%** even when the strategy is losing.

## Status

Specification only. **No trades have been placed.** Not financial advice.
All expectancy figures are illustrative calculations from assumed hit rates, not
backtested results — see §7 and §11 of the spec.
