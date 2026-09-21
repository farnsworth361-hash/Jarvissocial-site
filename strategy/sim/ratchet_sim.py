#!/usr/bin/env python3
"""
RATCHET v1.0 -- Monte Carlo comparison.

Compares the RATCHET two-sleeve strategy against a full-size "double it daily"
attempt, over 252 trading sessions, starting from the account's actual $1,500.

=============================== READ THIS FIRST ===============================
These are ASSUMPTIONS, not backtested facts. No historical validation of the
CB or PED entry filters was performed. The purpose of this simulation is to
show the SHAPE of each approach's outcome distribution -- specifically that one
of them has a bounded downside and the other has a ruin probability that
compounds to near-certainty. It is not a forecast of returns.

The simulation is deliberately GENEROUS to the doubling approach:
  * It ignores the PDT rule, which would make ~5 day trades/week illegal in
    this account and stop the strategy outright after 3.
  * It assumes a per-trade edge better than most 0DTE buyers actually achieve.
It still goes to zero in essentially every path.
===============================================================================

Pure stdlib. Run:  python3 ratchet_sim.py
"""

import random
import math
from statistics import mean, NormalDist

SEED = 20260902
SESSIONS = 252
START_EQUITY = 1500.0
PATHS = 20000

# ---------------------------------------------------------------- RATCHET ---
CORE_TARGET_PCT = 0.70
CONVEXITY_PCT = 0.30
MAX_RISK_PER_POSITION = 150.0
MAX_CONCURRENT = 3
MAX_NEW_PER_WEEK = 2

TARGET_MULT = 1.00          # win  = +100% of debit
STOP_MULT = -0.50           # loss = -50% of debit
GAP_MULT = -1.00            # gap through the stop = full debit lost
GAP_PROB_GIVEN_LOSS = 0.15  # 15% of losers gap past the stop
FRICTION_PCT = 0.10         # round-trip bid/ask, as fraction of debit

HOLD_MIN, HOLD_MAX = 15, 30 # sessions (30-45 DTE entry, exit at 10 DTE)

CORE_MU_ANNUAL = 0.08
CORE_SIGMA_ANNUAL = 0.16

REFILL_CAP_WEEKLY_PCT = 0.02   # max refill per week, as pct of total equity
REFILL_CAP_ANNUAL_PCT = 0.20   # max total refills per year, pct of year-start
DRAWDOWN_HALT = 0.15           # halt convexity at -15% from high water
HALT_SESSIONS = 30

# ---------------------------------------------------------------- DOUBLER ---
# Full account into an ATM 0DTE-style position, every session.
# Calibrated to roughly -11% expectancy per trade, which is a defensible
# (arguably kind) estimate for full-size short-dated long premium with real
# spreads. The ruin driver is the 35% total-loss branch, and that branch's
# effect is robust to the exact expectancy calibration.
DOUBLER_OUTCOMES = [
    (0.22, +1.50),   # the trade that makes people believe: +150%
    (0.18, +0.20),
    (0.25, -0.50),
    (0.35, -1.00),   # expires worthless
]
# A DISCIPLINED version of the same goal: still bets the full account every
# session chasing a double, but always cuts at -50% and never lets anything
# expire worthless. Per-trade expectancy is roughly FLAT (+0.5%). It still
# fails -- not to a single wipeout, but to volatility drag, because the
# geometric mean of a full-size bet is far below its arithmetic mean.
DOUBLER_STOPPED = [
    (0.20, +1.50),
    (0.15, +0.20),
    (0.65, -0.50),
]

RUIN_FLOOR = 50.0    # below this you cannot buy another contract


def sample_outcome(rng, table):
    r = rng.random()
    c = 0.0
    for p, v in table:
        c += p
        if r <= c:
            return v
    return table[-1][1]


