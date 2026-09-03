# RATCHET decision log

Every decision, **including every decision not to trade.** A journal that
records only the trades taken hides the signals that were skipped, and a
skipped signal is the cheapest possible lesson — it costs nothing and still
tells you whether the filters are behaving.

Newest entries at the top. Prices are as-of their timestamp.

---

## 2026-09-02 — Daily scan automation: rolling window, NOT a cron routine

**Do not "fix" this by converting it to a recurring cron routine. That was tried
and it silently does not work.**

A recurring routine was created (`45 19 * * 1-5`, weekdays 15:45 ET) and the
API returned:

> *this trigger stores no MCP connectors, so the sessions it fires will run
> without connector (`mcp__<server>__*`) tools*

A scan session without connector tools cannot reach Robinhood. It would have
woken every weekday, found no market data, and done nothing — while appearing
in the trigger list as healthy coverage. **An automation that fails silently is
worse than none, because it removes the prompt to check.** The routine was
deleted.

**Working mechanism: a self-maintaining rolling window.** Each scan, as its
first step, calls `list_triggers` and ensures a scan exists for each of the next
**5 trading days**, creating any that are missing via `send_later`. These fire
into the existing session and carry its tools.

Properties worth keeping:
- **Idempotent** — it checks before creating. Duplicate scans on one day could
  double-enter a position, so the check is not optional.
- **Self-healing** — a 5-day buffer means several consecutive runs can fail
  before coverage lapses, and any single successful run restores the full
  window.
- **Holiday-aware** — the prompt requires verifying the market was open and
  skipping holidays. Labor Day (Mon Sep 7 2026) is named explicitly.
- **DST-aware** — 15:45 ET is 19:45 UTC under EDT and 20:45 UTC under EST. The
  prompt carries both; the switch is in November.

Schedule maintenance is embedded in the Thursday (`trig_0177cLpLKQnnBGNStzK5uDdi`)
and Tuesday (`trig_016rp6J5k7on7Q7dNuNL3z1d`) prompts, and propagates because
each created scan reuses the same prompt text.

---

## 2026-09-02 — Convexity universe expanded; scan schedule set

**Added to the Convexity sleeve:** NVDA (primary high-beta) and PLTR
(secondary), alongside SPY. TSLA and MSTR analysed and left on the watchlist —
TSLA for book depth (ask size 2 behind a 4,962 OI headline), MSTR for friction
(22.7% crossing cost, 63.6% break-even hit rate).

**The governing finding** (`HIGH-BETA-MODULE.md`): delta-matched 30-delta
verticals showed 21–22% probability of profit across IV from 10.7% (SPY) to
71.4% (MSTR). Higher volatility does not improve win odds — it is already in
the premium. What improves is reward:risk (NVDA 3.08:1 vs SPY 2.45:1) and the
target as a share of max profit (32.5% vs 40.8%). Same odds, bigger swings
both ways. Recorded here so nobody later mistakes this for an edge.

**Cadence corrected.** Both setups trigger on a *close*, so the single 09:45
scan in v1.0 could never have evaluated a trigger. Split into an ARM pass at
09:45 (conditions and levels only, never enters) and a TRIGGER pass at 15:45
(reads the close, enters if rails pass).

**Scans scheduled:**

| Session | Trigger | Notes |
|---|---|---|
| Thu Sep 3, 15:45 ET | `trig_0177cLpLKQnnBGNStzK5uDdi` | CB only; TPB blocked by NFP proximity |
| Fri Sep 4, 15:45 ET | `trig_01BYy45Q7s3M9qJaqzizWa74` | NFP day — CB plausible, but elevated IV should self-disqualify it |
| Tue Sep 8, 15:45 ET | `trig_016rp6J5k7on7Q7dNuNL3z1d` | First fully clean session; all setups live |

Mon Sep 7 is Labor Day — market closed.

**Gap this closes:** the Compression Break was armed on Sep 2 with nothing
scheduled to read Thursday's or Friday's close. An armed signal with no
observer is not a strategy.

---

## 2026-09-03 — Close scan: NO TRADE. One genuine band break DECLINED.

Near-close marks (15:47 ET). Bands are the Sep 2 values; today's bar had not
yet settled into the series.

| | Close | 20d upper | Width | Yest. vs midline | Verdict |
|---|---|---|---|---|---|
| SPY | $773.23 (+1.06%) | **$773.96** | **2.26%** | 0.02% | ARMED, missed by $0.73 |
| NVDA | $229.08 (+2.08%) | $227.61 | 9.60% | **3.33%** | **DECLINED** |
| PLTR | $183.07 (**+8.03%**) | $184.87 | 15.54% | — | no setup |

