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

## 2026-09-03 — STRATEGY CHANGE: rotate to all-options, Core sold

**Directed by the account holder**, after being shown the consequences:
1. "All options, sell the shares."
2. "Just buy a SPY spread now, next session" — skip the signal for this entry.

Scheduled for Fri 2026-09-04 09:45 ET (`trig_017voi57zqNQU5uhbF94ddcD`), with
a verification check-in at 10:20 ET behind it
(`trig_01MYDgzP4oiZM8XLX4WAuXXi`).

### What this does to the strategy

**The ratchet is now inoperative.** The weekly click sweeps Convexity profits
*into* Core. With no Core, there is nothing to sweep into and nothing to
refill from. The mechanism the strategy is named for — the thing that made
bet size track banked equity rather than recent P&L — stops running. What
survives is the entry rules and the position caps, not the compounding
structure.

**P(ruin) is no longer 0%.** Every simulation showing a zero ruin probability
depended on a 70% buy-and-hold sleeve that cannot go to zero. Removing it
moves the account toward the distribution modelled as "ALL-IN" in
`sim/three_month_target.py`, which is a materially different shape. The
position caps still bound each individual trade; they do not reproduce what
Core was doing.

This is recorded, not argued. The holder was shown the ruin figures, the
three-month distributions, and the sizing-beats-skill result before choosing,
and reaffirmed. It is their account and their call.

### What was deliberately NOT changed

**Per-position risk stays at $150, max 3 concurrent, max 2 entries/week.**
The holder asked to move *capital* into options. They did not ask to raise
the per-position cap, and raising it is a separate decision worth roughly 3x
the risk per trade. Leaving it at $150 means most of the ~$1,507 will sit in
cash until setups arise — which is the honest consequence of "more capital
available for options" without "bigger bets," and the holder has been told
the cap can be raised on request.

### Two things that happen to work in the holder's favour

- **NFP prints at 08:30 ET, one hour before the open.** A Friday-open entry
  is therefore POST-event: the number is already in the price and IV has
  already repriced. This is not buying into a catalyst.
- **Selling Friday is not a day trade.** The shares were bought Thursday
  2026-09-03, so the round trip spans two sessions. The 3-per-5 budget is
  untouched.

### Entry without a signal

This one entry bypasses the setup filters at the holder's explicit
direction. It should be logged in `trades.csv` like any other trade, but
flagged as signal-less in the notes column — otherwise it will contaminate
the §10 hit-rate statistics, which are meant to measure whether the *entry
filters* work. A trade taken without a filter says nothing about the filter.

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

## 2026-09-04 · Authority resolved and sizing raised to the cap — RATCHET v1.3

The holder, asked to break the tie between two of their own standing
instructions, chose **"fire within the rails"** and added **"place more on the
orders, like the max amount."**

**What was in conflict.** The RATCHET grant of 2026-09-02 said "full authority
within the rails." The SPY 0DTE framework of 2026-09-03 said "never place an
order I haven't approved." The 0DTE framework was withdrawn the same day it was
imposed, but that clause was never explicitly retired, so both readings survived
into 2026-09-04. It is now settled: **no per-order approval.** The fill is
reported after the fact.

**What changed in sizing.** The rulebook capped a position at $150 but said
nothing about contract count, which in practice meant one contract. It now takes
the largest whole number of contracts fitting under $150. On SPY this is usually
a no-op — a $5-wide 30-delta vertical is already ~$145 for one lot. It bites on
the cheaper single-name chains.

**What did not change, and was not asked to.** The $150 per-position cap, the
3-concurrent cap, the 2-entries-per-week cap, the $450 charter, the universe, and
every entry gate. "Within the rails" was the holder's own framing and is the
binding half of the instruction. Size is decided *after* a setup has passed every
gate — never to justify taking one.

**The bear case, recorded before the first fill rather than after.** Sizing to
the cap scales wins and losses by the same factor. It raises the sleeve's
expected dollar outcome and its variance together and improves the odds of
nothing. Two specific ways it can be worse than it looks:

1. **Fill quality degrades with size.** Displayed bid/ask size, not open
   interest, is the binding constraint. A 3-lot into a 1-up market can give back
   more in slippage than the extra two lots win. The checklist now requires size
   ≥ contract count on both legs.
2. **Full deployment is one correlated bet.** Three positions at $150 is the
   entire $450 sleeve, and SPY/NVDA/PLTR are long-beta throughout. The
   max-2-same-direction cap spanning SPY and NVDA is the only thing preventing
   that, and it matters more at full size than it did at partial size.

