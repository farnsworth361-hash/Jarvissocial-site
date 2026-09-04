# RATCHET — High-Beta Module

**Adds higher-volatility underlyings to the Convexity sleeve.** Requested
because SPY, at 10.7% IV, is the tamest liquid underlying available and the
account holder wants more aggression.

All quotes live 2026-10-16 expiry (44 DTE), captured 2026-09-02 at the close.
Reproduce with `python3 sim/highbeta_compare.py`.

**No orders placed.**

---

## 1. The finding that should change how you think about this

Five delta-matched ~30-delta $5-wide debit verticals:

| Spread | IV | Debit (mid) | Max profit | R:R | Combined OI | **P(profit)** |
|---|---|---|---|---|---|---|
| SPY 785/790 | 10.7% | $145.00 | $355.00 | 2.45:1 | 26,329 | **22.3%** |
| NVDA 240/245 | 32.5% | $122.50 | $377.50 | 3.08:1 | **65,926** | **21.6%** |
| PLTR 185/190 | 46.2% | $127.50 | $372.50 | 2.92:1 | 7,499 | **21.8%** |
| TSLA 390/395 | 42.4% | $120.00 | $380.00 | 3.17:1 | 4,962 | **20.9%** |
| MSTR 140/145 | 71.4% | $110.00 | $390.00 | 3.55:1 | 9,054 | **21.1%** |

**IV ranges from 10.7% to 71.4% — nearly seven-fold. Probability of profit is
21–22% across every single one.**

That is not a coincidence, it is arithmetic. Delta *is* the standardised
measure of moneyness. A 30-delta option is a 30-delta option whether the
underlying moves 1% a day or 5% a day, because the extra movement is already
in the price you pay. MSTR needs **+13.6%** to reach its long strike where SPY
needs **+2.6%** — but MSTR's 44-day sigma is 24.8% against SPY's 3.7%, so in
standardised terms the two bets are 0.55σ and 0.70σ. Nearly identical.

> **Buying a more volatile name at the same delta does not improve your odds of
> winning. The market is not giving away movement.** Anyone who tells you
> otherwise is selling something.

## 2. What genuinely does improve

Two things, and they are real:

**Reward-to-risk.** A $5 width is a much smaller slice of a volatile name's
expected move, so the debit comes cheaper relative to the width. NVDA pays
**3.08:1** against SPY's 2.45:1.

**The target gets easier as a fraction of max profit.** The exit rule is +100%
of debit. On SPY that is 40.8% of the spread's maximum; on NVDA it is **32.5%**;
on MSTR **28.2%**. Same win probability, less distance to travel before you can
take the money.

So the honest summary: **same odds, bigger payoff when right, bigger loss when
wrong.** That is aggression correctly defined. It is not an edge — it is a
larger bet on the same coin.

## 3. What it costs — the tick problem

**Single-name options quote in $0.05 increments above $3.00** (`min_ticks.
above_tick = 0.05`). SPY quotes in **pennies**. That is a hard floor on how
tight these spreads can ever be, and it is the price of admission:

| Spread | Mid | Crossing | Cross % | BE @ cross | Mid+1 tick | BE @ +1 tick |
|---|---|---|---|---|---|---|
| SPY 785/790 | $145.00 | $146.00 | 0.7% | **34.3%** | $146.00 | **34.3%** |
| NVDA 240/245 | $122.50 | $135.00 | 10.2% | 46.9% | $127.50 | **38.8%** |
| PLTR 185/190 | $127.50 | $145.00 | 13.7% | 51.6% | $132.50 | **38.6%** |
| TSLA 390/395 | $120.00 | $145.00 | 20.8% | 61.1% | $125.00 | **38.9%** |
| MSTR 140/145 | $110.00 | $135.00 | 22.7% | 63.6% | $115.00 | **39.4%** |

Two readings, and the gap between them is the whole ballgame:

- **Crossing the spread** (market order, or an impatient limit) pushes the
  required hit rate to **47–64%**. At those levels none of these are worth
  trading. TSLA and MSTR become outright unplayable.
- **A patient limit filled one tick through mid** lands at **38.6–39.4%** —
  about **4–5 points worse than SPY's 34.3%**, and entirely survivable.

**Execution discipline is not optional on these names. It is the difference
between a viable trade and a donation.**

### Rule correction this forces

§6 of the SPY module says *"walk the price at most $0.02."* **On a nickel-tick
chain you cannot express $0.02.** The rule is unimplementable as written.

