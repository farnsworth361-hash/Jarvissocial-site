#!/usr/bin/env python3
"""RATCHET journal statistics.

Computes the exact quantities RATCHET.md section 10 uses to decide whether the
strategy is working or should be abandoned. Run after every close:

    python3 stats.py

Reads trades.csv. Reports nothing it cannot support: with few closed trades the
confidence interval on the hit rate is enormous, and this script says so rather
than printing a precise-looking number that means nothing.
"""

import csv
import math
import os
import sys

TARGET_MULT = 1.00        # win  = +100% of debit
STOP_MULT = -0.50         # loss = -50% of debit
ASSUMED_FRICTION = 0.10   # the round-trip figure the expectancy math assumes

# section 10 abandonment thresholds
MIN_TRADES_TO_JUDGE = 60
ABANDON_HIT_RATE = 0.43
ABANDON_FRICTION = 0.08

HERE = os.path.dirname(os.path.abspath(__file__))


def wilson(k, n, z=1.96):
    """Wilson score interval — correct for small n, unlike normal approximation."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return ((c - m) / d, (c + m) / d)


def breakeven(friction):
    """Hit rate needed for zero expectancy at the given round-trip friction."""
    return (-STOP_MULT + friction) / (TARGET_MULT - STOP_MULT)


def main():
    path = os.path.join(HERE, 'trades.csv')
    if not os.path.exists(path):
        print(f"no trades.csv at {path}")
        return 1

    with open(path) as f:
        rows = [r for r in csv.DictReader(f) if r.get('date_opened', '').strip()]

    opened = len(rows)
    closed = [r for r in rows if r.get('date_closed', '').strip()]
    n = len(closed)

    print("=" * 72)
    print("RATCHET journal".center(72))
    print("=" * 72)
    print(f"positions opened : {opened}")
    print(f"positions closed : {n}")

    # Entry slippage is measurable from the moment a position opens -- it does
    # not require the trade to be closed, and it is the earliest signal that the
    # expectancy assumptions are wrong.
    slips = []
    for r in rows:
        try:
            mid, fill = float(r['debit_mid']), float(r['debit_filled'])
            if mid > 0:
                slips.append((fill - mid) / mid)
        except (ValueError, KeyError):
            pass

    if slips:
        avg_entry = sum(slips) / len(slips)
        est_rt = avg_entry * 2
        print()
        print("-- execution ------------------------------------------------")
        print(f"entry slippage vs mid : {avg_entry * 100:+.2f}%  (n={len(slips)})")
        print(f"implied round trip    : {est_rt * 100:.2f}% of debit")
        print(f"assumed in the model  : {ASSUMED_FRICTION * 100:.2f}%")
        print(f"break-even hit rate   : {breakeven(est_rt) * 100:.1f}% "
              f"(model assumed {breakeven(ASSUMED_FRICTION) * 100:.1f}%)")
        if est_rt > ABANDON_FRICTION * 2:
            print(f"  ** friction is running hot. Section 10 flags a round trip "
                  f"above {ABANDON_FRICTION * 2 * 100:.0f}%.")
    else:
        print()
        print("-- execution ------------------------------------------------")
        print("no fills recorded yet. Entry slippage is the earliest warning")
        print("sign available -- log debit_mid and debit_filled on every fill.")

    if n == 0:
        print()
        print("-- outcome --------------------------------------------------")
        print("No closed trades. Nothing can be concluded about edge yet.")
        print(f"Section 10 requires {MIN_TRADES_TO_JUDGE} closed trades before "
              f"judging this strategy.")
        print("=" * 72)
        return 0

    wins = sum(1 for r in closed if r.get('hit', '').strip() == '1')
    hit = wins / n
    lo, hi = wilson(wins, n)

    pnl = 0.0
    debits = 0.0
    for r in closed:
        try:
            pnl += float(r['pnl'])
            debits += float(r['debit_filled']) * float(r.get('contracts') or 1) * 100
        except (ValueError, KeyError):
            pass

    print()
    print("-- outcome --------------------------------------------------")
    print(f"hit rate     : {hit * 100:.1f}%  ({wins}/{n})")
    print(f"95% interval : {lo * 100:.1f}% -- {hi * 100:.1f}%")
    print(f"realized P&L : ${pnl:+,.2f}")
    if debits:
        print(f"expectancy   : {pnl / debits * 100:+.2f}% of deployed debit")

    print()
    print("-- section 10 verdict ---------------------------------------")
    if n < MIN_TRADES_TO_JUDGE:
        print(f"{n}/{MIN_TRADES_TO_JUDGE} closed trades. TOO EARLY TO JUDGE.")
        print(f"The interval above spans {(hi - lo) * 100:.0f} points -- it cannot")
        print("yet separate a working strategy from a broken one.")
        print("Do not tune parameters on this sample. That is curve fitting.")
    elif hi < ABANDON_HIT_RATE:
        print(f"ABANDON. Hit rate {hit * 100:.1f}% and the whole confidence")
        print(f"interval sits below the {ABANDON_HIT_RATE * 100:.0f}% line.")
        print("Section 10: stop trading convexity and hold core. Do NOT retune.")
    elif hit < ABANDON_HIT_RATE:
        print(f"WARNING. Hit rate {hit * 100:.1f}% is below the "
              f"{ABANDON_HIT_RATE * 100:.0f}% abandonment line,")
        print(f"but the interval still reaches {hi * 100:.1f}%. Keep logging.")
    else:
        print(f"CONTINUE. Hit rate {hit * 100:.1f}% clears the "
              f"{ABANDON_HIT_RATE * 100:.0f}% line.")
    print("=" * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