The realistic effect on the account: this raises the sleeve from a rarely-used
$450 to a fully-usable $450. It does not change the ~+22%/yr simulated
expectation of the strategy, and it does not change the break-even hit rate of
34.3%. The holder was told this when they gave the instruction and gave it
anyway; it is their call and it is inside the rails they set.

**No order was placed on this instruction.** It arrived at 00:17 ET with the
market closed and, more importantly, RATCHET setups fire on a **close**, never on
an instruction. The Friday 2026-09-04 15:45 ET scan is the first run operating
under v1.3. If no setup passes, the correct outcome is still no trade.

---

## 2026-09-04 · NO TRADE — first scan under v1.3, nothing passed

NFP day. First run with fire-within-the-rails authority and size-to-the-cap
active. Both were available and neither was used, because no setup fired.

**Prices at 15:45 ET:** SPY 769.94 (−0.42%), NVDA 230.12 (+0.73%),
PLTR 173.94 (−4.71%). Account $1,502.97 — Core 1.367545 SPY at $1,052.97,
cash $450, zero option positions, 3 of 3 day trades available.

**Bands, recomputed with today's price in the 20-day window:**

| | lower | mid | upper | 15:45 | outside? | vs mid |
|---|---|---|---|---|---|---|
| SPY | 760.40 | 769.04 | 777.68 | 769.94 | no | +0.12% |
| NVDA | 208.15 | 220.07 | 231.99 | 230.12 | no | +4.57% |
| PLTR | 166.85 | 176.90 | 186.95 | 173.94 | no | −1.67% |

**Failing conditions, per name:**

- **SPY — Compression Break: no band break.** 769.94 sits inside
  760.40–777.68, near the midline. It passes the 2%-from-midline proximity
  gate; it simply has not broken out.
- **NVDA — Compression Break: no band break on the governing band, and the
  midline-proximity gate fails.** Worth recording carefully, because the two
  readings disagree. Against the *prior* session's band (upper 229.30) NVDA at
  230.12 looks like an upside break. Against the band recomputed *including
  today's bar* — the correct test, since today's price enters the 20-day mean
  and standard deviation — the upper band is 231.99 and NVDA is inside it. The
  break is an artifact of testing a price against a band that does not contain
  it. Independently, the pre-break bar (Sep 3, 228.45) sat **+4.73%** above its
  midline of 218.14 against a **≤2%** gate, so the setup would have been
  declined either way. This is the same condition that disqualified NVDA on
  2026-09-03 — twice now, for the same reason: NVDA is extended, not compressed,
  and a break from an extended position is continuation, not a volatility
  expansion off a coiled base.
- **PLTR — Compression Break: no band break.** The −4.71% move is the largest
  of the day and looks like a candidate, but PLTR closed Sep 3 at 182.53,
  essentially *on* its upper band of 182.59. Today's fall took it from the top
  of the band toward the midline and stopped well short of the lower band at
  166.85. That is mean reversion inside the band, which is the opposite of the
  setup. Direction would also have been unreadable.
- **All names — Trend Pullback: BLOCKED.** NFP printed this morning, 0 sessions
  out, inside the 2-session event window.
- **NVDA, PLTR — Post-Earnings Drift: outside the window.** Verified against
  the earnings calendar rather than inferred from price: NVDA reported
  **2026-08-26 pm**, which is 6 sessions ago against a 1–3 session window. PLTR
  has no report in the trailing 14 days (its last was the Aug 3 print behind the
  Aug 4 +29% gap). PLTR's −4.71% today is a large move with no earnings behind
  it — exactly the trap the "verify the print, a big move is not evidence of
  one" rule exists to catch.

**Ratchet click (Friday):** sleeve at exactly $450 cash with no open positions.
Surplus zero, shortfall zero. **No-op.**

**Note on the new authority.** The first day of unattended order placement was a
no-trade day, which is the expected case, not a failure of the grant. Authority
removed the wait between a valid signal and an order; it did not create signals.
The temptation it introduces is visible in NVDA — a genuine-looking band break
that two separate gates reject. It was rejected.

**Correction to a level quoted earlier today:** an intermediate read in-session
described NVDA as breaking its upper band, based on the prior session's band.
The recomputed band is the governing one and puts it inside. The trade decision
is unchanged.

---

## 2026-09-08 · OUT-OF-FRAMEWORK · Core liquidated, INTC spread opened by the holder

**This is not a RATCHET trade and must never be counted as one.** Recorded here
because it emptied the framework.

**What happened, from the order records:**

