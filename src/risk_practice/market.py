"""Original single-currency teaching workflows; no capital or approval inference."""

from .models import _finite_result, _number, _product, _sum, _vector, exposure_concentration


def _name(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    if value != value.strip():
        raise ValueError(f"{field} must not have surrounding whitespace")
    return value


def _confidence(value):
    value = _number(value, "confidence")
    if not 0 < value < 1:
        raise ValueError("confidence must be strictly between zero and one")
    return value


def _quantile(values, confidence):
    """Left-continuous inverse empirical CDF: order statistic ceil(n * c)."""
    ordered = sorted(values)
    # Compare CDF masses directly: n * (k/n) may round just above integer k.
    return next(value for rank, value in enumerate(ordered, 1)
                if rank / len(ordered) >= confidence)


def historical_var_es(losses, confidence, stress_losses):
    """Nonnegative losses, equally weighted observations, no annualisation.

    VaR is inf{x:F_n(x)>=confidence}. ES integrates this empirical quantile
    over (confidence,1), including only the required fraction of the cutoff
    observation. Named stress amounts are separate deterministic scenarios,
    not extra observations and not probabilistic forecasts.
    """
    values = _vector(losses, "losses", minimum=0)
    confidence = _confidence(confidence)
    if not isinstance(stress_losses, dict) or not stress_losses:
        raise ValueError("stress_losses must be a nonempty mapping of names to losses")
    stresses = []
    for name, amount in stress_losses.items():
        stresses.append({"scenario": _name(name, "stress name"),
                         "loss": _number(amount, f"stress_losses[{name}]", minimum=0)})
    tail_mass = len(values) * (1 - confidence)
    rows = []
    for rank, loss in enumerate(sorted(values, reverse=True)):
        mass = max(0.0, min(1.0, tail_mass - rank))
        rows.append({"descending_rank": rank + 1, "loss": loss,
                     "observation_mass_in_tail": mass,
                     "normalized_tail_weight": mass / tail_mass})
    es = _sum(_product(r["loss"], r["normalized_tail_weight"]) for r in rows)
    return {"confidence": confidence, "observations": len(values),
            "var": _quantile(values, confidence), "es": es,
            "tail_observation_mass": tail_mass, "tail_evidence": rows,
            "stress_results": stresses,
            "notes": ["VaR uses the inverse empirical CDF; ES uses fractional tail mass.",
                      "Input contains nonnegative losses, not signed returns or P&L.",
                      "No out-of-sample backtest or independence test is performed.",
                      "Named stresses are not assigned probabilities; this is not FRTB capital."],
            "human_review": ["Check holding period, position scope and loss units.",
                             "Assess clustered losses and stress severity before setting limits."]}


def _matrix(value, name):
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError(f"{name} must be a nonempty path-by-time matrix")
    result = [_vector(row, f"{name}[{i}]") for i, row in enumerate(value)]
    if len({len(row) for row in result}) != 1:
        raise ValueError(f"{name} must be rectangular")
    return result


def counterparty_exposure(mtm_paths, collateral_available, discount_factors,
                          conditional_pds, lgd, legal_netting_set, confidence=0.95):
    """Equally weighted, time-aligned net MTM paths for one declared netting set.

    Collateral is nonnegative available received collateral, already adjusted for
    timing, eligibility and haircuts. The caller supplies delayed/stressed paths;
    this function does not simulate CSA rules. Positive exposure is max(MTM-C,0).
    CVA uses period-end EE times marginal default probability, discount and LGD,
    assuming default independent of exposure and constant LGD. PD is conditional
    on survival over each corresponding period, not an annual rate.
    """
    name = _name(legal_netting_set, "legal_netting_set")
    paths = _matrix(mtm_paths, "mtm_paths")
    collateral = _matrix(collateral_available, "collateral_available")
    if len(paths) != len(collateral) or len(paths[0]) != len(collateral[0]):
        raise ValueError("collateral_available must have the same shape as mtm_paths")
    if any(v < 0 for row in collateral for v in row):
        raise ValueError("collateral_available must be nonnegative")
    discounts = _vector(discount_factors, "discount_factors", minimum=0)
    if any(d == 0 for d in discounts):
        raise ValueError("discount_factors must be positive")
    pds = _vector(conditional_pds, "conditional_pds", minimum=0, maximum=1)
    if len(discounts) != len(paths[0]) or len(pds) != len(paths[0]):
        raise ValueError("discount_factors and conditional_pds must match time dimension")
    lgd = _number(lgd, "lgd", minimum=0, maximum=1)
    confidence = _confidence(confidence)
    evidence = []
    for i, (path, coll) in enumerate(zip(paths, collateral)):
        for t, (mtm, received) in enumerate(zip(path, coll)):
            evidence.append({"path": i + 1, "period": t + 1, "net_mtm": mtm,
                             "available_collateral": received,
                             "positive_exposure": max(_finite_result(mtm - received), 0)})
    rows, survival = [], 1.0
    for t, (discount, pd) in enumerate(zip(discounts, pds)):
        exposures = [r["positive_exposure"] for r in evidence if r["period"] == t + 1]
        ee = _sum(v / len(paths) for v in exposures)
        marginal = _product(survival, pd)
        rows.append({"period": t + 1, "ee": ee, "pfe": _quantile(exposures, confidence),
                     "survival_before": survival, "conditional_pd": pd, "marginal_pd": marginal,
                     "discount_factor": discount, "cva_contribution": _product(ee, marginal, lgd, discount)})
        survival = _product(survival, 1 - pd)
    return {"legal_netting_set": name, "pfe_confidence": confidence,
            "independent_cva": _sum(r["cva_contribution"] for r in rows),
            "period_results": rows, "path_evidence": evidence,
            "notes": ["Legal enforceability of the declared netting set is not verified.",
                      "CVA assumes default independent of exposure; wrong-way risk is omitted.",
                      "Equal path weights and period-end exposure approximation; not SA-CCR or regulatory capital.",
                      "Collateral paths must already reflect margin lag; calls are not received collateral.",
                      "Own default, funding, initial margin, collateral return exposure and closeout mechanics are omitted."],
            "human_review": ["Validate enforceable netting, collateral availability and simulation measure.",
                             "Run delayed-collateral and wrong-way stress scenarios before granting limits."]}


def broker_margin(loan, securities, currency):
    """One borrower, same-currency collateral; deterministic financing stress.

    Haircut affects lending value. Realizable fraction affects stressed sale
    proceeds separately: it is not multiplied by the lending haircut. Proceeds
    assume the supplied fraction is cash actually available, net of costs, by
    the chosen horizon. There is no cross-currency conversion or FRR calculation.
    """
    currency = _name(currency, "currency")
    loan = _number(loan, "loan", minimum=0)
    if not isinstance(securities, (list, tuple)) or not securities:
        raise ValueError("securities must be a nonempty list")
    fields = {"security_id", "issuer", "currency", "quantity", "price", "haircut", "stress_return", "realizable_fraction"}
    seen, rows, issuers = set(), [], {}
    for record in securities:
        if not isinstance(record, dict) or set(record) != fields:
            raise ValueError("each security must contain exactly the declared security fields")
        key = _name(record["security_id"], "security_id")
        if key in seen:
            raise ValueError("security_id must be unique; aggregate lots explicitly")
        seen.add(key)
        issuer = _name(record["issuer"], "issuer")
        if record["currency"] != currency:
            raise ValueError("all securities must share the loan currency")
        q = _number(record["quantity"], "quantity", minimum=0)
        price = _number(record["price"], "price", minimum=0)
        haircut = _number(record["haircut"], "haircut", minimum=0, maximum=1)
        shock = _number(record["stress_return"], "stress_return", minimum=-1)
        fraction = _number(record["realizable_fraction"], "realizable_fraction", minimum=0, maximum=1)
        market = _product(q, price)
        stressed = _product(market, _finite_result(1 + shock))
        rows.append({"security_id": key, "issuer": issuer, "market_value": market,
                     "baseline_lending_value": _product(market, 1 - haircut),
                     "stressed_market_value": stressed,
                     "stressed_lending_value": _product(stressed, 1 - haircut),
                     "stressed_realizable_proceeds": _product(stressed, fraction)})
        issuers.setdefault(issuer, []).append(market)
    groups = [{"issuer": name, "baseline_market_value": _sum(values)} for name, values in sorted(issuers.items())]
    concentration = exposure_concentration([r["baseline_market_value"] for r in groups])
    for i, group in enumerate(groups):
        group["share"] = None if concentration["shares"] is None else concentration["shares"][i]
    baseline = _sum(r["baseline_lending_value"] for r in rows)
    stressed = _sum(r["stressed_lending_value"] for r in rows)
    proceeds = _sum(r["stressed_realizable_proceeds"] for r in rows)
    return {"currency": currency, "loan": loan, "baseline_collateral": baseline,
            "stressed_collateral": stressed, "baseline_margin_shortfall": max(loan - baseline, 0),
            "stressed_margin_shortfall": max(loan - stressed, 0),
            "stressed_realizable_proceeds": proceeds, "realizable_proceeds_gap": max(loan - proceeds, 0),
            "security_evidence": rows, "issuer_results": groups, "issuer_concentration": concentration,
            "notes": ["Margin shortfall is a required call, not received cash.",
                      "Haircuts affect lending values; realizable fractions affect liquidation cash separately.",
                      "Single borrower, same currency, fixed loan; not FRR liquid capital or an execution instruction.",
                      "Concentration uses baseline gross market value and caller-supplied issuer grouping."],
            "human_review": ["Review connected issuers, suspension risk and borrower repayment ability.",
                             "Assess timing and authority before calls, financing restrictions or liquidation."]}
