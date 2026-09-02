# RATCHET v1.1

**An original trading strategy built exclusively for Robinhood account ••••8464 ("Agentic").**

Not adapted from any existing published model, newsletter system, or third-party
strategy. Every rule below is derived from the four binding constraints this
specific account actually operates under.

- **Author:** Claude Code, for farnsworth361
- **Designed:** 2026-09-02 · **v1.1** corrects the strike-grid rule (§6)
- **SPY-only adaptation:** see `SPY-MODULE.md`
- **Account snapshot at design time:** limited margin individual · options level 3 ·
  $1,500.00 total value, 100% cash · 0 equity positions · 0 option positions ·
  0 realized trades in the trailing 90 days

---

## 0. The stated goal, answered directly

The request was a strategy to double the account daily. That target cannot be
built, and it is worth being precise about why rather than waving at "risk."

**The arithmetic.** 100%/day compounded over 252 trading sessions is
2^252 ≈ 7.2 × 10^75. Total world financial assets are on the order of
10^15 dollars. Starting from $1,500, a daily-doubling process consumes every
dollar on Earth in roughly 60 sessions — about twelve weeks. A method with that
property cannot exist, because the market it trades against is finite and it
would eat that market before the quarter ended. Its absence is not a gap in
anyone's skill or effort.

**The scale you actually want is much closer than it sounds.**
$1,500 → $1,000,000 is only 10 doublings. $1,500 → all world assets is ~40.
The gap between "life-changing" and "physically impossible" is 30 doublings,
and a daily-doubling process crosses it in six weeks.

**This account is additionally blocked by rule.** Equity is $1,500, far under
$25,000, so FINRA's pattern day trader rule caps this account at **3 day trades
per rolling 5 business days**. A daily-doubling scheme requires at minimum ~5
day trades per week. Robinhood will block the attempt before the math gets a
chance to. This is not a constraint that can be optimized around; it is
broker-enforced.

**What "chasing it anyway" actually pays.** The nearest real instrument that
occasionally returns +100% in a day is a full-size at-the-money 0DTE option.
Those do print. The distribution is the problem: a large fraction of such
positions expire at or near zero. Betting the full account sequentially with a
per-trial total-loss probability anywhere near 1/3 produces P(ruin) > 99% inside
three weeks. Section 7 simulates this explicitly, with the simulation deliberately
rigged in that approach's favor (it ignores the PDT rule that would make it
illegal). It still goes to zero in essentially every path.

**The real doubling timelines.** 15%/yr doubles the account in ~5.0 years.
30%/yr — genuinely elite, better than nearly every professional fund over a
decade — doubles it in ~2.6 years. 50%/yr, which almost nobody sustains,
doubles it in ~1.7 years. Those are the honest numbers, and RATCHET is built to
give this account a real shot at the aggressive end of that range while making
the catastrophic outcome structurally unavailable.

---

## 1. The four constraints this account actually has

Everything downstream is derived from these. They were read from the live
account, not assumed.

**C1 — Pattern day trader cap.** Equity $1,500 < $25,000. Maximum 3 day trades
per rolling 5 business days. Exceeding it freezes the account to
closing-only for 90 days. *Consequence: intraday trading is not a strategy
this account can run. Every position must be built to survive overnight.*

**C2 — No leverage.** Buying power is $1,500 against unleveraged buying power of
$1,500 — they are equal. "Limited margin" on this account means proceeds settle
instantly, **not** that money can be borrowed. There is no 2x. *Consequence:
any return has to come from the assets, not from the balance sheet.*

**C3 — Options level 3.** Long calls and puts and defined-risk spreads are
available. Naked short options and portfolio margin are not. *Consequence:
defined-risk structures are the only options this account can use, which is
fortunate, because they are also the only ones it should use.*

**C4 — Friction dominance.** This is the constraint nobody names and the one
that actually decides the outcome. At $1,500, the bid/ask spread on a typical
two-leg option position is 5–15% of the debit paid. A round trip therefore costs
10–30% of what was risked, *before the market has done anything at all*. On a
$100,000 account this is a rounding error. Here it is the largest single term in
the P&L equation. *Consequence: the correct response to a small account is
**fewer, longer-held, higher-conviction positions** — the exact opposite of the
high-frequency behavior that the doubling goal implies. Trading more often at
this size is mathematically self-harm.*

---