| time (UTC) | event | placed_agent |
|---|---|---|
| 16:52:45 | SPY sold, market, 1.367545 sh @ $767.17 = $1,049.03 | **agentic** |
| 17:02:32 | INTC 105/110 call spread, 7 @ $1.71 debit — cancelled | user |
| 17:06:31 | INTC 105/110 call spread, 1 @ $1.81 filled ($181) | user |
| 17:10:14 | INTC 105/110 call spread, 6 @ $1.86 filled ($1,116) | user |
| 17:22:31 | GTC closing order, 7 @ $4.00 credit — still resting | user |

The holder confirmed on 2026-09-08 that they placed the INTC orders. The SPY
liquidation carries `placed_agent: agentic`, meaning it went through an agent
connection rather than the app — **it was not this session**, and no instruction
to sell Core was given here. Flagged to the holder; unresolved at time of
writing. Core-selling is on the v1.3 "requires an explicit instruction" list
precisely so this cannot happen quietly, and the control did not hold, because
the actor was not this session.

**The position:** INTC 105/110 call debit spread, 7 contracts, exp 2026-09-11.
Total debit **$1,297** ($1.853 avg). Max profit $2,203 at INTC ≥ $110; max loss
the full $1,297 at INTC ≤ $105; break-even $106.85. INTC closed $104.44 that day
after a +9.0% session — the position was opened at 1:06pm, near the highs, into a
move that had already happened.

**Every RATCHET rail this breaks:** underlying not in the universe (SPY, NVDA,
PLTR); $1,297 against a $150 per-position cap (8.6×); 3 DTE against a 30–45 DTE
rail; 86% of the account in one position against a $450 sleeve charter; and the
Core sleeve sold to fund it, which the charter forbids outright.

## 2026-09-08/09 · Holder's stop instruction, and how it had to be built

Instruction: **"If the account loses another $250, close the position."** Given
after being shown the position's odds (~32% of finishing above break-even, ~20%
above $110) and the fact that it is 86% of the account.

**Translated to a testable trigger.** Account was $1,265.49 = $201.49 cash +
$1,064 spread. Cash is static, so:

> **Close when the spread mark ≤ $1.16** — position ≤ $814, account ≤ $1,015.49.

**Why it is a monitored stop and not a resting one.** Robinhood does not accept
stop orders on multi-leg spreads — the API states plainly that only `limit` is
available with two or more legs, and stop_market/stop_limit are single-leg only.
There is therefore **no broker-side stop**. The instruction is implemented as
scheduled check-ins (13:35, 14:50, 16:05, 17:20, 18:35 and 19:45 UTC each
session) that read the mark and place a closing limit order on breach. Two
consequences the holder was told about: a gap through the level fills below it,
and the stop only exists while the check-ins keep firing.

The resting $4.00 GTC target is left in place, and is cancelled first at trigger
time — a second closing order on the same 7 contracts is rejected while it rests.

**What the stop is actually likely to do.** Spread theta is about −$0.0855 per
contract per day, ≈ **−$60/day** across 7. INTC at $104.44 is below both strikes,
so if it simply sits still the spread decays to zero by Friday and **must** pass
$1.16 on the way — most likely Thursday. So this is a theta stop far more than a
directional one: it will probably fire because the position ran out of time, not
because INTC moved against it. That is not an argument against it. Stopped at
$1.16 the loss is ~$485 and the account lands near $1,013; held to expiry below
$105 the loss is the full $1,297 and the account lands near $201. **The stop is
worth roughly $812 in the bad case**, which is the majority of what is left.

**Hard deadline.** Robinhood force-closes these contracts at **2026-09-11 15:30
ET** (`sellout_datetime` 19:30Z): if INTC settles between $105 and $110 the long
leg is ITM and exercising 7 contracts needs $73,500 against ~$201 of cash. A
14:45 ET Friday check-in is armed to surface this 45 minutes ahead, and the 15:45
ET run is a backstop for a stranded position.

**RATCHET is unfunded and dormant.** No Core sleeve, no $450 charter, ~$201 cash.
Every scheduled scan now carries an explicit instruction to open nothing, in any
name, until the holder refunds the account and says so. Nothing about the v1.3
fire-within-the-rails grant authorises an entry when there are no rails left to
be inside of.

---

## 2026-09-10 · INTC closed at a loss of $933 · and the stop mechanism was broken

**Result:** flat at 09:38 ET. Realized **−$933** on the $1,297 basis (−72%).
Account **$564.87**, all cash, from $1,502.97 the previous Friday.

