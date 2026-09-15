"""Small, original teaching models; no regulatory or production approval implied.

Amounts in each call must share one currency/unit. Rates and probabilities are
fractions (0.01 means 1%). No currency conversion or implicit annualisation occurs.
"""

import math
from numbers import Real


def _number(value, name, *, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number, not a boolean")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} must be representable as a finite float") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")
    return value


def _vector(values, name, **bounds):
    if isinstance(values, (str, bytes, dict)):
        raise ValueError(f"{name} must be a nonempty sequence of numbers")
    try:
        result = [_number(v, f"{name}[{i}]", **bounds) for i, v in enumerate(values)]
    except TypeError as exc:
        raise ValueError(f"{name} must be a nonempty sequence of numbers") from exc
    if not result:
        raise ValueError(f"{name} must not be empty")
    return result


def _same_length(*vectors):
    if len({len(v) for v in vectors}) != 1:
        raise ValueError("all input sequences must have the same length")


def _finite_result(value):
    if not math.isfinite(value):
        raise ValueError("inputs produce an unrepresentable numerical result")
    return value


def _product(*values):
    """Avoid losing a small factor before multiplication by a large exposure."""
    if any(v == 0 for v in values):
        return 0.0
    parts = [math.frexp(v) for v in values]
    try:
        result = math.ldexp(math.prod(m for m, _ in parts), sum(e for _, e in parts))
    except OverflowError as exc:
        raise ValueError("numerical product is not representable") from exc
    if result == 0:
        raise ValueError("numerical product underflows; inputs exceed floating-point resolution")
    return _finite_result(result)


def _sum(values):
    try:
        return _finite_result(math.fsum(values))
    except OverflowError as exc:
        raise ValueError("numerical total is not representable") from exc


def _discount(rate, year):
    try:
        factor = math.exp(-year * math.log1p(rate))
    except OverflowError as exc:
        raise ValueError("discount factor is not representable") from exc
    if factor == 0:
        raise ValueError("discount factor underflows; reduce rate or horizon")
    return _finite_result(factor)


def simplified_ecl(conditional_pds, lgds, eads, effective_annual_rate, *,
                   default_window_years=None):
    """Annual end-of-year expected-loss proxy, in the EAD currency.

    PD[t] is default probability conditional on survival to year t. Marginal PD
    equals prior survival times conditional PD. LGD and EAD are year-specific
    fractions and amounts. The effective annual rate discounts each proxy loss
    to time zero. A window of 1 includes first-year defaults; None includes all
    supplied years. Each LGD must represent the full lifetime loss conditional on
    default in that year. This proxy places that entire loss at the default-year
    end, without a post-default recovery schedule. A one-year default window is
    NOT a truncation of cash shortfalls to twelve months. This is not a complete
    IFRS 9 calculation and does not assign Stage 1/2/3 or implement SICR policy.
    """
    pds = _vector(conditional_pds, "conditional_pds", minimum=0, maximum=1)
    losses = _vector(lgds, "lgds", minimum=0, maximum=1)
    exposures = _vector(eads, "eads", minimum=0)
    _same_length(pds, losses, exposures)
    rate = _number(effective_annual_rate, "effective_annual_rate")
    if rate <= -1:
        raise ValueError("effective_annual_rate must be > -1")
    window = len(pds) if default_window_years is None else default_window_years
    if isinstance(window, bool) or not isinstance(window, int) or not 1 <= window <= len(pds):
        raise ValueError("default_window_years must be an integer within the supplied horizon")
    survival = 1.0
    rows = []
    for i in range(window):
        marginal = _product(survival, pds[i])
        factor = _discount(rate, i + 1)
        loss = _product(marginal, losses[i], exposures[i], factor)
        rows.append({"year": i + 1, "conditional_pd": pds[i],
                     "survival_before": survival, "marginal_pd": marginal,
                     "lgd": losses[i], "ead": exposures[i],
                     "discount_factor": factor, "discounted_loss": loss})
        survival = _product(survival, 1 - pds[i])
    return {"ecl": _sum(r["discounted_loss"] for r in rows),
            "default_window_years": window, "supplied_horizon_years": len(pds),
            "cumulative_default_probability": math.fsum(r["marginal_pd"] for r in rows),
            "survival_at_window_end": survival, "annual_results": rows}


def weighted_scenario_ecl(scenario_ecls, weights):
    """Weight same-currency, same-horizon scenario ECL amounts.

    Weights must total 1 within absolute 1e-12; accepted rounding is normalised
    explicitly. Scenarios must represent mutually exclusive outcomes; the caller
    must ensure common horizon, valuation date and methodology.
    """
    amounts = _vector(scenario_ecls, "scenario_ecls", minimum=0)
    probabilities = _vector(weights, "weights", minimum=0, maximum=1)
    _same_length(amounts, probabilities)
    total = math.fsum(probabilities)
    if not math.isclose(total, 1, rel_tol=0, abs_tol=1e-12):
        raise ValueError("weights must sum to 1 within absolute tolerance 1e-12")
    normalized = [w / total for w in probabilities]
    return {"weighted_ecl": _sum(a * w for a, w in zip(amounts, normalized)),
            "scenario_ecls": amounts, "input_weights": probabilities,
            "normalized_weights": normalized}