## 2. Architecture — two sleeves and a ratchet

```
                    TOTAL EQUITY  ($1,500)
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
   CORE SLEEVE  70% ($1,050)            CONVEXITY SLEEVE  30% ($450)
   Broad index ETF shares               Defined-risk option spreads
   Bought and held                      Max 3 concurrent positions
   Compounds quietly                    The ONLY capital that can zero
        │                                       │
        │         ◄── sweep profits ───────────┘
        │              (every Friday)
        └───────── capped refill ──────────►
                   (max 2% of equity/week)
```

**Core sleeve — 70%, target $1,050.** Broad-index ETF shares, fractional
permitted. Bought once, held. This is the compounding base and the reason a bad
year is survivable. It is **never** liquidated to fund a trade idea, to average
down, or to make back a loss. Its only outflow is the capped weekly refill in
§3, and its only inflow is the ratchet sweep and deposits.

**Convexity sleeve — 30%, target $450.** Defined-risk option structures only.
This is the aggressive engine, and it is also a firebreak: it is the only money
in the account capable of going to zero, and it is capped at 30% by charter.
If every convexity idea in a year is wrong, the account loses ~30%, not 100%.

---

## 3. The Ratchet — the mechanism the strategy is named for

This is the original core of the design and the part that does the real work.

Let `S` = current Convexity sleeve equity, `S0` = the sleeve's charter size
(initially $450), `E` = total account equity, `E_hwm` = all-time high-water
equity.

**Every Friday at 15:45 ET, the ratchet clicks:**

| Condition | Action |
|---|---|
| `S > S0` | Sweep `S − S0` into Core. Convexity resets to exactly `S0`. |
| `S < S0` | Refill from Core by `min(S0 − S, 0.02 × E, annual budget remaining)`. |
| `S = S0` | Nothing. |

**The refill also has an annual budget.** Total refills from Core are capped at
**20% of year-start equity per calendar year** ($300 in year one). Without this
cap, a 2%/week refill running for 52 weeks could drain the entire Core sleeve
over one bad year — the weekly cap alone limits the *rate* of bleed but not its
*total*. The annual budget is what actually makes the Core sleeve safe.

**And `S0` itself moves only one way.** Monthly, recompute
`S0 = 0.30 × E_hwm`. `S0` may increase. **`S0` may never decrease.** It ratchets.

### Why this is the whole strategy

Every account that dies, dies the same way: **bet size becomes a function of
recent P&L.** After wins, conviction rises and size rises — so the inevitable
loss arrives at maximum exposure. After losses, the urge to make it back rises
and size rises — so the second loss arrives at maximum exposure. Both failure
modes are the same bug: *the recent past is allowed to set the bet.*

The ratchet severs that link completely.

- **Winning cannot increase your risk.** Profits are swept out of the risk
  sleeve and into the buy-and-hold base every single week. You cannot let a hot
  streak scale you up, because the hot streak's proceeds are physically no
  longer in the account that trades.
- **Losing cannot increase your risk either.** The refill is capped at 2% of
  equity per week. After a bad week you are *smaller*, and you can only get back
  to charter size slowly, over weeks. Revenge-sizing is not available.
- **The bet only grows when banked equity grows.** `S0` tracks the high-water
  mark of *total* equity, recomputed monthly, never revised down. Size follows
  realized, retained wealth — never unrealized P&L, never conviction, never a
  narrative about the next trade.

The result is a system where good outcomes are permanent (swept into Core) and
bad outcomes are capped and slow to reload. It clicks up; it does not click back.

---

## 4. Day-trade rationing — treating C1 as a budget, not a limit

Three day trades per rolling five business days is not an annoyance to be worked
around. It is a **scarce, non-renewable resource**, and RATCHET spends it like
one.

**The rule: day trades are insurance, never income.**

- A day trade may **only** be spent on an **exit**. Never an entry.
- Permitted exit reasons, exhaustively: (a) a same-session stop breach on a
  position opened that session; (b) a gap or news event that invalidates the
  thesis outright; (c) cleanup of an unplanned assignment or expiration pin risk.
- **Budget floor: at least 1 day trade must remain available at all times.**
  When 2 of 3 are consumed, the system enters **LOCKDOWN**: no new Convexity
  entries until the rolling 5-day window releases one. Core is unaffected.

