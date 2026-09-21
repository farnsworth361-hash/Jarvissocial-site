#!/usr/bin/env python3
"""High-beta underlying comparison for the RATCHET convexity sleeve.

All quotes are live 2026-10-16 (44 DTE) calls captured 2026-09-02 at the close.
Delta-matched ~30-delta $5-wide debit verticals, one contract each.

The question this answers: does trading a higher-volatility underlying actually
improve the sleeve, or does it just cost more friction for the same odds?
"""

TARGET_MULT = 1.00
STOP_MULT = -0.50
TICK = 0.05          # single-name min tick above $3.00; SPY quotes in pennies

# name, spot, long(bid,ask,mark,iv,delta,oi), short(bid,ask,mark,iv,delta,oi),
# strikes, chance_of_profit_long
ROWS = [
    ("SPY  785/790", 765.14,
     (5.07, 5.08, 5.075, 0.1072, 0.2903, 13255),
     (3.62, 3.63, 3.625, 0.1048, 0.2286, 13074), 785, 790, 0.2227, 0.01),
    ("NVDA 240/245", 224.40,
     (4.65, 4.80, 4.725, 0.3249, 0.3090, 41383),
     (3.45, 3.55, 3.500, 0.3237, 0.2468, 24543), 240, 245, 0.2163, TICK),
    ("PLTR 185/190", 169.46,
     (5.35, 5.50, 5.425, 0.4619, 0.3305, 3979),
     (4.05, 4.25, 4.150, 0.4595, 0.2713, 3520), 185, 190, 0.2179, TICK),
    ("TSLA 390/395", 356.99,
     (9.55, 9.85, 9.700, 0.4243, 0.3100, 2652),
     (8.40, 8.60, 8.500, 0.4249, 0.2805, 2310), 390, 395, 0.2090, TICK),
    ("MSTR 140/145", 123.24,
     (6.30, 6.55, 6.425, 0.7137, 0.3548, 3917),
     (5.20, 5.45, 5.325, 0.7216, 0.3065, 5137), 140, 145, 0.2114, TICK),
]


def breakeven(rt):
    return (-STOP_MULT + rt) / (TARGET_MULT - STOP_MULT)


print("=" * 112)
print("Delta-matched 30-delta $5-wide debit verticals, 2026-10-16 (44 DTE)".center(112))
print("=" * 112)
print(f"{'Spread':<14} {'IV':>7} {'mid $':>8} {'max P':>8} {'R:R':>7} "
      f"{'tgt %max':>9} {'comb OI':>9} {'P(profit)':>10}")
print("-" * 112)
for name, spot, lo, sh, k1, k2, pop, tick in ROWS:
    mid = lo[2] - sh[2]
    width = k2 - k1
    maxp = width - mid
    print(f"{name:<14} {lo[3]*100:>6.1f}% ${mid*100:>7.2f} ${maxp*100:>7.2f} "
          f"{maxp/mid:>6.2f}:1 {mid/maxp*100:>8.1f}% "
          f"{lo[5]+sh[5]:>9,} {pop*100:>9.1f}%")

print()
print("=" * 112)
print("FRICTION — the cost of leaving SPY".center(112))
print("=" * 112)
print("Single-name options quote in $0.05 ticks above $3.00. SPY quotes in")
print("pennies. That is a floor on how tight their spreads can ever be.")
print()
print(f"{'Spread':<14} {'mid $':>8} {'cross $':>9} {'cross %':>8} "
      f"{'BE(cross)':>10} | {'+1 tick':>9} {'tick %':>8} {'BE(tick)':>9}")
print("-" * 112)
for name, spot, lo, sh, k1, k2, pop, tick in ROWS:
    mid = lo[2] - sh[2]
    cross = lo[1] - sh[0]                 # buy the ask, sell the bid
    slip_x = (cross - mid) / mid
    realistic = mid + tick                # patient limit, one tick through mid
    slip_t = (realistic - mid) / mid
    print(f"{name:<14} ${mid*100:>7.2f} ${cross*100:>8.2f} {slip_x*100:>7.1f}% "
          f"{breakeven(slip_x*2)*100:>9.1f}% | ${realistic*100:>8.2f} "
          f"{slip_t*100:>7.1f}% {breakeven(slip_t*2)*100:>8.1f}%")

print()
print("=" * 112)
print("THE FINDING".center(112))
print("=" * 112)
print("Look at the P(profit) column. Every one of these sits at 21-22%.")
print()
print("Delta-matching standardises the bet. A 30-delta option is a 30-delta")
print("option whether the underlying moves 1% a day or 5% a day -- the higher")
print("IV is already in the price. Buying a 'more volatile' name at the same")
print("delta does NOT raise your odds of winning. The market is not offering")
print("free movement.")
print()
print("What DOES change, and is worth having:")
print()
for name, spot, lo, sh, k1, k2, pop, tick in ROWS:
    mid = lo[2] - sh[2]
    maxp = (k2 - k1) - mid
    sigma = spot * lo[3] * (44 / 365) ** 0.5
    need = (k1 - spot) / spot
    print(f"  {name:<14} target is {mid/maxp*100:>5.1f}% of max profit;  "
          f"1σ(44d) = {sigma/spot*100:>5.1f}%;  needs {need*100:>+5.1f}% "
          f"({need*spot/sigma:>4.2f}σ)")
print()
print("The $5 width is a far smaller slice of a volatile name's expected move,")
print("so the debit is cheaper relative to the width and the reward:risk is")
print("better. NVDA pays 3.08:1 against SPY's 2.45:1, and its +100% target is")
print("32.5% of max profit versus SPY's 40.8% -- a materially easier bar.")
print()
print("That is the real trade: same win probability, bigger payoff when right,")
print("bigger loss when wrong, and 4-5 extra points of break-even hit rate")
print("handed to the market maker in wider ticks. Worth it only if you accept")
print("the variance -- it is not a free upgrade.")
