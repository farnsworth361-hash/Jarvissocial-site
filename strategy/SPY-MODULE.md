# RATCHET — SPY Module

**Adaptation of RATCHET v1.0 for trading SPY exclusively, in account ••••8464.**

All prices and indicator readings below were pulled live on **2026-09-02
~15:56 ET** with SPY at **$765.07** (+$3.29, +0.43%). They are a snapshot for
calibration, not standing recommendations — re-pull before acting.

**No orders have been placed.**

---

## 1. Two corrections to the base spec

Trading SPY specifically surfaced two errors in `RATCHET.md`. Both are fixed
here and in the base document. The second one would have cost real money.

### Correction 1 — max loss on a debit vertical is the debit, not the width

`RATCHET.md` §6 originally justified its $10–$120 price band this way:

> *"A chain that only offers $5-wide strikes forces a maximum risk of $500 per
> spread — 33% of this entire account on a single position."*

**That is wrong.** $500 is the max loss on a *credit* (short) vertical. RATCHET
trades **debit** verticals, where **maximum loss is the debit paid** and the
width only sets maximum *profit*. A $5-wide SPY spread at 30 delta costs about
**$145**, so its max loss is $145 — comfortably inside the $150 per-position cap.

The width is therefore *free to choose*. It should be chosen to place the debit
near the risk cap, and — per Correction 2 — to land on the liquid strike grid.

### Correction 2 — the price band pointed at the *illiquid* strikes

The original rule preferred "$1-strike index ETFs." On SPY, the $1-increment
strikes are precisely the **bad** ones. Live quotes, SPY 2026-10-16 calls:

| Strike | Bid | Ask | Spread | Open Interest | Volume | Grid |
|---|---|---|---|---|---|---|
| 780 | 6.82 | 6.86 | $0.04 | 5,667 | 1,120 | $5 |
| 781 | 6.52 | 6.62 | $0.10 | 2,085 | 102 | $1 |
| 784 | 5.42 | 5.52 | $0.10 | 1,130 | 293 | $1 |
| **785** | 5.07 | 5.08 | **$0.01** | **13,255** | 2,295 | **$5** |
| 787 | 4.48 | 4.57 | $0.09 | 743 | 235 | $1 |
| 789 | 3.89 | 3.92 | $0.03 | 1,087 | 149 | $1 |
| **790** | 3.62 | 3.63 | **$0.01** | **13,074** | 1,788 | **$5** |

The $5-grid strikes carry **6–12x the open interest** and **one-cent** spreads.
The $1-grid strikes sit at nine to ten cents. The old rule steered directly into
the worse half of the chain.

**Corrected rule: on SPY, trade the $5 strike grid only. Choose the width so the
debit lands just under the $150 risk cap.**

### What this is worth

| | 785/790 ($5 grid) | 784/787 ($1 grid) |
|---|---|---|
| Debit at mid | $145.00 | $94.00 |
| Debit crossing the spread | $146.00 | $104.00 |
| Entry slippage | **$1.00 (0.7%)** | **$10.00 (10.6%)** |
| Max profit | $355.00 | $206.00 |
| Reward : risk | 2.45 : 1 | 2.19 : 1 |
| Combined OI | 26,329 | 1,873 |
| Round-trip friction | **1.4% of debit** | **21.3% of debit** |
| **Break-even hit rate** | **34.3%** | **47.5%** |

> **Thirteen percentage points of required hit rate, decided entirely by strike
> selection.** That is larger than any edge the entry filters in §5 could
> plausibly supply. At this account size, execution is not a detail that
> supports the strategy — it *is* the strategy.

---

## 2. Live state — where SPY actually is today

### Setup A (Compression Break): **ARMED, NOT TRIGGERED**

Bollinger Band width has collapsed over five sessions:

| Date | Lower | Middle | Upper | Width % |
|---|---|---|---|---|
| Aug 25 | 739.98 | 763.91 | 787.84 | 6.27% |
| Aug 26 | 746.52 | 764.12 | 781.72 | 4.61% |
| Aug 27 | 751.34 | 764.78 | 778.23 | 3.52% |
| Aug 28 | 755.88 | 765.22 | 774.56 | 2.44% |
| Aug 31 | 757.61 | 765.39 | 773.18 | **2.03%** |
| Sep 1 | 756.58 | 765.05 | 773.52 | **2.21%** |

