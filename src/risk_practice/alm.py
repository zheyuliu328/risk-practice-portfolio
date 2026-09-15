"""Explicit annual ALM/NMD teaching assumptions, without fitted behaviour."""

import math

from .models import _discount, _finite_result, _number, _product, _sum, _vector


LIMITS = [
    "One currency; annual end-of-year coupons, deposit interest and runoff. No intraday timing.",
    "Asset is a fixed-rate bullet loan/bond held unchanged. Deposit rates reprice immediately and remain flat in each run.",
    "Core/noncore shares, runoff weights, beta and deposit-rate floor are caller assumptions, not behaviour estimates.",
    "First-year NII uses opening balances for the whole year; year-end runoff is not reinvested or replaced.",
    "Net EVE proxy is asset PV minus deposit-liability PV. NII is undiscounted first-year interest income minus interest cost.",
    "No optionality, prepayment, new business, credit losses, curve twists, hedges or regulatory shock calibration; not complete IRRBB.",
]


def _weights(values, name):
    values = _vector(values, name, minimum=0, maximum=1)
    if len(values) > 50:
        raise ValueError(f"{name} horizon must be at most 50 years")
    total = _sum(values)
    if not math.isclose(total, 1, rel_tol=0, abs_tol=1e-12):
        raise ValueError(f"{name} must sum to 1 within absolute tolerance 1e-12")
    return values, [v / total for v in values]