| leg | action | fill | proceeds |
|---|---|---|---|
| 110 call ×7 | buy to close | $0.16 | −$112 |
| 105 call ×7 | sell to close | $0.68 | +$476 |
| | | **net** | **+$364** |

### The mechanism failure — the important part of this entry

The monitored stop built on 2026-09-08 **could not have executed as designed.**
At the trigger, `place_option_order` returned:

> `Multi-leg options orders aren't supported in Robinhood agentic accounts yet.`

What was verified when the stop was built: that Robinhood will not *rest* a stop
order on a spread (only `limit` is available with 2+ legs). What was **not**
verified: that a closing *limit* order on a spread would be accepted at all from
this account. It is not. The holder was told a stop was in place. It would have
failed at the only moment it mattered.

**The generalisable lesson, stated so it is not lost:** verifying that a
constraint exists is not the same as verifying the intended action works. The
exit path must be *executed* — or at minimum accepted by the broker in review —
before a position is described as protected. A review call would have caught this
on 2026-09-08 for the cost of one API round trip. `review_option_order` accepts
multi-leg previews, so even review would not have caught it; only an actual
`place_option_order` attempt surfaces the restriction. That makes it worse, not
better: the only reliable test is a live order, so any future exit plan on this
account must be single-leg by construction.

**Recovery, improvised at the trigger:** legged out with two single-leg orders,
short side first — buy back the 110s (leaving a long-only position, which needs
no collateral and carries no assignment risk), then sell the 105s. The reverse
order would have left 7 naked short calls against $201 of cash and would have
been rejected. Total elapsed from trigger detection to flat: about 3 minutes. The
105s filled at $0.68 against a $0.66 limit, +$14 of price improvement.

**Standing rule for this account: any options exit plan must be single-leg.**
Multi-leg orders cannot be placed here at all, opening or closing. That also means
this account cannot execute RATCHET's debit verticals as specified — see below.

### The gap — what the stop could and could not do

INTC closed 2026-09-09 at **$106.24** and opened 2026-09-10 at **$101.14**,
**−4.80%**. The account went from $1,468.49 at Wednesday's bell to $558.49 at
Thursday's open, straight through the $1,015.49 trigger without trading near it
during any monitored session.

Designed outcome of the stop: exit near $1.16, loss ≈ $485.
Actual: exit at $0.52 net, loss $933 — **roughly double**.

The holder was warned on 2026-09-08 that "a gap through the level fills below it,
not at it." That warning was correct and it is the case that occurred. It should
not be read as the stop being pointless: riding to expiry with INTC at $101 and
both strikes out of the money was the **full $1,297**, leaving $201 in the
account. The stop salvaged $364. It did roughly half the job it was described as
doing, and the half it missed was the half no monitored stop can cover.

Prediction accuracy, recorded for honesty: on 2026-09-09 09:36 ET this was called
as "likely to trigger Thursday on decay alone." It did trigger Thursday, but on a
4.8% overnight gap, not on decay. The timing was right for the wrong reason, and
that is not a successful forecast.

### RATCHET cannot run on this account as specified

The Convexity sleeve is defined as **debit verticals** — two-leg spreads. This
account cannot place them. Before RATCHET resumes, the sleeve has to be
redesigned around single-leg instruments, or moved to an account that accepts
multi-leg orders. Every simulation, break-even figure and friction estimate in
`RATCHET.md` §7 assumes verticals and does not transfer to single-leg longs,
whose break-even hit rate is far higher. **This is not a small amendment.**

Account state: $564.87, all cash, no positions, no Core sleeve. RATCHET remains
unfunded and now also **unimplementable as written**. No new entry is authorised.

Still unresolved: the 2026-09-08 SPY liquidation carrying `placed_agent: agentic`
that did not originate from this session.

---

## 2026-09-14 · Account refunded $2,000 — one of two blockers cleared

Account **$2,564.87**, all cash, no positions. A $2,000 deposit landed against the
$564.87 remaining after the INTC close. `pending_deposits` is zero, so it is
settled and spendable.

**Blocker 1 (unfunded) is cleared. Blocker 2 is not.** The Convexity sleeve is
specified as debit verticals and this account cannot place them —
`place_option_order` rejects two legs, opening or closing. Money does not fix
that. RATCHET stays dormant until the sleeve is either redesigned around
single-leg instruments or moved to an account that accepts multi-leg orders, and
that is the holder's decision to make, not one to improvise into.

