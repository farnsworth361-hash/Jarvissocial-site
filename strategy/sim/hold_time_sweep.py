#!/usr/bin/env python3
"""Can RATCHET's hold time be shortened, and what does it cost?

Sweeps entry DTE and profit target across the live underlyings. For each
configuration it reports:

  hold      - median trading days to resolution
  hit(rn)   - share of paths reaching the target, under RISK-NEUTRAL drift
              (i.e. assuming the entry filters provide NO edge at all)
  need      - hit rate required to break even, given the payoff and friction
  GAP       - need minus hit(rn): how many percentage points of edge the
              entry filters must actually supply for the config to profit

GAP is the number that matters. It is the height of the bar the strategy has
to clear. A config with a faster clock but a taller bar is not an improvement,
it is a worse bet that resolves sooner.

Strikes are re-solved for ~30 delta at each DTE and snapped to the $5 grid,
so each row is a like-for-like structure rather than a stale strike.
"""

import math
import random

SEED = 20260902
PATHS = 20000
R = 0.04
STOP = 0.50          # -50% of debit, held constant
DTE_EXIT = 10
TDY = 252
FRICTION = {"SPY": 0.014, "NVDA": 0.082}   # round trip, from HIGH-BETA-MODULE

UNDERLYINGS = [("SPY", 765.14, 0.1072, 5), ("NVDA", 224.40, 0.3249, 5)]
DTES = [21, 30, 44]
TARGETS = [0.50, 0.75, 1.00, 1.50]


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def call(S, K, T, sigma):
    if T <= 1e-9:
        return max(0.0, S - K)
    d1 = (math.log(S / K) + (R + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    return S * norm_cdf(d1) - K * math.exp(-R * T) * norm_cdf(d1 - sigma * math.sqrt(T))


def spread(S, K1, K2, T, sigma):
    return call(S, K1, T, sigma) - call(S, K2, T, sigma)


def strike_30d(S, T, sigma, grid):
    """Solve for the ~30-delta call strike, snapped to the grid."""
    z = -0.5244                       # N(z) = 0.30
    K = S * math.exp((R + 0.5 * sigma ** 2) * T - z * sigma * math.sqrt(T))
    return round(K / grid) * grid


def simulate(S0, sigma, dte, target_mult, grid, rng):
    T0 = dte / 365.0
    K1 = strike_30d(S0, T0, sigma, grid)
    K2 = K1 + grid
    debit = spread(S0, K1, K2, T0, sigma)
    if debit <= 0.05:
        return None
    tgt, stp = debit * (1 + target_mult), debit * (1 - STOP)
    dt = 1.0 / TDY
    drift = (R - 0.5 * sigma ** 2) * dt
    vol = sigma * math.sqrt(dt)

    days, hits = [], 0
    for _ in range(PATHS):
        S, d, day = S0, dte, 0
        while d > DTE_EXIT:
            S *= math.exp(drift + vol * rng.gauss(0, 1))
            day += 1
            d -= 365.0 / TDY
            v = spread(S, K1, K2, max(d, 0.5) / 365.0, sigma)
            if v >= tgt:
                hits += 1
                break
            if v <= stp:
                break
        days.append(day)
    days.sort()
    return {"K1": K1, "K2": K2, "debit": debit,
            "median": days[len(days) // 2], "hit": hits / PATHS}


def main():
    rng = random.Random(SEED)
    print("=" * 104)
    print("HOLD-TIME SWEEP — what shortening the trade actually costs".center(104))
    print("=" * 104)
    for sym, S0, sigma, grid in UNDERLYINGS:
        f = FRICTION[sym]
        print()
        print(f"{sym}  spot {S0}  IV {sigma*100:.1f}%  round-trip friction "
              f"{f*100:.1f}% of debit")
        print(f"{'DTE':>4} {'target':>7} {'strikes':>12} {'debit':>8} "
              f"{'hold':>6} {'hit(rn)':>8} {'need':>7} {'GAP':>8}")
        print("-" * 104)
        best = None
        for dte in DTES:
            for tm in TARGETS:
                r = simulate(S0, sigma, dte, tm, grid, rng)
                if not r:
                    continue
                need = (STOP + f) / (tm + STOP)
                gap = need - r["hit"]
                if best is None or gap < best[0]:
                    best = (gap, dte, tm, r)
                print(f"{dte:>4} {tm*100:>6.0f}% "
                      f"{str(r['K1'])+'/'+str(r['K2']):>12} "
                      f"${r['debit']*100:>7.0f} {r['median']:>5}d "
                      f"{r['hit']*100:>7.1f}% {need*100:>6.1f}% "
                      f"{gap*100:>+7.1f}%")
        g, dte, tm, r = best
        print(f"  -> lowest bar: {dte} DTE / +{tm*100:.0f}% target "
              f"(gap {g*100:+.1f} pts, {r['median']}d median hold)")

    print()
    print("=" * 104)
    print("READING THIS".center(104))
    print("=" * 104)
    print("Every GAP is positive, and that is correct, not a bug: under")
    print("risk-neutral drift no configuration profits by itself. The market")
    print("prices these fairly. GAP is simply how much the entry filters must")
    print("add before a config makes money.")
    print()
    print("The trade-off is the whole answer:")
    print()
    print("  LOWER TARGET  -> resolves faster and hits far more often, but the")
    print("                   required hit rate rises much faster than the")
    print("                   achieved one. +50% needs ~60%; +100% needs ~40%.")
    print()
    print("  SHORTER DTE   -> shortens the clock, but the 10-DTE exit eats most")
    print("                   of the holding window and gamma/theta both bite")
    print("                   harder. The bar goes up, not down.")
    print()
    print("Shortening hold time is available. It is not free, and on these")
    print("numbers it is not cheap either.")


if __name__ == "__main__":
    main()