### NVDA broke its band and was declined anyway

This is the entry worth reading. NVDA closed at $229.08 against a 20-day
upper band of $227.61 — **a real break, unambiguously outside the band.**
It was not taken, because Compression Break is not a breakout setup. It is a
*compression* setup that happens to enter on a break, and NVDA failed both
compression preconditions:

- **Price within 2% of the midline before the break — FAILED.** NVDA closed
  Sep 2 at $224.41 against a $217.18 midline, already **3.33%** above it. The
  move was a continuation of an existing trend, not an expansion out of a
  coiled range.
- **BB width in the bottom 20% — FAILED.** Width was **9.60%**, roughly
  normal for a name carrying 32.5% IV. Nothing was compressed.

Buying optionality here would be paying for a move that had already started,
in a name that was never quiet. That is the opposite of the setup's thesis.

### PLTR +8.03% is not a signal

An 8% single-day move invites a trade. It qualifies for nothing:
- Inside its bands ($183.07 vs $184.87 upper) — no break at all.
- BB width 15.54% — not compressed.
- **Not post-earnings.** `get_earnings_calendar` over the trailing 7 days
  shows no PLTR report, so Setup B cannot apply. A large move is not evidence
  of a print, and the calendar was checked rather than assumed.

### SPY remains the live one

Closed **$0.73** below its trigger. Preconditions are excellent: BB width
2.26% (near the 1-year low), and Sep 2's close sat **0.02%** off the midline
— as clean a coil as the setup describes. It needs a close above roughly
$773.96, and today's large bar will widen the band and raise that threshold
for tomorrow.

**Trend Pullback: BLOCKED on all three names.** NFP prints tomorrow
(Fri Sep 4, 8:30 ET), one session out, inside the 2-session event filter.

**Day-trade budget: 3 of 3 available. No LOCKDOWN.**

---

## 2026-09-03 — Core sleeve entry: FILLED (38 minutes late)

**FILLED.** Order `6a997f6a-f245-47fb-bdf5-470ad15a7673`, `placed_agent: agentic`.

| | |
|---|---|
| Filled | **1.367545 SPY @ $767.799** |
| Amount | **$1,050.00** |
| Fees | $0.00 |
| Fill time | 2026-09-03 14:08:42.854 UTC (10:08:42 ET) |
| 09:30 opening print | **$767.88** |
| Fill vs open | **−$0.081/share, i.e. $0.11 BETTER** |
| Remaining cash | **$450.00** (the Convexity sleeve) |

### The order was late, and that is the entry that matters here

The trigger fired on time at 13:30:43 UTC, but this session's worker process
restarted mid-turn and the order was never submitted. The account sat at
$1,500 in cash with zero orders for 38 minutes while believing itself
invested.

**It was caught by the 14:00 UTC follow-up check-in** — the one scheduled
specifically to verify the fill rather than assume it, with an explicit
instruction that a missed order is a real failure and must not be re-armed
silently. That safety net is the only reason this was noticed within the
hour instead of at the 15:45 scan or later.

**The delay cost nothing, and that was luck, not skill.** SPY opened at
$767.88, ran to an intraday high of $770.04 at 13:52 UTC, then came back to
$767.7 by the time the order went in. Filling at $767.799 was 11 cents
better than the open. Had the session recovered twenty minutes earlier it
would have paid ~$770 — about **$3.06 worse** on this position size. The
outcome was a coin flip; the process failure was real regardless of which
way the coin landed.

### Lesson recorded

A fire-and-forget order trigger is not sufficient on its own. **Every
order-placing trigger needs a separate verification check-in behind it**,
scheduled after the order is due, whose job is to confirm the fill actually
exists rather than trust that the placing turn completed. That pattern is
already in place for this order and should be kept for every future one.

---

## 2026-09-03 — Core sleeve entry (as scheduled, superseded by the entry above)

**Scheduled:** 09:30 ET (market open) via `trig_01XARL14T3fZ1wm12z1aY6nZ`.
**Action:** BUY SPY, market, `dollar_amount` = 70% of equity (~$1,050), regular
hours, GFD.

**Cadence rule consciously overridden — logged so this is not mistaken later for
the rule being quietly ignored.**

§9 says scan at 09:45 and never trade the open. Originally scheduled for 09:45
on that basis. The account holder asked why, and the honest answer was that the
rule buys almost nothing *here*: it was written for option spreads, where an
opening spread of ten cents on a $145 debit is ~7% of capital at risk. SPY
**shares** quote a penny wide at 09:31 and a penny wide at 09:45 — on $1,050 the
difference is a few cents. They then directed the order be placed at the open,
and that is the correct call on the merits.