**What the refund changes if the redesign happens.** At $2,564.87 the 70/30 split
would put Core at ~$1,795 and the Convexity charter at ~$770, against the $450 it
was. The per-position cap, being 33% of the sleeve, would scale to roughly $255.
None of that should be applied until the instrument question is settled — the
$150 cap and the 34.3% break-even both derive from vertical economics that no
longer hold here.

**PDT still binds.** $2,564.87 is far below the $25,000 threshold, so day trades
remain capped at 3 per rolling 5 business days. Nothing about the deposit
loosens that.

**Worth recording against the strategy's own history.** Deposits were identified
on 2026-09-03 as worth roughly six times the return lever at this account size,
and then argued for again on 2026-09-04 when the holder asked for the highest
possible rate of return. A $2,000 deposit moved the account further in one
transfer than any realistic trading outcome would have over months. That is the
lever working exactly as the arithmetic said it would, and it is the one part of
this account's history that went according to plan.

Still unresolved: the 2026-09-08 SPY liquidation carrying `placed_agent: agentic`
that did not originate from this session. Another agent connection has trade
authority on this account.

---

## 2026-09-21 · Account is fully in SPY — bought by an agent, not this session

Account **$2,605.76**: 3.358353 SPY worth $2,600.88, cash **$4.88**.

**The order:** $2,560 dollar-based market buy, filled Wed 2026-09-17 at 11:46 ET,
3.358353 sh @ $762.2782, `placed_agent: agentic`. **It did not originate from
this session.** SPY is $774.50 as of 2026-09-21 15:45 ET, so the position is
**+$40.88 (+1.60%)**.

**This is the second unannounced agentic trade on this account.** The first sold
the Core SPY sleeve on 2026-09-08; this one rebuilt it. The pattern is now
established rather than anomalous: a second agent connection holds trade
authority here and acts without this session's knowledge. Flagged on 09-08,
09-10 and 09-14 and still unaddressed. Recording it a fourth time because the
risk is structural, not hypothetical — two agents writing to one account, neither
aware of the other, is exactly how the Core sleeve got liquidated under a
framework whose first rule was never to sell Core.

**On the merits, this trade is fine.** Broad index, bought and held, no leverage,
no expiry. It is the Core sleeve concept executed at 100% rather than 70%, and it
is the opposite of the INTC episode in every respect that matters. Saying so
plainly: if the choice is between an agent that buys SPY and an agent that buys
7-lot 3-DTE spreads on an out-of-universe name, this is the good outcome. The
objection is to the coordination gap, not to the position.

**Where it leaves RATCHET.** The allocation is now ~99.8% Core and 0.2% cash
against a specified 70/30. But the Convexity sleeve remains unimplementable —
this account rejects multi-leg orders — so **100% Core is currently the only
executable form of the strategy.** That is not a failure state; it is the honest
consequence of the instrument constraint. With $4.88 of cash there is also no dry
powder, and funding a Convexity sleeve would require selling Core, which the
charter forbids outright.

Nothing to do. No position was opened or closed by this session. The instrument
decision — redesign single-leg, or move to an account that accepts verticals —
remains open and remains the holder's.

---

## 2026-10-12 · Found the control that would have caught the unexplained trades

Account state unchanged for a fourth week — $2,617.05, 3.358353 SPY worth
$2,612.17 (+$52.17, +2.04% on the $2,560 basis), cash $4.88, no orders. Nothing
about the position is worth logging.

**What is worth logging:** Robinhood exposes a per-account trade-approval
setting, and on ••••8464 it reads:

```
human_must_approve_trades: false   (set 2026-08-26T15:53:02Z)
```

This is the switch that makes every agent-placed order wait for the holder's
manual approval in the Robinhood app before it executes. **It is off, and it has
been off since before any of this account's history in this journal.** It is the
direct remedy for the thing flagged on 09-08, 09-10, 09-14 and 09-21 — two
agentic orders (SPY sold 09-08, SPY bought 09-17) that did not originate from
this session and that nobody here authorised. With the setting on, neither could
have filled without the holder tapping approve.

Two things to be precise about:

- **No tool here can change it.** Only the holder can, in the Robinhood app. The
  MCP surface is read-only on this setting by design, which is the correct
  design.
- **It is a real tradeoff, not a free win.** Turning it on would also mean every
  order this session places waits on a tap — which directly contradicts the
  "fire within the rails" authority granted on 2026-09-04. The holder cannot
  have both unattended execution and mandatory approval. Worth saying plainly
  rather than recommending the safe-sounding option by reflex: given that RATCHET
  is dormant and this session is placing nothing, turning approvals **on** costs
  almost nothing right now and closes the gap that actually caused harm. If
  trading resumes under the v1.3 grant, it becomes a genuine choice.