For context across the trailing year: the April 2026 peak was **16.1%**, and the
tightest prior reading was the December 2025 trough at **2.52%**. Today's 2.21%
is *below* that trough — **at or near the one-year minimum**, comfortably inside
the "bottom 20%" requirement.

| Condition | Required | Actual | Status |
|---|---|---|---|
| BB width percentile | ≤ 20th | ~1st–3rd | **PASS** |
| ATM IV rank | ≤ 30 | IV = **10.5–11.1%** | **PASS** |
| Within 2% of midline | ≤ 2.0% | $765.07 vs $765.05 = **0.003%** | **PASS** |
| Close outside the band | trigger | not yet | **WAITING** |

**Trigger levels: a daily CLOSE above $773.52 or below $756.58.** Intraday pokes
do not count. Direction is taken from the close, not forecast.

### Setup B′ (Trend Pullback): **MAY TRIGGER AT TODAY'S CLOSE**

| Condition | Required | Actual | Status |
|---|---|---|---|
| Uptrend regime | close > 200-day SMA | 765.07 vs **710.66** (+7.7%) | **PASS** |
| Oversold | RSI(2) < 15 | Sep 1 = **9.69** | **PASS** |
| Trigger | first up-close | today +0.43%, unconfirmed | **PENDING CLOSE** |

RSI(2) ran 62.98 → 91.64 → 59.51 → 30.97 → **9.69** across the last five
sessions — a sharp washout inside an intact uptrend. Confirm at 15:45 ET.

---

## 3. Setup B′ — Trend Pullback, replacing PED

**SPY has no earnings, so Setup B (Post-Earnings Drift) cannot fire on it.**
Running SPY-only with one setup would leave the sleeve dependent on a single
return driver. Setup B′ replaces it.

**Thesis.** Inside an established uptrend, short-horizon selloffs in a broad
index overshoot, because the selling is mechanical — margin calls, stop
cascades, index-level de-risking — rather than informational. The rebound is the
market repricing away that forced flow. This is a *different* return driver from
Setup A (which monetizes volatility expansion), so the two diversify each other
even on one underlying.

**Entry — all four must hold:**
1. **Regime:** SPY closes above its 200-day SMA. Non-negotiable; this setup
   never fights a bear market, it simply does not fire.
2. **Washout:** RSI(2) closes below **15**.
3. **Trigger:** the first daily close above the prior session's high.
4. **Event filter:** not within 2 sessions of FOMC, CPI, or NFP. Check the
   calendar before entry — a scheduled macro event is a different distribution.

**Structure:** call debit vertical, $5 grid, 30–45 DTE, long leg ≈ 30 delta.
**Exits:** identical to Setup A — +100% of debit / −50% of debit / 10 DTE.
Direction is long only, by construction.

---

## 4. Concurrency — what SPY-only costs

Three SPY positions are not three bets. Simulated at a 45% hit rate, 20,000
paths, with concurrent outcomes correlated at ρ = 0.85 versus independent:

| Sleeve | median | mean | 5th pct | 95th pct | P(profit) | P(2x) |
|---|---|---|---|---|---|---|
| Diversified (ρ=0.00) | $1,533 | $1,677 | $1,079 | $2,759 | 52.5% | 2.7% |
| **SPY-only (ρ=0.85)** | **$1,469** | $1,752 | **$1,035** | **$3,365** | 48.1% | **8.4%** |

Correlation does not cost expected return — it **widens the distribution in both
directions**. The median and the 5th percentile get worse; the 95th percentile
and P(2x) get materially better. It is a genuine trade, not a disaster, and the
reason it stays a trade rather than a catastrophe is that the sleeve is capped at
30% of the account. Concentration inside a capped sleeve is survivable.
Concentration across the whole account is not.

**SPY-only concurrency rule:**
- Maximum **2 concurrent same-direction** positions.
- A 3rd position is permitted **only if it is the opposite direction**
  (e.g. a put vertical from a downside Compression Break against an existing
  call vertical).