def run_ratchet(rng, hit_rate):
    """One 252-session path of the RATCHET strategy."""
    core = START_EQUITY * CORE_TARGET_PCT
    cash = START_EQUITY * CONVEXITY_PCT      # uninvested convexity cash
    s0 = START_EQUITY * CONVEXITY_PCT        # sleeve charter size
    hwm = START_EQUITY
    refilled_this_year = 0.0
    halt_until = -1
    open_positions = []   # list of [resolve_day, debit, payout]
    opened_this_week = 0

    mu_d = CORE_MU_ANNUAL / 252.0
    sig_d = CORE_SIGMA_ANNUAL / math.sqrt(252.0)

    for day in range(SESSIONS):
        # --- core drifts
        core *= math.exp((mu_d - 0.5 * sig_d ** 2) + sig_d * rng.gauss(0, 1))

        # --- resolve positions coming due (payout returns to cash)
        still_open = []
        for pos in open_positions:
            if pos[0] <= day:
                cash += pos[2]
            else:
                still_open.append(pos)
        open_positions = still_open

        # Open positions are carried at cost, so the sleeve is valued as
        # cash + deployed capital. Failing to do this makes the ratchet see a
        # permanently depleted sleeve and refill from Core every single week.
        deployed = sum(p[1] for p in open_positions)
        sleeve_value = cash + deployed
        equity = core + sleeve_value
        hwm = max(hwm, equity)

        # --- drawdown circuit breaker
        if equity < hwm * (1.0 - DRAWDOWN_HALT) and day > halt_until:
            halt_until = day + HALT_SESSIONS

        # --- weekly boundary: ratchet click + entry budget reset
        if day % 5 == 4:
            opened_this_week = 0
            if sleeve_value > s0:
                sweep = min(sleeve_value - s0, cash)   # can only sweep free cash
                core += sweep
                cash -= sweep
            elif sleeve_value < s0:
                want = s0 - sleeve_value
                weekly_cap = REFILL_CAP_WEEKLY_PCT * max(equity, 0.0)
                annual_left = max(
                    0.0, REFILL_CAP_ANNUAL_PCT * START_EQUITY - refilled_this_year)
                amt = min(want, weekly_cap, annual_left, max(core, 0.0))
                core -= amt
                cash += amt
                refilled_this_year += amt

        # --- try to open a position
        can_trade = (
            day > halt_until
            and len(open_positions) < MAX_CONCURRENT
            and opened_this_week < MAX_NEW_PER_WEEK
        )
        if can_trade and rng.random() < 0.35:   # a qualifying signal appears
            slots_free = MAX_CONCURRENT - len(open_positions)
            debit = min(MAX_RISK_PER_POSITION, cash / slots_free)
            if debit >= 20.0:
                cash -= debit
                friction = FRICTION_PCT * debit
                if rng.random() < hit_rate:
                    gross = debit * (1.0 + TARGET_MULT)
                else:
                    if rng.random() < GAP_PROB_GIVEN_LOSS:
                        gross = debit * (1.0 + GAP_MULT)
                    else:
                        gross = debit * (1.0 + STOP_MULT)
                payout = gross - friction
                open_positions.append(
                    [day + rng.randint(HOLD_MIN, HOLD_MAX), debit, payout])
                opened_this_week += 1

    for pos in open_positions:
        cash += pos[2]
    return max(0.0, core + cash)