**Corrected: walk at most ONE TICK beyond mid** — $0.01 on penny chains (SPY),
$0.05 on nickel chains (all single names). Unfilled at mid + 1 tick → cancel
and stand down. With max 2 entries a week, skipping one costs almost nothing;
paying 10% of the debit to force a fill costs the strategy its edge.

## 4. Verdict per name

**NVDA — ADD. Primary high-beta name.**
Combined OI of **65,926** is 2.5x SPY's on this expiry, with 18,618 contracts
traded today across the two strikes. IV 32.5% (3x SPY). Best R:R of the liquid
group at 3.08:1. Deep books mean a mid-ish fill is realistic rather than
hopeful. This is the one that clearly earns its place.

**PLTR — ADD. Secondary.**
IV 46.2%, 4.3x SPY. Combined OI 7,499 with 3,836 traded today — thinner than
NVDA but comfortably past the 1,000 filter, and the quoted spread is the
tightest of the single names relative to debit (13.7% crossing). Note it fell
**−5.81%** today, so it is already in motion.

**TSLA — WATCHLIST ONLY. Do not trade yet.**
The problem is not the OI headline (4,962) but the depth behind it: **ask size
of 2 and bid size of 3** on the long leg, and only 432/150 contracts traded.
A two-lot offer is not a market you can rely on exiting into under stress. The
20.8% crossing cost reflects that thinness honestly.

**MSTR — WATCHLIST ONLY.**
The highest IV on the board at 71.4% and the best headline R:R at 3.55:1, but
also the worst friction (22.7% crossing, 63.6% break-even). Its P(profit) is
still 21.1% — the volatility buys you nothing in odds. Revisit only if the
quoted spread tightens.

## 5. What single names change structurally

**Setup B comes back to life.** Post-Earnings Drift could never fire on SPY —
an index has no earnings. NVDA and PLTR both report quarterly, which restores
a **second, genuinely uncorrelated return driver** (information diffusion,
versus Setup A's volatility mean-reversion). This is the biggest strategic gain
in the whole module, and it is a side effect rather than the point.

**Earnings also become a live hazard.** §5's rule — *never hold long premium
into an announcement* — was dormant on SPY and is now binding. **Every single-
name entry must verify the earnings date falls after the planned exit.** No
exceptions, and it is a pre-trade check, not a monitoring task.

**Correlation improves, but less than it looks.** SPY + NVDA + PLTR is more
diversified than three SPY positions — but NVDA and SPY are heavily
co-moving, and PLTR is high-beta tech. Treat SPY and NVDA as **partially
correlated**: the §6 correlation cap (max 2 same-direction) applies across the
pair, not to each independently.

**Single-name gap risk is larger.** An index does not gap 15% on a headline; a
single name does. The −50% stop is a *resting order*, not a guarantee — a gap
straight through it takes the full debit. This is already modelled (the
simulator assumes 15% of losers gap past the stop) but it is more likely here,
and the day-trade budget still may not be spent rescuing it.

## 6. Updated Convexity universe

| Symbol | Role | IV | Status |
|---|---|---|---|
| SPY | Index anchor, tightest execution | 10.7% | Active |
| NVDA | Primary high-beta | 32.5% | Active |
| PLTR | Secondary high-beta | 46.2% | Active |
| TSLA | — | 42.4% | Watchlist — book too thin |
| MSTR | — | 71.4% | Watchlist — friction too high |

Unchanged: max $150 risk per position, max 2 same-direction, max 2 entries per
week, 30–45 DTE, GTC exits placed at fill, day-trade budget for exits only,
weekly ratchet, 30% sleeve cap.

## 7. On "maximize profits daily"

This module raises the **size** of each outcome, not the **frequency** of
trades. Entries stay capped at 2 per week, because frequency multiplies
friction while volatility does not. The daily-P&L arithmetic from §7 is
unchanged: at this account size the daily expected return is a small fraction
of the daily noise, and no instrument choice fixes that.

What changes is that a winning NVDA trade now returns 3.08:1 instead of 2.45:1
— and a losing one loses the same $150 faster.

## 8. Disclaimers

Not financial advice. Specification only; no orders placed. Prices are a
2026-09-02 snapshot and will be stale. P(profit) figures are broker-supplied
model outputs, not guarantees. No backtest of Setup A or B on these underlyings
was performed.