This rule is what forces the rest of the design to be sound. Because a day trade
may not be used to rescue a position, **every position must be constructed to
survive an adverse overnight gap without intervention.** That single requirement
is what rules out 0DTE, rules out weeklies, rules out full-size single positions,
and forces defined-risk structures with pre-placed GTC exits. The PDT rule,
treated properly, is not a handicap — it is the thing that enforces discipline
this account would otherwise have to supply from willpower.

---

## 5. Signal engine — two setups, and only two

More setups means more trades means more friction (C4). Two is deliberate.

### Setup A — Compression Break (CB) · primary

**Thesis.** Volatility mean-reverts and clusters: quiet periods resolve into
loud ones. The setup buys optionality specifically when it is cheap *relative to
the size of the move that is statistically due*. The edge, if it exists, is in
that relative mispricing — not in predicting direction. Direction is not
predicted at all; it is read off the break.

**Entry — all five must hold:**
1. 10-session realized volatility is in the **bottom 25%** of its own trailing
   1-year distribution.
2. 20-day Bollinger Band width is in the **bottom 20%** of its 1-year range
   (a genuine squeeze, not just a quiet week).
3. **IV rank ≤ 30** on the 30–45 DTE at-the-money option. You are not paying up
   for the move you expect.
4. Price is within 2% of the 20-day midline — no directional pre-commitment.
5. **Trigger:** the first daily *close* outside the 20-day band. Direction is
   taken from that close. Intraday pokes do not count — closes only, which also
   means entries are never rushed and never require a day trade.

Conditions 1–2 say a move is coming. Condition 3 says the option is cheap.
Condition 5 says the market, not the forecast, picks the side. The combination
is the setup: *pay a low price for a large expected move whose direction you
refuse to guess.*

**Structure.** Debit vertical spread, **30–45 DTE**, long leg ≈ **30 delta**,
short leg one strike width further out.

*Why a vertical rather than a plain long call?* At $1,500 this is not a
preference, it is arithmetic. The short leg cuts the debit by roughly 35–45%.
That is the difference between the sleeve holding one position and holding
three — which is the difference between the sleeve's outcome being one coin flip
and being a distribution. It also caps theta bleed, which matters enormously
when you cannot day trade your way out of a slow decay.

*Why 30–45 DTE?* Short enough that the compression thesis is still live; long
enough that a single bad day cannot end the trade, which is mandatory under §4.

**Exits — all placed as GTC orders at entry, before walking away:**
- **Target:** **+100% of the debit paid** (double your money on the spread).
  For a 30-delta vertical the debit runs ~40% of the width, so max profit is
  ~1.5x the debit and this target is ~⅔ of the maximum — reachable without
  needing the underlying to pin the short strike.
- **Stop:** **−50% of the debit paid.**
- **Time:** close at 10 DTE regardless of P&L. Gamma risk past that point is not
  compensated, and it is exactly where an account without day trades gets hurt.

This is a clean **2:1 payoff**, which is what makes the break-even hit rate in
§7 low enough to be plausibly achievable. Stating the target in units of *debit*
rather than "% of max profit" matters: the two are not the same number, and
mixing them silently corrupts every expectancy calculation downstream.

Because these are resting GTC orders, no exit consumes a day trade unless the
position was opened the same session — which is why the target is placed
immediately rather than "watched."

### Setup B — Post-Earnings Drift (PED) · diversifier

**Thesis.** A stock that gaps on earnings and then *holds* the gap tends to
continue drifting that direction for weeks — institutional repositioning takes
longer than one session. The setup is a diversifier because its return driver
(information diffusion) is uncorrelated with Setup A's (volatility mean
reversion).

**Entry — all four must hold:**
1. Earnings were released **1–3 sessions ago**. Never before.
2. Gap ≥ **4%** on ≥ **2x** average volume.
3. Price has held ≥ **60%** of the gap for **2 consecutive closes** — the gap is
   not fading.
4. Post-crush **IV rank ≤ 40**.

**Structure and exits: identical to Setup A.** One shared exit discipline across
the whole system, so there is never a judgment call about which rules apply.

**The hard rule that makes this setup work:** *never hold long premium into an
earnings announcement.* Buying options before a print is the single most
expensive habit available to a small options account — implied volatility is at
its annual peak, and the post-announcement IV collapse routinely loses money on
positions that **correctly predicted the direction**. PED is deliberately
constructed to be the mirror image: it enters *after* the crush, buying the
now-cheap option to capture the drift the crush left behind.

