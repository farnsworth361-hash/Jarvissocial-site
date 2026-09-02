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

## 2026-09-03 — Core sleeve entry (SCHEDULED)

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

**Outcome:** _pending_

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