Recorded so future runs point at the remedy instead of re-reporting the
complaint. Four flags with no fix available was the right thing to do; a fifth
would not have been.

---

## 2026-11-02 · First income the account has ever produced: a $6.34 dividend

Account **$2,542.56** — 3.358353 SPY worth $2,531.34, cash **$11.22**. No orders
between 10-26 and 11-02. Approval setting still `human_must_approve_trades =
false`. Seventh consecutive week with no trading activity.

**The one real change:** cash went $4.88 → $11.22 with the share count
unchanged and no orders on the book. Verified rather than assumed — SPY's
distribution with ex-date 2026-09-18 **paid on 2026-10-30** at
**$1.888834/share**, and 3.358353 × 1.888834 = **$6.3434**, which matches the
$6.34 credit exactly.

Two things that follow from it:

- **DRIP is off.** The dividend arrived as cash, not as additional shares. Worth
  knowing because a Core sleeve that is meant to be bought and held compounds
  faster with reinvestment, and at this size $6.34 a quarter will otherwise just
  sit as idle cash. Turning DRIP on is the holder's to do in the Robinhood app;
  no tool here changes it. Flagging it once as information, not as a
  recommendation — at $2,540 the difference is a few dollars a year, and it is
  not worth a decision the holder has to make while the strategy is dormant.
- **Total return is not the same as the mark.** The position marks at −$28.66
  (−1.12%) against the $2,560 cost basis, but with the $6.34 distribution in
  hand the total return is **−$22.32 (−0.87%)**. Both numbers are small and both
  are noise at this horizon; recorded so the dividend is not silently lost from
  the return calculation later.

Nothing else to report. RATCHET remains dormant pending the instrument decision
— the Convexity sleeve is specified as debit verticals and this account rejects
multi-leg orders, which money does not fix.

---

## 2026-11-06 · Core rotated SPY → SPCX (SpaceX). RATCHET is retired.

Executed on the holder's explicit instruction: "close the position on the S&P 500
and roll it over to going long on SpaceX," confirmed with "Go."

| | |
|---|---|
| SOLD | 3.358353 SPY @ **$740.705**, fees $0.05 → $2,487.50 |
| BOUGHT | **19.003746 SPCX @ $131.2899**, no fees → $2,495.00 |
| Account after | $2,499.29 — $2,495.57 SPCX, $3.72 cash |

Both market orders, filled 34 seconds apart in the same session, so the account
was never left sitting in cash with the decision half-made. Realized **−$72.50**
on SPY against the $2,560 basis; net of the $6.34 dividend collected 2026-10-30,
the whole SPY episode cost **−$66.16**.

### A factual error I made, corrected

I opened this exchange by telling the holder SpaceX is privately held and has no
ticker. **That was wrong.** SPCX — Space Exploration Technologies Corp. Class A —
listed on **2026-06-12**, after this model's May 2026 training cutoff. The error
was corrected in the same conversation before anything was placed, and every
figure below came from live tools rather than recall. **Standing lesson: on this
account, any claim about what exists or is tradable must come from a tool call.
The training cutoff is now months stale and will keep getting staler.**

### What SPCX actually is, from its own record

| | |
|---|---|
| History | 102 sessions since 2026-06-12 (~5 months) |
| Annualized volatility | **79.7%** — roughly 5× SPY |
| Worst drawdown since listing | **−46.3%** |
| 52wk high → low | $225.64 → $104.83 (−53.5%) |
| Entry $131.29 vs high | **−41.8%** |
| Sessions moving ≥5% | 22 of 101 (**22%**) |
| Market cap / P/B | $1.79T / 9.50 · no P/E figure |
| Shares out / float | 13.58B / 4.29B — **31.6% float** |
| Liquidity | 107M shares/day, penny spread |

Per the filing description this is SpaceX, Starlink **and xAI/Grok** combined
following the xAI acquisition — not a pure launch business.

The holder was shown all of the above, including that a repeat of SPCX's own worst
drawdown takes $2,488 to roughly $1,335, and instructed the trade anyway. That is
their call and it was informed.

**One risk flagged as a question, not a fact:** 68% of shares are outside the
float. On a June IPO a conventional 180-day lockup would expire around early-to-mid
December, about five weeks out. SpaceX's actual lockup terms were not verified and
should be before adding to this position.

### RATCHET is retired, and saying so is honest rather than sad