def alm_nmd(asset_principal, asset_coupon_rate, asset_maturity_years,
            deposit_principal, base_deposit_rate, base_discount_rate,
            rate_shock, scenarios):
    """Value a fixed-rate bullet asset against explicitly amortising deposits.

    Every scenario specifies name, core_fraction, core_runoff_weights,
    noncore_runoff_weights, deposit_beta and deposit_rate_floor (number or None).
    Weights allocate each segment's initial principal across annual repayments.
    Interest uses opening principal; first-year NII therefore has no runoff effect.
    All annual rates/shocks are fractions. A floor applies to both baseline and
    shocked deposit rates. Beta is constrained to [0, 1] for this teaching case.
    """
    asset = _number(asset_principal, "asset_principal", minimum=0)
    coupon = _number(asset_coupon_rate, "asset_coupon_rate", minimum=0)
    deposit = _number(deposit_principal, "deposit_principal", minimum=0)
    dep_rate = _number(base_deposit_rate, "base_deposit_rate")
    discount = _number(base_discount_rate, "base_discount_rate")
    shock = _number(rate_shock, "rate_shock")
    shocked_discount = _finite_result(discount + shock)
    if discount <= -1 or shocked_discount <= -1:
        raise ValueError("base and shocked discount rates must exceed -1")
    if isinstance(asset_maturity_years, bool) or not isinstance(asset_maturity_years, int) or not 1 <= asset_maturity_years <= 50:
        raise ValueError("asset_maturity_years must be an integer from 1 to 50")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios must be a nonempty list")
    names, results = set(), []
    required = {"name", "core_fraction", "core_runoff_weights", "noncore_runoff_weights", "deposit_beta", "deposit_rate_floor"}
    income = _product(asset, coupon)
    for config in scenarios:
        if not isinstance(config, dict) or set(config) != required:
            raise ValueError("each scenario must contain exactly the documented fields")
        name = config["name"]
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("scenario names must be unique nonempty strings")
        names.add(name)
        core = _number(config["core_fraction"], "core_fraction", minimum=0, maximum=1)
        beta = _number(config["deposit_beta"], "deposit_beta", minimum=0, maximum=1)
        floor = config["deposit_rate_floor"]
        if floor is not None:
            floor = _number(floor, "deposit_rate_floor")
        raw_core, core_w = _weights(config["core_runoff_weights"], "core_runoff_weights")
        raw_noncore, noncore_w = _weights(config["noncore_runoff_weights"], "noncore_runoff_weights")
        horizon = max(asset_maturity_years, len(core_w), len(noncore_w))
        # Allocate independently declared segment principal. Last repayment takes
        # the rounding residual, preserving total principal across the schedule.
        segment_rows = []
        for fraction, weights in [(core, core_w), (1 - core, noncore_w)]:
            principal = _product(deposit, fraction)
            paid = [_product(principal, w) for w in weights[:-1]]
            last = _finite_result(principal - _sum(paid))
            if last < 0:
                raise ValueError("runoff rounding creates negative residual; revise weights")
            segment_rows.append(paid + [last] + [0.0] * (horizon - len(weights)))
        repayments = [_sum([segment_rows[0][i], segment_rows[1][i]]) for i in range(horizon)]
        if not math.isclose(_sum(repayments), deposit, rel_tol=1e-12, abs_tol=0):
            raise ValueError("deposit principal conservation failed")
        raw_shocked = _finite_result(dep_rate + _product(beta, shock))
        base_cost_rate = dep_rate if floor is None else max(floor, dep_rate)
        shocked_cost_rate = raw_shocked if floor is None else max(floor, raw_shocked)
        opening, rows = deposit, []
        for i in range(horizon):
            year = i + 1
            asset_cf = _sum([income if year <= asset_maturity_years else 0,
                             asset if year == asset_maturity_years else 0])
            closing = _sum(repayments[i + 1:])
            base_interest = _product(opening, base_cost_rate)
            shocked_interest = _product(opening, shocked_cost_rate)
            base_liability_cf = _sum([repayments[i], base_interest])
            shocked_liability_cf = _sum([repayments[i], shocked_interest])
            bd, sd = _discount(discount, year), _discount(shocked_discount, year)
            rows.append({"year": year, "opening_deposits": opening,
                         "core_principal_repayment": segment_rows[0][i],
                         "noncore_principal_repayment": segment_rows[1][i],
                         "principal_repayment": repayments[i], "closing_deposits": closing,
                         "asset_cashflow": asset_cf, "base_deposit_interest": base_interest,
                         "shocked_deposit_interest": shocked_interest,
                         "base_liability_cashflow": base_liability_cf,
                         "shocked_liability_cashflow": shocked_liability_cf,
                         "base_asset_pv": _product(asset_cf, bd),
                         "shocked_asset_pv": _product(asset_cf, sd),
                         "base_liability_pv": _product(base_liability_cf, bd),
                         "shocked_liability_pv": _product(shocked_liability_cf, sd)})
            opening = closing
        base_apv = _sum(row["base_asset_pv"] for row in rows)
        shock_apv = _sum(row["shocked_asset_pv"] for row in rows)
        base_lpv = _sum(row["base_liability_pv"] for row in rows)
        shock_lpv = _sum(row["shocked_liability_pv"] for row in rows)
        base_eve = _sum([base_apv, -base_lpv])
        shock_eve = _sum([shock_apv, -shock_lpv])
        base_nii = _sum([income, -rows[0]["base_deposit_interest"]])
        shock_nii = _sum([income, -rows[0]["shocked_deposit_interest"]])
        results.append({"name": name, "declared_core_fraction": core,
                        "input_core_runoff_weights": raw_core, "normalized_core_runoff_weights": core_w,
                        "input_noncore_runoff_weights": raw_noncore, "normalized_noncore_runoff_weights": noncore_w,
                        "deposit_beta": beta, "deposit_rate_floor": floor,
                        "base_deposit_rate_after_floor": base_cost_rate,
                        "shocked_deposit_rate_before_floor": raw_shocked,
                        "shocked_deposit_rate_after_floor": shocked_cost_rate,
                        "principal_repaid": _sum(repayments), "final_deposits": rows[-1]["closing_deposits"],
                        "base_asset_pv": base_apv, "shocked_asset_pv": shock_apv,
                        "base_liability_pv": base_lpv, "shocked_liability_pv": shock_lpv,
                        "base_net_eve_proxy": base_eve, "shocked_net_eve_proxy": shock_eve,
                        "delta_net_eve_proxy": _sum([shock_eve, -base_eve]),
                        "base_12month_nii_proxy": base_nii, "shocked_12month_nii_proxy": shock_nii,
                        "delta_12month_nii_proxy": _sum([shock_nii, -base_nii]),
                        "annual_results": rows})
    return {"currency_unit": "one caller-declared common currency/unit",
            "asset_principal": asset, "asset_coupon_rate": coupon,
            "asset_maturity_years": asset_maturity_years, "asset_repricing_fraction": 0,
            "deposit_principal": deposit, "base_discount_rate": discount,
            "shocked_discount_rate": shocked_discount, "rate_shock": shock,
            "assumptions_and_limits": LIMITS, "scenario_results": results}
