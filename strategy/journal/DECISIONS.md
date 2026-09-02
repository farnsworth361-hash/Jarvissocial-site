# RATCHET decision log

Every decision, **including every decision not to trade.** A journal that
records only the trades taken hides the signals that were skipped, and a
skipped signal is the cheapest possible lesson — it costs nothing and still
tells you whether the filters are behaving.

Newest entries at the top. Prices are as-of their timestamp.

---

## 2026-09-03 — Core sleeve entry (SCHEDULED)

**Scheduled:** 09:45 ET via `trig_01XARL14T3fZ1wm12z1aY6nZ`.
**Action:** BUY SPY, market, `dollar_amount` = 70% of equity (~$1,050), regular
hours, GFD.

Deliberately not placed at the 09:30 open. Fractional/notional orders on
Robinhood require `type=market` + regular hours, and an order queued after
Wednesday's close would have filled into the widest spreads of the day. For a
buy-and-hold Core position the cost is pennies, but the cadence rule exists and
there was no reason to break it.

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