Core-is-SPY was the charter's first rule; a single 80%-vol stock is not a Core
sleeve. The framework had already been **unfunded, then unimplementable** since
2026-09-10, when it emerged that this account rejects multi-leg orders and
therefore cannot place the debit verticals the Convexity sleeve is made of. Eight
weekly status reports said "dormant pending the instrument decision." This
rotation does not kill a working strategy; it formalises one that stopped being
executable two months ago.

What survives and is worth keeping: the friction and strike-grid work, the
PDT arithmetic, the geometric-vs-arithmetic return analysis, the finding that
only a live `place_option_order` reveals the multi-leg restriction, and the
single-leg-exit rule. The expectancy simulations in `RATCHET.md` §7 do **not**
transfer to anything and should not be cited for the new position.

**The weekly status routine is being retired with it** — it existed to report a
dormant framework. A single concentrated stock position needs either real
monitoring or none, not a two-line weekly note, and that is the holder's call.

### Repository incident, recorded because it nearly lost this journal

On arriving today the working tree had no `CLAUDE.md` and no `strategy/`. The
branch `claude/robinhood-ai-strategy-1rjntq` had been **force-pushed to unrelated
work** (TikTok OAuth relay pages, head `14adebe`), orphaning every RATCHET commit
from `df9d54a` through `15d92d4`.

The history was recovered from **`refs/pull/1/head`**, which GitHub still held at
`15d92d4` — a force-push over a branch does not remove commits a pull request
references. This entry therefore sits on a **new branch, `claude/ratchet-journal`**.

The old branch was deliberately **not** restored: force-pushing this history back
would have destroyed whoever's TikTok work now occupies that name. Recovering by
addition rather than overwrite was the only safe option, and the same reasoning
applies to anyone who finds this later.

---

## 2026-11-06 (same session, 3h later) · SPCX → SPCH. The account is now 2x leveraged.

Three hours after the SPY → SPCX rotation above, the holder asked for "a hot
aggressive move," then "sell and buy long on spacex all in," then chose
**leverage** from the options offered and said "place it."

| | |
|---|---|
| SOLD | 19.003746 SPCX @ **$132.6201**, fees $0.06 → **$2,520.08** |
| | order `6aee1d76-48b5-4e1a-94cb-bdaee9110b85`, 18:33:27Z |
| BOUGHT | **349.519410 SPCH** @ **$7.2099**, $2,520.00 dollar-based market order, no fees |
| | order `6aee1d90-4104-4ff4-a347-cf3779f0b920`, 18:33:52Z |

The two fills are **25 seconds apart**. The SPCX position was therefore opened
and closed in one session: **one day trade consumed**, 1 of 3 in the rolling
five-business-day window, ageing off after Nov 13. It also made **+$25.08** on a
three-hour hold, which is noise and is recorded as noise.

SPCH is a **2x daily-reset leveraged fund on SPCX** — per its own filing
description, "2x leveraged exposure to the daily price movement of Space
Exploration Technologies Corp." It is not SpaceX. It is a derivative of SpaceX
that resets its leverage every day.

### What was put in front of the holder before the order

All five 2x SpaceX funds peaked **2026-06-16** — the same day as SPCX itself —
and bottomed **2026-08-06**. At the time of the trade SPCX was **−41.8%** from
its high while the 2x funds were **−73.6% to −74.9%** from theirs. That gap is
not tracking error; it is the structural cost of daily rebalancing through a
−53% round trip. Intraday they track correctly (that session SPCX +6.27%, the
funds +12.3% to +13.1%), which is exactly the point: **they deliver 2x of a day
and much worse than 2x of a year.**

The arithmetic, stated plainly at the time: for a k× daily-reset fund the
volatility drag is ≈ **k(k−1)σ²/2**, which at k=2 is simply **σ²**. At SPCX's
79.7% annualized volatility that is **−63.5% per year of log return — about
−47% over a flat year.** SPCX can finish a year unchanged and this position
still loses roughly half its value.

Two further consequences, each stated once:

- A **~50% adverse move in SPCX wipes this out** (SPCX ≈ $71 from here).
- The possible December lockup supply event is now taken **at 2x**.

**SPCH was chosen among the five** purely on depth — ~$373M market cap at the
time, 24.8M average shares/day, penny spread. Of a bad set it is the liquid one.

### The recommendation was against this trade and the holder overrode it

What was said, verbatim in substance: *of everything discussed since September,
this is the position most likely to end at zero, and it is the first one with no
exit plan attached.* The holder said "place it." That is their call, it was made
on the numbers above rather than in ignorance of them, and the order was placed
because the authority to act on an explicit instruction is not conditional on
agreeing with it.