---

## 6. Rails — the numbers that are not negotiable

### Universe and liquidity filters

At $1,500 these matter more than the signals do. A perfect signal on an illiquid
chain loses money to the spread.

| Filter | Threshold | Why |
|---|---|---|
| Open interest at chosen strikes | ≥ 1,000 | You must be able to get out |
| Bid/ask on the **spread** | ≤ 10% of mid | Direct C4 defense |
| Underlying average daily volume | ≥ 5M shares | Liquidity begets liquidity |
| Strike grid | the **liquid** grid for that chain ($5 on SPY) | See below |
| Days to expiration at entry | 30–45 | §4 survivability |

> ### ⚠ Corrected in v1.1 — this rule previously said the opposite
>
> Earlier versions of this section required an underlying priced $10–$120 "or a
> $1-strike index ETF," justified by the claim that *"a chain that only offers
> $5-wide strikes forces a maximum risk of $500 per spread."*
>
> **That justification was wrong.** $500 is the max loss on a *credit* vertical.
> RATCHET trades **debit** verticals, where **max loss is the debit paid** and
> the width only sets max profit. A $5-wide SPY spread at 30 delta costs about
> $145 — inside the $150 cap.
>
> Worse, the rule steered toward $1-increment strikes, which on SPY are the
> *illiquid* ones: the $5-grid strikes carry 6–12x the open interest and
> one-cent bid/ask spreads, against nine to ten cents on the $1 grid. Trading
> the $1 grid raises round-trip friction from ~1.4% of debit to ~21%, which
> moves the **break-even hit rate from 34.3% to 47.5%**.
>
> See `SPY-MODULE.md` §1 for the live quotes demonstrating this.

**The corrected rule: select strikes on the chain's liquid grid, then choose the
width so the debit lands just under the $150 per-position cap.** Width is free —
it does not set your risk — so spend that freedom on liquidity. At this account
size, thirteen points of break-even hit rate turn on this single choice, which
is more than the entry filters in §5 could plausibly contribute.

**Starting whitelist** — prices verified live at design time (2026-09-02):

| Symbol | Price | Role |
|---|---|---|
| SPY | $765.15 | Index, $1-wide strikes available |
| QQQ | $708.62 | Index, $1-wide strikes available |
| IWM | $294.08 | Index, $1-wide strikes available |
| HYG | $79.15 | Credit / risk-off tell |
| EEM | $67.09 | Non-US diversifier |
| SLV | $58.94 | Commodity, low correlation to equity |
| XLF | $57.72 | Sector |
| SOFI | $17.90 | Single name, cheap options |
| F | $14.17 | Single name, cheap options |

GLD ($402.16) is watchlist-only and permitted solely via $1-wide strikes.

**Excluded permanently:** 0DTE. Any expiration under 21 DTE at entry. Stocks
under $5. Single-name biotech (binary FDA risk is not a tradeable distribution
at this size). Anything failing the liquidity table above.

### Risk limits

| Rail | Value | Rationale |
|---|---|---|
| Max risk per position | **$150** | 10% of account, 33% of sleeve |
| Max concurrent Convexity positions | **3** | Forces diversification of the sleeve |
| Max total Convexity capital at risk | **$450** | The sleeve charter; hard ceiling |
| Max new positions per week | **2** | C4 — friction control, the binding one |
| Daily loss limit (Convexity) | **$150** | Stop opening for the day |
| Weekly loss limit (Convexity) | **$225** | Stop opening for the week |
| Drawdown circuit breaker | **−15% from equity high-water** | Convexity halts 30 days; Core untouched |
| Correlation cap | Max 2 same-direction positions on correlated names | SPY/QQQ/IWM count as **one** underlying |
| Day-trade floor | **≥ 1 available at all times** | §4 LOCKDOWN trigger |

---

## 7. What this actually returns — the honest math

### Break-even hit rate

The exits are +100% of debit / −50% of debit — a 2:1 payoff. Round-trip friction
runs ~10% of the debit (C4). Expectancy per trade, as a fraction of debit:

```
E = p(1.00) − (1−p)(0.50) − 0.10
```

Setting `E = 0` gives **p = 40.0%**. That is the number to remember:

