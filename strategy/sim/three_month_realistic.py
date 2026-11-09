#!/usr/bin/env python3
"""What is realistically achievable in 3 months (63 trading days)?

The answer hinges entirely on the one unknown: whether the entry filters lift
the hit rate above break-even. Nothing is backtested, so this sweeps the range
rather than asserting a number.

Reference points:
  31.4% - the risk-neutral touch rate. The filters add NOTHING.
  ~39%  - break-even on SPY-weighted friction
  45%   - filters add a modest, plausible edge
  50%   - filters work well
"""

import math, random

random.seed(20260902)
START, DAYS, PATHS = 1500.0, 63, 100000
HOLD, FRICTION = 8, 0.05          # blended SPY/single-name round trip

def run(p_win, p_stop_share=0.955):
    core, cash, s0 = START * 0.70, START * 0.30, START * 0.30
    mu, sig = 0.08 / 252, 0.16 / math.sqrt(252)
    open_pos, trades = [], 0
    for day in range(DAYS):
        core *= math.exp(mu - 0.5 * sig ** 2 + sig * random.gauss(0, 1))
        still = []
        for res, debit in open_pos:
            if res <= day:
                r = random.random()
                if r < p_win:
                    gross = debit * 2.0
                elif r < p_win + (1 - p_win) * p_stop_share:
                    gross = debit * 0.5
                else:
                    gross = debit * 0.9
                cash += gross - debit * FRICTION
            else:
                still.append((res, debit))
        open_pos = still
        if day % 5 == 4:
            val = cash + sum(d for _, d in open_pos)
            if val > s0:
                sweep = min(val - s0, cash); core += sweep; cash -= sweep
        if len(open_pos) < 3 and random.random() < 0.35:
            debit = min(150.0, cash / max(1, 3 - len(open_pos)))
            if debit >= 20:
                cash -= debit; open_pos.append((day + HOLD, debit)); trades += 1
    return core + cash + sum(d for _, d in open_pos), trades

print("=" * 86)
print("REALISTIC 3-MONTH OUTCOMES — $1,500 start, 63 trading days".center(86))
print("=" * 86)
print()
print(f"{'scenario':<26} {'median':>9} {'5th':>8} {'25th':>8} {'75th':>8} "
      f"{'95th':>8} {'P(up)':>7}")
print("-" * 86)

for label, p in (("No edge at all (31%)", 0.314),
                 ("Break-even (39%)", 0.39),
                 ("Modest edge (45%)", 0.45),
                 ("Filters work well (50%)", 0.50)):
    finals, tr = [], []
    for _ in range(PATHS):
        v, t = run(p)
        finals.append(v); tr.append(t)
    finals.sort()
    n = len(finals); q = lambda x: finals[int(x * (n - 1))]
    up = sum(1 for v in finals if v > START) / n * 100
    print(f"{label:<26} ${q(.5):>8,.0f} ${q(.05):>7,.0f} ${q(.25):>7,.0f} "
          f"${q(.75):>7,.0f} ${q(.95):>7,.0f} {up:>6.1f}%")

print("-" * 86)
print(f"{'Core only (no trading)':<26}", end="")
finals = sorted(START * 0.70 * math.exp((0.08 - 0.5*0.16**2) * 0.25
                + 0.16 * math.sqrt(0.25) * random.gauss(0, 1)) + START * 0.30
                for _ in range(PATHS))
n = len(finals); q = lambda x: finals[int(x * (n - 1))]
up = sum(1 for v in finals if v > START) / n * 100
print(f" ${q(.5):>8,.0f} ${q(.05):>7,.0f} ${q(.25):>7,.0f} "
      f"${q(.75):>7,.0f} ${q(.95):>7,.0f} {up:>6.1f}%")

print()
print(f"Closed trades in 3 months: ~{sum(tr)/len(tr):.0f}")
print()
print("=" * 86)
print("READ THIS BEFORE THE NUMBERS".center(86))
print("=" * 86)
print("Across EVERY scenario the 90% range is roughly $1,050 to $2,000.")
print("Three months is too short for the edge — if there is one — to")
print("separate itself from noise. Even 'filters work well' has a wide")
print("losing tail, and even 'no edge' has winning paths. You cannot tell")
print("these apart from three months of P&L. That is the whole point.")
print()
print(f"~{sum(tr)/len(tr):.0f} closed trades is a quarter of the 60 that section 10")
print("requires before the strategy can be judged at all.")