**The rule is not weakened for Convexity.** It binds in full on every option
entry, where it is worth real money. What changed is the recognition that a rule
written for two-leg option execution was being applied to a buy-and-hold share
purchase where its rationale does not carry.

**Why it could not happen on 2026-09-02 at all:** dollar-based fractional orders
require `type=market` **and** `market_hours=regular_hours`; the tool rejects them
in extended and overnight sessions. After the 16:00 close the only alternative
was a whole-share limit order in the overnight book — 1 share ≈ $764.50, which
is 51% of the account instead of 70%, at a wider spread. Wrong size, worse fill.

**Outcome:** filled 38 minutes late — see the entry above.

---

## 2026-09-02 — Trend Pullback SIGNAL FIRED, entry DECLINED

**The signal was valid. I did not take it.**

| Condition | Required | Actual | |
|---|---|---|---|
| Regime | close > 200-day SMA | 765.14 > 710.66 (+7.7%) | PASS |
| Washout | RSI(2) < 15 | Sep 1 close = 9.69 | PASS |
| Trigger | close > prior session high | 765.14 > 764.67 | PASS |
| Event filter | no FOMC/CPI/NFP within 2 sessions | **NFP Fri Sep 4, 8:30 ET** | **FAIL** |

**Reason for declining:** NFP lands 2 sessions out. Buying long premium into a
scheduled macro release means paying elevated IV and eating the post-release
crush — the exact failure mode Setup B′ was written to avoid. Three of four
conditions passing is not three-quarters of a signal; the event filter is a
gate, not a score.

**Also noted:** the trigger cleared by **$0.47**, and SPY traded back to $764.54
post-market, below the trigger level. Even without the event filter this was a
marginal entry. Worth watching whether "first close above prior high" needs a
minimum margin — but that is a change to consider **after** 60 logged trades,
not a parameter to tweak now on a sample of one.

**RSI(2) run-up:** 62.98 → 91.64 → 59.51 → 30.97 → **9.69**

---

## 2026-09-02 — Compression Break ARMED, not triggered

Bollinger width collapsed 6.27% → 2.21% over five sessions. Context across the
trailing year: April 2026 peak **16.1%**, prior tightest reading (Dec 2025)
**2.52%**. Current 2.21% is **below** that trough — at or near the one-year
minimum.

ATM IV **10.5–11.1%**, which is unusually cheap and exactly the condition the
setup wants: pay very little for optionality ahead of a statistically overdue
expansion.

**Trigger levels: daily CLOSE above $773.52 or below $756.58.** Sep 2 closed at
$765.14 — inside the bands. Not triggered. Bands must be recomputed daily.

**Watch item for Friday:** NFP is exactly the kind of catalyst that resolves a
squeeze this tight. But if the break comes *from* NFP, IV will have repriced and
the `IV rank ≤ 30` condition should fail on its own. That is the setup
protecting itself, not a reason to override it. **Do not take a post-NFP break
on expensive optionality.**

**Correlation caution:** Compression Break and Trend Pullback both reading PASS
on the same day are **not** two independent confirmations. Both are descriptions
of the same quiet, drifting tape. If they ever fire together, size as ONE
position.

---

## 2026-09-02 — Authorization granted

Account holder elected **"Full authority within the rails"** and **"Go live at
full size"** ($150/position) after being shown that:

- no backtest was run on either entry filter;
- the 5th-percentile simulated outcome is roughly −32%;
- the paper-trade and half-size alternatives were both available and were
  recommended over this.

Recorded here because the decision was informed and is the account holder's to
make. "Within the rails" is the binding half of that grant: every limit in
`RATCHET.md` §6 and every item on the §9 checklist still gates each order.
The NFP decline above is the first exercise of exactly that.

---

## Logging protocol

**Every fill** gets a row in `trades.csv`, including `debit_mid` and
`debit_filled` — the difference is realized slippage, and it is the earliest
available evidence that the expectancy model is wrong. The whole case for this
strategy rests on round-trip friction near 1.4% of debit rather than the ~21%
the illiquid strike grid would cost. That assumption is testable from the very
first fill, long before any hit-rate conclusion is possible.

**Every declined signal** gets an entry here, with the failing condition named.

Run `python3 stats.py` after each close.

**Do not tune parameters before 60 closed trades.** The confidence interval on a
small sample spans dozens of points; anything "learned" from it is noise, and
retuning on it is curve fitting with real money.