> **RATCHET must win 40% of its trades just to break even. Everything in §5
> and §6 exists to buy the percentage points above that line, and nothing
> guarantees they do.**

| Hit rate | Gross expectancy (× debit) | Net of friction | On a $110 debit |
|---|---|---|---|
| 35% | +0.025 | **−0.075** | **−$8.25** |
| 40% | +0.100 | **0.000** | **$0.00** |
| 45% | +0.175 | **+0.075** | **+$8.25** |
| 50% | +0.250 | **+0.150** | **+$16.50** |
| 55% | +0.325 | **+0.225** | **+$24.75** |

The 2:1 payoff is what makes 40% a plausible bar rather than a fantasy — a
filtered breakout setup that is right slightly less than half the time still
makes money. A 1:1 payoff would require winning 60%, which is not realistic.

### Simulated outcomes

`sim/ratchet_sim.py` — 20,000 paths × 252 sessions from the actual $1,500:

| Strategy | median | mean | 5th pct | 95th pct | P(ruin) | P(profit) | P(2x in yr) | P(−50%) |
|---|---|---|---|---|---|---|---|---|
| RATCHET @ 35% hit | $1,302 | $1,389 | $1,027 | $2,028 | **0.0%** | 26.9% | 0.2% | **0.0%** |
| RATCHET @ 40% hit | $1,388 | $1,510 | $1,049 | $2,368 | **0.0%** | 39.0% | 0.8% | **0.0%** |
| RATCHET @ 45% hit | $1,522 | $1,671 | $1,077 | $2,738 | **0.0%** | 51.9% | 2.4% | **0.0%** |
| RATCHET @ 50% hit | $1,747 | $1,886 | $1,108 | $3,122 | **0.0%** | 64.8% | 6.7% | **0.0%** |
| RATCHET @ 55% hit | $2,069 | $2,161 | $1,151 | $3,539 | **0.0%** | 75.8% | 15.4% | **0.0%** |
| "2x daily", held to expiry | $0 | $0 | $0 | $0 | **100.0%** | 0.0% | 0.0% | 100.0% |
| "2x daily", **with stop-losses** | $37 | $37 | $26 | $47 | **100.0%** | 0.0% | 0.0% | 100.0% |

**Three things in that table are worth sitting with.**

**1. Even at the break-even hit rate, the median path loses money.** At 40% the
*mean* is $1,510 — the sleeve is genuinely EV-neutral, exactly as the formula
says. But the *median* is $1,388. The gap is skew: a few large winners pull the
average up while the typical path drifts down. Break-even in expectation is not
break-even in experience. You need to clear 40% by a real margin, not scrape it.

**2. P(ruin) is 0.0% in every RATCHET row, and P(−50%) is 0.0% too — including
at a 35% hit rate where the strategy is genuinely losing.** That is not luck.
It is the ratchet, the 30% sleeve cap, and the annual refill budget doing
precisely the job they were designed for. The worst 5th-percentile outcome
across every scenario is about $1,027 — down 32%. **A bad year is a bad year,
not a wipeout.** That property is the actual product being delivered here.

**3. The disciplined doubler is the important row.** The second "2x daily" line
uses proper stop-losses, never lets anything expire worthless, and has a roughly
**flat arithmetic edge (+0.5% per trade)** — and it still goes to zero in
**100% of paths**, median 13 sessions. Its *geometric* edge is **−21.3% per
trade**. That gap between a fine average trade and a catastrophic compounded
outcome is **volatility drag**, and it is entirely a function of bet *size*, not
of skill, discipline, or signal quality.

> **This is the single most important result in the document.** You cannot fix a
> full-size daily bet by being better at picking. Stop-losses do not save it.
> Discipline does not save it. Only sizing saves it — which is why RATCHET's
> risk sleeve is capped at 30%, swept weekly, and refilled on a budget.

The simulation is deliberately **generous** to the doubling approach: it ignores
the PDT rule (which would halt it after 3 day trades) and assumes a better
per-trade edge than most short-dated option buyers achieve. It goes to zero
anyway.

### Realistic expectation, stated plainly

With ~40 closed trades a year (3 concurrent slots × ~3.5-week holds — the
2-per-week cap rarely binds), at a **45% hit rate**, the convexity sleeve
contributes roughly **+$250/yr** swept into Core, against Core's own ~8%
(~+$85). That is **≈ +22%/yr**, and it doubles the account in about **3.5
years**.