def run_ratchet_corr(rng, hit_rate, rho):
    """RATCHET where concurrent trade outcomes are correlated by `rho`.

    rho=0.0  -> a diversified sleeve (independent underlyings)
    rho=0.85 -> a SPY-only sleeve: every position is the same directional bet
                on the same index, so they win and lose together.

    A persistent market factor M (AR(1), phi=0.95 daily, standard normal
    marginally) drives all outcomes through a Gaussian copula. Mean expectancy
    is unchanged by rho -- only the DISPERSION changes. That is the whole point:
    correlation does not cost you expected return, it costs you the ability to
    survive the bad draw.
    """
    nd = NormalDist()
    thresh = nd.inv_cdf(hit_rate)      # Z < thresh  => win
    phi = 0.95
    m = rng.gauss(0, 1)

    core = START_EQUITY * CORE_TARGET_PCT
    cash = START_EQUITY * CONVEXITY_PCT
    s0 = START_EQUITY * CONVEXITY_PCT
    hwm = START_EQUITY
    refilled_this_year = 0.0
    halt_until = -1
    open_positions = []
    opened_this_week = 0

    mu_d = CORE_MU_ANNUAL / 252.0
    sig_d = CORE_SIGMA_ANNUAL / math.sqrt(252.0)

    for day in range(SESSIONS):
        m = phi * m + math.sqrt(1 - phi ** 2) * rng.gauss(0, 1)
        core *= math.exp((mu_d - 0.5 * sig_d ** 2) + sig_d * rng.gauss(0, 1))

        still_open = []
        for pos in open_positions:
            if pos[0] <= day:
                debit, z_idio = pos[1], pos[2]
                z = rho * m + math.sqrt(1 - rho ** 2) * z_idio
                friction = FRICTION_PCT * debit
                if z < thresh:
                    gross = debit * (1.0 + TARGET_MULT)
                elif rng.random() < GAP_PROB_GIVEN_LOSS:
                    gross = debit * (1.0 + GAP_MULT)
                else:
                    gross = debit * (1.0 + STOP_MULT)
                cash += gross - friction
            else:
                still_open.append(pos)
        open_positions = still_open

        deployed = sum(p[1] for p in open_positions)
        equity = core + cash + deployed
        hwm = max(hwm, equity)

        if equity < hwm * (1.0 - DRAWDOWN_HALT) and day > halt_until:
            halt_until = day + HALT_SESSIONS

        if day % 5 == 4:
            opened_this_week = 0
            sleeve_value = cash + deployed
            if sleeve_value > s0:
                sweep = min(sleeve_value - s0, cash)
                core += sweep
                cash -= sweep
            elif sleeve_value < s0:
                want = s0 - sleeve_value
                amt = min(want,
                          REFILL_CAP_WEEKLY_PCT * max(equity, 0.0),
                          max(0.0, REFILL_CAP_ANNUAL_PCT * START_EQUITY
                              - refilled_this_year),
                          max(core, 0.0))
                core -= amt
                cash += amt
                refilled_this_year += amt

        if (day > halt_until and len(open_positions) < MAX_CONCURRENT
                and opened_this_week < MAX_NEW_PER_WEEK
                and rng.random() < 0.35):
            slots_free = MAX_CONCURRENT - len(open_positions)
            debit = min(MAX_RISK_PER_POSITION, cash / slots_free)
            if debit >= 20.0:
                cash -= debit
                open_positions.append(
                    [day + rng.randint(HOLD_MIN, HOLD_MAX), debit,
                     rng.gauss(0, 1)])
                opened_this_week += 1

    for pos in open_positions:
        debit, z_idio = pos[1], pos[2]
        z = rho * m + math.sqrt(1 - rho ** 2) * z_idio
        friction = FRICTION_PCT * debit
        if z < thresh:
            cash += debit * (1.0 + TARGET_MULT) - friction
        else:
            cash += debit * (1.0 + STOP_MULT) - friction
    return max(0.0, core + cash)


def run_doubler(rng, table=None):
    """One 252-session path of a full-size daily-doubling attempt."""
    table = table or DOUBLER_OUTCOMES
    equity = START_EQUITY
    for _ in range(SESSIONS):
        if equity < RUIN_FLOOR:
            return equity, True
        equity *= (1.0 + sample_outcome(rng, table))
        if equity < 0.01:
            return 0.0, True
    return equity, equity < RUIN_FLOOR


def pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] * (hi - k) + sorted_vals[hi] * (k - lo)


def summarize(name, finals, ruins=None):
    s = sorted(finals)
    n = len(s)
    ruin_ct = ruins if ruins is not None else sum(1 for v in s if v < RUIN_FLOOR)
    return {
        "name": name,
        "median": pct(s, 0.50),
        "p05": pct(s, 0.05),
        "p25": pct(s, 0.25),
        "p75": pct(s, 0.75),
        "p95": pct(s, 0.95),
        "mean": mean(s),
        "p_ruin": ruin_ct / n,
        "p_profit": sum(1 for v in s if v > START_EQUITY) / n,
        "p_double": sum(1 for v in s if v >= 2 * START_EQUITY) / n,
        "p_lose_half": sum(1 for v in s if v <= 0.5 * START_EQUITY) / n,
    }