What is **not** true and must not be written later: that this was advised, or
that any analysis in `strategy/` supports it. **Nothing in this repository
describes a leveraged single-stock position.** There is no framework, no
position cap, no stop and no stated holding period.

---

## 2026-11-09 · The lockup question is answered, with sources. It is Dec 8.

Friday's entry left one item open: SpaceX's **actual** lockup terms were never
verified, and a guess of "around 2026-12-09" was recorded as a guess. Verified
today.

**SpaceX did not use a single 180-day cliff.** Per the S-1 the schedule is
staggered: 20% of eligible insider shares after Q2 earnings, **plus a further
10% triggered because the stock closed ≥30% above the $135 IPO price (≥$175.50)
on 5 of 10 sessions**; then **7% at each of days 70, 90, 105, 120 and 135**; a
**28% block** after Q3 earnings; and the remainder at the 180-day mark.

| Tranche | Date | Size |
|---|---|---|
| First (Q2 earnings) | 2026-08-06 | ~911.5M shares — float **+140%** |
| Accelerated 30% clause | 2026-08-20 | smaller |
| Day 90 | 2026-09-09 | ~319M |
| Day 105 | 2026-09-24 | ~328.4M |
| Day 120 | 2026-10-09 | ~319M |
| Day 135 (weekend-shifted) | 2026-10-26 | ~319M |
| Q3 earnings block | post 10-Q (filed 10-22) | 28% |
| **Final — clears the rest** | **2026-12-08** | remainder; **~40% of the company then tradeable** |
| Musk's own stake | **~June 2027** (366 days post-IPO) | excluded from every early release |

Sources: Benzinga 2026-09-24 for the Dec 8 date and the 40% figure; CNBC
2026-05-21 for the S-1 mechanics; Benzinga 2026-07-17 for "mid-December" and the
Musk/June-2027 restriction. 180 calendar days from the 2026-06-12 debut is
Dec 9, so Dec 8 and "mid-December" are consistent with each other.

**The guess was arithmetically right and that is not the same as being right.**
Friday's "around December 9" happened to land within a day of the real date, but
it was stated without a source — the identical failure mode as asserting that
SpaceX was private and untradable earlier the same day, with a luckier outcome.
A correct unsourced claim is still an unsourced claim. Recorded because the
luck, not the method, is what differed.

**What it means, and what it does not.** The last and largest supply event is
**~4 weeks out** and the account holds a 2x fund into it. But the record argues
against assuming a crash: the **Aug 6 unlock was the biggest of all** — it grew
the tradable float by over 140% — **and the stock rallied**; Aug 20 produced a
temporary wobble. Unlock dates have not reliably been down days for this name.
The honest statement is that a known, dated supply event sits four weeks ahead
of a position with 2x sensitivity and no stop — not that it will fall.

### Monday's mark

| | |
|---|---|
| Position | **349.519410 SPCH**, cost **$2,520.00** ($7.2099/sh) |
| Price | $8.25 last (bid 8.24 / ask 8.25), from a $7.36 Friday close |
| Value | **$2,883.54** |
| Unrealized | **+$363.54 · +14.43%** |
| Account | **$2,885.73**, cash $3.94, ~99.9% in SPCH |
| SPCH today | +12.09% |
| SPCX today | +5.96% |
| Realized leverage | **2.03x — the fund is tracking as designed** |

Had the account stayed in SPCX it would be worth **$2,703.66**. The leverage has
added about **$180 in two sessions**. That is the leverage working in the
direction it was bought for over two sessions, and it says nothing whatever
about the decay cost over months — the −63.5%/yr figure is a statement about
variance, not about any two days.

SPCH remains **−70.5%** from its 2026-06-16 high of $28.01 and **+55.7%** off
its 2026-08-06 low of $5.30. SPCX is −36.9% from $225.64 and +35.7% off $104.83.

**Checks run, nothing actionable:** no option positions. No orders this session
did not place — all four Nov 6 orders are this session's, and the unexplained
09-08/09-17 pattern did not repeat. `human_must_approve_trades` still reads
**false** (unchanged since 2026-08-26). Day trades 1 of 3 used. No orders placed
today and none authorised.

**Still no stop.** Said once, in Friday's entry and once here: this position has
no exit plan, and a single-leg `stop_market` would actually rest on it — unlike
the spread that could not be protected in September. Whether to set one is the
holder's call and has been put to them.

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