That is the honest pitch: a genuinely aggressive target, a real chance of
beating the market, a bounded worst case — and nothing remotely like doubling
daily.

**Every figure above is derived from assumed hit rates, not from backtests.**
No historical validation of the CB or PED filters was performed for this
document. The simulation shows the *shape* of each approach's distribution,
which is what the decision actually turns on. It is not a forecast.

## 8. The lever that actually matters

The honest ranking of what moves this account:

1. **Deposits.** $1,500 growing at an excellent 25%/yr earns **+$375/yr**.
   Contributing $200/month adds **+$2,400/yr** — more than six times the impact
   of the entire strategy. At $1,500, the strategy's real job is to not lose the
   deposits while they accumulate.
2. **Crossing $25,000.** That threshold removes the PDT cap and unlocks a
   genuinely different and better strategy space. It is a *deposit* problem, not
   a trading problem. No amount of cleverness at $1,500 gets there quickly.
3. **The strategy itself.** Third. Meaningfully third.

Any plan that inverts this ranking — that treats trading skill as the primary
lever on a $1,500 account — is selling something.

---

## 9. Operating cadence for the agent

| When | Action |
|---|---|
| Daily 09:45 ET | Scan whitelist against CB and PED filters. **Never trade the open** — the first 15 minutes have the widest spreads of the day (C4). |
| On signal | Verify every rail in §6, then enter. Max 2 entries/week. Skip entirely if LOCKDOWN is active. |
| Immediately after entry | Place target and stop as **GTC orders**. Non-negotiable — this is what keeps exits off the day-trade budget. |
| Daily 15:50 ET | Check day-trade budget. If ≤ 1 remaining, set LOCKDOWN. |
| **Friday 15:45 ET** | **Ratchet click.** Compute sweep or refill per §3. Log it. |
| Monthly, 1st session | Recompute `S0 = 0.30 × E_hwm` (never downward). Rebalance Core to 70%. |
| Continuous | If equity < 85% of high-water, halt Convexity for 30 days. Core untouched. |

### Pre-trade checklist — every box, every order

- [ ] Setup A or Setup B conditions **fully** met (no partial credit)
- [ ] Underlying passes all liquidity filters in §6
- [ ] Spread bid/ask ≤ 10% of mid **right now**, not on average
- [ ] Max loss ≤ $150
- [ ] Position count after entry ≤ 3
- [ ] Total sleeve risk after entry ≤ $450
- [ ] Correlation cap not breached (SPY/QQQ/IWM = one underlying)
- [ ] Entries this week ≤ 2
- [ ] Not in LOCKDOWN; ≥ 2 day trades available
- [ ] Not in drawdown halt
- [ ] **No earnings before this position's exit date** (Setup A only)
- [ ] 30–45 DTE
- [ ] GTC target and stop ready to place immediately on fill

Any unchecked box is a no-trade. Not a smaller trade — a no-trade.

---

## 10. What would falsify this

A strategy that cannot be wrong is not a strategy. RATCHET should be abandoned
or rebuilt if, after **at least 60 closed Convexity trades**:

- **Hit rate is below 40%.** That is the break-even line computed in §7, and
  below it the convexity sleeve is a slow donation to market makers. Note the
  stronger bar implied by the simulation: at exactly 40% the *median* path still
  loses money, so a rate that merely touches 40% is already failing in practice.
  Treat sustained results under **43%** as a failure even though the formula
  says break-even is 40%.
- Realized average friction exceeds **8% of debit** per round trip. The
  liquidity filters would then be failing at their only job.
- The Convexity sleeve underperforms simply holding the Core allocation, on a
  risk-adjusted basis, across a full year.

If any of these is true, the correct action is to **stop trading the Convexity
sleeve and hold Core**, not to adjust parameters until the backtest looks better.
Sixty trades is not enough data to justify fitting; it is only enough to detect
a strategy that clearly is not working.

---

## 11. Disclaimers

This is not financial advice. It is a specification document written at the
account holder's request. No trades have been placed. Options trading involves
substantial risk including total loss of the amount at risk, and defined-risk
structures limit the loss per position but do not prevent losing the entire
Convexity sleeve. All expectancy figures in §7 are **illustrative calculations
from assumed hit rates, not backtested results** — no historical validation of
the CB or PED filters was performed for this document. The account holder is
responsible for all trading decisions.