def fmt(r):
    return (
        f"{r['name']:<28} "
        f"${r['median']:>9,.0f} "
        f"${r['mean']:>8,.0f} "
        f"${r['p05']:>9,.0f} "
        f"${r['p95']:>10,.0f} "
        f"{r['p_ruin']*100:>7.1f}% "
        f"{r['p_profit']*100:>8.1f}% "
        f"{r['p_double']*100:>8.1f}% "
        f"{r['p_lose_half']*100:>9.1f}%"
    )


def main():
    rng = random.Random(SEED)

    print("=" * 117)
    print("RATCHET v1.0 -- Monte Carlo".center(117))
    print(f"{PATHS:,} paths x {SESSIONS} sessions, starting from "
          f"${START_EQUITY:,.0f} (account ****8464)".center(117))
    print("=" * 117)
    print()
    print("Break-even hit rate check (2:1 payoff, 10% round-trip friction):")
    be = (0.5 + FRICTION_PCT) / (TARGET_MULT + 0.5)
    print(f"  win=+{TARGET_MULT*100:.0f}% of debit, loss=-{-STOP_MULT*100:.0f}% "
          f"of debit, friction={FRICTION_PCT*100:.0f}% of debit")
    print(f"  -> RATCHET needs a {be*100:.1f}% hit rate just to break even.")
    print(f"  -> Below {be*100:.1f}%, the convexity sleeve is a slow donation.")
    print()

    header = (f"{'Strategy':<28} {'median':>10} {'mean':>9} {'5th pct':>10} "
              f"{'95th pct':>11} {'P(ruin)':>8} {'P(profit)':>9} {'P(2x yr)':>9} "
              f"{'P(-50%)':>10}")
    print(header)
    print("-" * 117)

    results = []
    for hr in (0.35, 0.40, 0.45, 0.50, 0.55):
        finals = [run_ratchet(rng, hr) for _ in range(PATHS)]
        r = summarize(f"RATCHET @ {hr*100:.0f}% hit rate", finals, ruins=0)
        results.append(r)
        print(fmt(r))

    print("-" * 117)
    for label, table in (("'2x DAILY' held to expiry", DOUBLER_OUTCOMES),
                         ("'2x DAILY' WITH stop-loss", DOUBLER_STOPPED)):
        dbl = [run_doubler(rng, table) for _ in range(PATHS)]
        d_finals = [f for f, _ in dbl]
        d_ruins = sum(1 for _, ru in dbl if ru)
        print(fmt(summarize(label, d_finals, ruins=d_ruins)))
    print("=" * 117)
    print()

    # how fast each doubling variant dies
    for label, table in (("held to expiry", DOUBLER_OUTCOMES),
                         ("WITH -50% stop-loss", DOUBLER_STOPPED)):
        rng2 = random.Random(SEED + 1)
        deaths = []
        for _ in range(PATHS):
            eq = START_EQUITY
            for d in range(1, SESSIONS + 1):
                eq *= (1.0 + sample_outcome(rng2, table))
                if eq < RUIN_FLOOR:
                    deaths.append(d)
                    break
        ds = sorted(deaths)
        ev = sum(p * v for p, v in table)
        if any(1 + v <= 0 for _, v in table):
            # Any branch that returns -100% drives the geometric mean to -100%:
            # one occurrence is absorbing. Skipping the branch (log of zero)
            # would report a positive edge for a strategy that always ruins.
            geo_txt = "-100.0% (a total-loss branch is absorbing)"
        else:
            glog = sum(p * math.log(1 + v) for p, v in table)
            geo_txt = f"{(math.exp(glog) - 1) * 100:+.1f}%"
        print(f"Time to ruin, '2x daily' {label} "
              f"({len(deaths):,}/{PATHS:,} = {len(deaths)/PATHS*100:.2f}% died):")
        print(f"  arithmetic edge/trade : {ev*100:+.1f}%   "
              f"geometric edge/trade: {geo_txt}")
        print(f"  median time to ruin   : {pct(ds, 0.50):.0f} sessions "
              f"(~{pct(ds, 0.50)/21:.1f} months)")
        print(f"  25th / 75th pct       : {pct(ds, 0.25):.0f} / "
              f"{pct(ds, 0.75):.0f} sessions")
        print()

    print("The second variant is the important one. It uses disciplined stops,")
    print("never lets anything expire worthless, and has a roughly FLAT")
    print("arithmetic edge -- and it still goes to zero, because betting the")
    print("full account makes the geometric return deeply negative even when")
    print("the average trade is fine. That gap is volatility drag, and it is")
    print("what position sizing exists to defeat. It is the entire reason the")
    print("RATCHET convexity sleeve is capped at 30% and swept weekly.")
    print()
    print("=" * 117)
    print("SPY-ONLY: what correlation costs".center(117))
    print("=" * 117)
    print("Three positions on one index are not three bets. Same mean, worse")
    print("tail -- correlation is paid in survivability, not expected return.")
    print()
    print(f"{'Sleeve':<28} {'median':>10} {'mean':>9} {'5th pct':>10} "
          f"{'95th pct':>11} {'P(ruin)':>8} {'P(profit)':>9} {'P(2x yr)':>9} "
          f"{'P(-50%)':>10}")
    print("-" * 117)
    for label, rho in (("Diversified (rho=0.00)", 0.00),
                       ("SPY-only     (rho=0.85)", 0.85)):
        rngc = random.Random(SEED + 7)
        finals = [run_ratchet_corr(rngc, 0.45, rho) for _ in range(PATHS)]
        print(fmt(summarize(label, finals, ruins=0)))
    print("-" * 117)
    print()

    print("=" * 117)
    print("STRIKE-GRID FRICTION (live SPY 2026-10-16 quotes)".center(117))
    print("=" * 117)
    print("Max loss on a DEBIT vertical is the debit paid -- not the width.")
    print("So width is free to choose, and it should be chosen for LIQUIDITY.")
    print()
    grids = [
        ("785/790  ($5 grid)", 5.075, 3.625, 5.08, 3.62, 5.00, 26329),
        ("784/787  ($1 grid)", 5.470, 4.530, 5.52, 4.48, 3.00, 1873),
    ]
    print(f"{'Spread':<22} {'mid debit':>10} {'crossed':>9} {'slippage':>9} "
          f"{'% of debit':>11} {'max profit':>11} {'R:R':>7} {'comb. OI':>10}")
    print("-" * 117)
    for name, lm, sm, la, sb, width, oi in grids:
        mid = lm - sm
        crossed = la - sb
        slip = crossed - mid
        print(f"{name:<22} ${mid*100:>9,.2f} ${crossed*100:>8,.2f} "
              f"${slip*100:>8,.2f} {slip/mid*100:>10.1f}% "
              f"${(width-mid)*100:>10,.2f} {(width-mid)/mid:>6.2f}:1 "
              f"{oi:>10,}")
    print("-" * 117)
    print()
    print("Break-even hit rate = (0.50 + round-trip friction) / 1.50")
    for name, lm, sm, la, sb, width, oi in grids:
        rt = 2 * ((la - sb) - (lm - sm)) / (lm - sm)
        print(f"  {name:<22} round-trip {rt*100:>5.1f}% of debit "
              f"-> break-even hit rate {(0.50 + rt) / 1.50 * 100:>5.1f}%")
    print()
    print("Same signal, same account, same risk. Thirteen points of required")
    print("hit rate, decided entirely by which strike grid you trade. That is")
    print("larger than any edge the entry filters could plausibly supply.")
    print()
    print("NOTE: assumptions, not backtests. See the module docstring.")


if __name__ == "__main__":
    main()
