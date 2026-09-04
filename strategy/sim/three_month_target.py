#!/usr/bin/env python3
"""$1,500 -> $25,000 in 3 months: what it requires, and what chasing it does.

Simulates two approaches over 63 trading days (~3 calendar months):
  RATCHET  - as specified: 30% convexity sleeve, $150/position cap, weekly sweep
  ALL-IN   - the only structure that could plausibly reach $25k: full account
             on one 30-delta vertical at a time, rolled straight into the next

Vertical outcomes use the touch probabilities measured in time_to_target.py
under risk-neutral drift (no edge assumed): ~31% reach +100%, ~67% hit the
-50% stop, ~2% time out near flat.
"""

import math
import random

random.seed(20260902)
START, TARGET, DAYS, PATHS = 1500.0, 25000.0, 63, 200000
P_WIN, P_STOP = 0.314, 0.665      # measured NVDA touch probabilities
HOLD = 8                          # trading days median to resolution
FRICTION = 0.082                  # NVDA round-trip, as fraction of debit
MIN_TRADE = 60.0                  # below this you cannot buy a $5-wide vertical

print("=" * 84)
print("WHAT $1,500 -> $25,000 IN 3 MONTHS REQUIRES".center(84))
print("=" * 84)
mult = TARGET / START
print(f"  multiple needed        : {mult:.2f}x")
print(f"  per trading day (63)   : {(mult ** (1/63) - 1) * 100:+.2f}%  EVERY day")
print(f"  per month              : {(mult ** (1/3) - 1) * 100:+.1f}%")
print(f"  annualised             : {mult ** 4:,.0f}x per year")
print(f"  $1,500 at that rate, 1 yr: ${START * mult ** 4:,.0f}")
print()
print("  For reference, Renaissance Medallion — the best track record in the")
print("  history of finance — compounds at roughly 66%/yr gross. That is")
print(f"  {0.66/((mult**4)-1)*100:.6f}% of the rate this target needs.")
print()
print("  Doublings required: log2(16.67) = 4.06. You need the account to")
print("  double four times over, back to back, in thirteen weeks.")

def run_allin():
    """Full account into one vertical at a time, rolled continuously."""
    eq, day, peak = START, 0, START
    while day < DAYS:
        if eq < MIN_TRADE:
            return 0.0, peak, True
        eq -= eq * FRICTION
        r = random.random()
        if r < P_WIN:
            eq *= 2.0
        elif r < P_WIN + P_STOP:
            eq *= 0.5
        peak = max(peak, eq)
        day += HOLD
        if eq >= TARGET:
            return eq, max(peak, eq), False
    return eq, peak, eq < MIN_TRADE

def run_ratchet():
    """Sleeve capped at 30%, $150/position, core compounds underneath."""
    core, cash, s0 = START * 0.70, START * 0.30, START * 0.30
    mu, sig = 0.08 / 252, 0.16 / math.sqrt(252)
    open_pos, day = [], 0
    for day in range(DAYS):
        core *= math.exp(mu - 0.5 * sig ** 2 + sig * random.gauss(0, 1))
        still = []
        for res, debit in open_pos:
            if res <= day:
                r = random.random()
                gross = debit * 2.0 if r < P_WIN else (
                    debit * 0.5 if r < P_WIN + P_STOP else debit * 0.9)
                cash += gross - debit * FRICTION
            else:
                still.append((res, debit))
        open_pos = still
        if day % 5 == 4:                       # weekly ratchet
            val = cash + sum(d for _, d in open_pos)
            if val > s0:
                sweep = min(val - s0, cash); core += sweep; cash -= sweep
        if len(open_pos) < 3 and random.random() < 0.35:
            debit = min(150.0, cash / max(1, 3 - len(open_pos)))
            if debit >= 20:
                cash -= debit
                open_pos.append((day + HOLD, debit))
    return core + cash + sum(d for _, d in open_pos)

for name, fn in (("ALL-IN (chasing $25k)", run_allin), ("RATCHET (as designed)", run_ratchet)):
    finals = []
    hits = ruins = 0
    for _ in range(PATHS):
        if fn is run_allin:
            v, _, ruined = fn()
            ruins += ruined
        else:
            v = fn()
        finals.append(v)
        hits += v >= TARGET
    finals.sort()
    n = len(finals)
    q = lambda p: finals[int(p * (n - 1))]
    print()
    print("=" * 84)
    print(name.center(84))
    print("=" * 84)
    print(f"  reached $25,000        : {hits/n*100:>7.3f}%   ({hits:,} of {n:,} paths)")
    if fn is run_allin:
        print(f"  wiped out (<$60)       : {ruins/n*100:>7.2f}%")
    print(f"  median outcome         : ${q(0.50):>10,.0f}")
    print(f"  5th / 25th percentile  : ${q(0.05):>10,.0f} / ${q(0.25):,.0f}")
    print(f"  75th / 95th percentile : ${q(0.75):>10,.0f} / ${q(0.95):,.0f}")
    print(f"  ended below $1,500     : {sum(1 for v in finals if v < START)/n*100:>7.1f}%")
    print(f"  ended below $500       : {sum(1 for v in finals if v < 500)/n*100:>7.1f}%")

print()
print("=" * 84)
print("THE DEPOSIT PATH".center(84))
print("=" * 84)
need = (TARGET - START) / 3
print(f"  $25,000 in 3 months, funded rather than traded: ${need:,.0f}/month.")
print(f"  Certainty: 100%. No path dependence, no ruin branch.")