def liquidity_runway(initial_cash, daily_inflows, daily_outflows, *, daily_realizable_cash=None):
    """End-of-day cash path; additional realised proceeds must be declared by day.

    Inputs are same-currency cash amounts. Realizable cash means proceeds actually
    available that day, already net of haircuts/costs, and not counted in inflows.
    No intraday ordering, execution guarantee, borrowing or LCR calculation is
    implied. An ending balance of exactly zero is not classified as negative.
    """
    balance = _number(initial_cash, "initial_cash", minimum=0)
    inflows = _vector(daily_inflows, "daily_inflows", minimum=0)
    outflows = _vector(daily_outflows, "daily_outflows", minimum=0)
    proceeds = ([0.0] * len(inflows) if daily_realizable_cash is None else
                _vector(daily_realizable_cash, "daily_realizable_cash", minimum=0))
    _same_length(inflows, outflows, proceeds)
    rows, first_negative = [], None
    for day, (incoming, outgoing, realized) in enumerate(zip(inflows, outflows, proceeds), 1):
        opening = balance
        try:
            balance = _finite_result(math.fsum([opening, incoming, realized, -outgoing]))
        except OverflowError as exc:
            raise ValueError("cash balance is not representable") from exc
        if balance < 0 and first_negative is None:
            first_negative = day
        rows.append({"day": day, "opening_cash": opening, "inflow": incoming,
                     "outflow": outgoing, "realized_cash": realized, "closing_cash": balance})
    return {"first_negative_day": first_negative, "ending_cash": balance,
            "minimum_closing_cash": min(r["closing_cash"] for r in rows), "daily_results": rows}


def fixed_cashflow_rate_shock(cashflows, years, base_annual_rate, parallel_shock):
    """Fixed annual cashflow PV under a flat effective annual rate and additive shock.

    Years are strictly increasing positive integers; cashflows may be signed.
    Shock 0.01 means +100 basis points. Both rates must exceed -1. This holds cash
    flows fixed and omits optionality, behavioural NMD assumptions, repricing and
    curve shape changes. It values the supplied leg of fixed cash flows, not a
    net asset/liability EVE or NII calculation and not a complete IRRBB model.
    """
    amounts = _vector(cashflows, "cashflows")
    times = _vector(years, "years", minimum=1)
    _same_length(amounts, times)
    if any(not t.is_integer() for t in times) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("years must be strictly increasing positive whole years")
    rate = _number(base_annual_rate, "base_annual_rate")
    shock = _number(parallel_shock, "parallel_shock")
    shocked = _finite_result(rate + shock)
    if rate <= -1 or shocked <= -1:
        raise ValueError("base and shocked effective annual rates must both be > -1")
    rows = []
    for amount, year in zip(amounts, times):
        rows.append({"year": int(year), "cashflow": amount,
                     "base_pv": _finite_result(amount * _discount(rate, year)),
                     "shocked_pv": _finite_result(amount * _discount(shocked, year))})
    try:
        base_pv = _finite_result(math.fsum(r["base_pv"] for r in rows))
        shocked_pv = _finite_result(math.fsum(r["shocked_pv"] for r in rows))
    except OverflowError as exc:
        raise ValueError("present value total is not representable") from exc
    return {"base_annual_rate": rate, "shocked_annual_rate": shocked,
            "base_pv": base_pv, "shocked_pv": shocked_pv,
            "delta_pv": _finite_result(shocked_pv - base_pv), "cashflow_results": rows}


def exposure_concentration(exposures):
    """Gross nonnegative exposure shares, HHI (0..1) and effective entity count.

    Supply one already-aggregated exposure per intended entity/group. No netting,
    credit conversion, correlation or loss-risk inference is performed. Zero
    total exposure yields explicitly undefined (None) shares and metrics.
    """
    amounts = _vector(exposures, "exposures", minimum=0)
    try:
        total = _finite_result(math.fsum(amounts))
    except OverflowError as exc:
        raise ValueError("total exposure is not representable") from exc
    if total == 0:
        return {"total_exposure": 0.0, "shares": None, "hhi": None,
                "top_share": None, "effective_count": None}
    shares = [a / total for a in amounts]
    hhi = math.fsum(s * s for s in shares)
    return {"total_exposure": total, "shares": shares, "hhi": hhi,
            "top_share": max(shares), "effective_count": 1 / hhi}