- Same-direction positions must sit in **different expirations**.
- Everything else in `RATCHET.md` §6 is unchanged.

Also worth stating plainly: **Core is already SPY.** Running the Convexity
sleeve on SPY too means the entire account is one asset. That is acceptable for
a buy-and-hold Core, and it is the explicit choice being made here — but it
means there is no diversification anywhere in this account, and a sustained SPY
drawdown hits both sleeves at once.

---

## 5. Trade blueprint

**This is the shape of the trade, not an order to place now.** Setup A has not
triggered. If it triggers upward, strikes get re-selected at that moment — SPY
will have moved to ~$773.52+ and the 30-delta strike moves with it.

**Bullish (upside Compression Break, or Setup B′):**

```
BUY  1x SPY 2026-10-16 785 CALL     ask 5.08   delta 0.290   OI 13,255
SELL 1x SPY 2026-10-16 790 CALL     bid 3.62   delta 0.229   OI 13,074
------------------------------------------------------------------------
Net debit          $145 at mid  /  $146 crossing
Max loss           $145           (the debit — this is the risk number)
Max profit         $355           (width $500 − debit)
Reward : risk      2.45 : 1
Breakeven          SPY $786.45 at expiry
Profit target      +$145  →  sell to close at $2.90   (GTC, placed at fill)
Stop               −$73   →  sell to close at $0.73   (GTC, placed at fill)
Time exit          2026-10-06 (10 DTE) regardless of P&L
```

**Bearish (downside Compression Break):** the mirror — buy the ~30-delta put on
the $5 grid, sell the put $5 further out of the money, same DTE, same exits.
Price it live at trigger; I have not quoted the put chain here and will not
invent numbers for it.

**Sizing against the sleeve:** one contract = $145 of the $450 Convexity sleeve.
Two same-direction contracts = $290, leaving $160 of dry powder. That is the
intended maximum SPY exposure under §4.

---

## 6. Order execution — the rule that carries the strategy

Section 1 showed that strike choice moves the break-even hit rate by 13 points.
Order *type* moves it nearly as much.

1. **Never send a market order.** Not once, not on an exit, not in a hurry.
2. **Enter as a single two-leg spread order**, never as two separate legs. A
   legged entry exposes you to the market moving between fills, and on a $145
   debit that risk dwarfs the spread you were trying to save.
3. **Limit at the mid.** Compute mid from the live quotes on both legs.
4. **Walk the price at most $0.02**, in one-cent steps, roughly 30 seconds
   apart. On the 785/790 that is a 1.4% concession.
5. **If unfilled at mid + $0.02, cancel and stand down.** There is no signal so
   good that it is worth paying 10% of the debit to enter. Two entries a week
   maximum means skipping one costs you almost nothing.
6. **Place the GTC target and stop immediately on fill** — before doing anything
   else. This is what keeps exits off the day-trade budget.
7. **Never trade the first 15 minutes.** Scan at 09:45 ET. The open carries the
   widest spreads of the day, and this whole document is about not paying them.

---

## 7. What is actually live right now

- **Compression Break:** armed, not triggered. Watching for a daily close
  **above $773.52** or **below $756.58**. Whichever comes first sets direction.
- **Trend Pullback:** conditions 1 and 2 met; the trigger resolves at today's
  close. Confirm at 15:45 ET before acting.
- **IV at 10.5–11.1% is unusually cheap**, which is exactly the condition both
  setups want — you are being asked to pay very little for optionality ahead of
  a statistically overdue range expansion.
- **Nothing has been ordered.** The rails in `RATCHET.md` §6 and the checklist in
  §9 apply in full before any entry.

One caution on the coincidence: a compression this tight *and* a 9.69 RSI(2)
washout arriving together is not two independent confirmations. Both are
readings of the same quiet, drifting tape. Treat this as **one** setup with two
descriptions, size it as one position, and do not double up because two rows in
a table both say PASS.

---

## 8. Disclaimers

Not financial advice. Specification only; no orders placed. All prices are a
2026-09-02 snapshot and will be stale when read. The expectancy and simulation
figures are calculations from assumed hit rates, **not backtested results** —
no historical validation of Setup A or Setup B′ was performed. Options trading
risks total loss of the amount at risk.
