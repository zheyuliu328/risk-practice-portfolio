"""Original credit review exercises with explicit labels and attribution limits."""

import copy
import datetime
import re

from .models import _number, _sum, _discount, simplified_ecl, weighted_scenario_ecl


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _boolean(value, name):
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


def _records(value, name):
    if not isinstance(value, list) or not value or any(not isinstance(r, dict) for r in value):
        raise ValueError(f"{name} must be a nonempty list of objects")
    return value


def _pd_metrics(rows):
    if not rows:
        return {"count": 0, "default_count": 0, "mean_predicted_pd": None,
                "observed_default_rate": None, "calibration_gap_observed_minus_predicted": None,
                "brier_score": None, "auc": None}
    positives = [r for r in rows if r["defaulted"]]
    negatives = [r for r in rows if not r["defaulted"]]
    # Pairwise definition is transparent for small teaching samples, O(n^2).
    auc = None
    if positives and negatives:
        wins = _sum(1 if p["predicted_pd"] > n["predicted_pd"] else
                    .5 if p["predicted_pd"] == n["predicted_pd"] else 0
                    for p in positives for n in negatives)
        auc = wins / (len(positives) * len(negatives))
    predicted = _sum(r["predicted_pd"] for r in rows) / len(rows)
    observed = len(positives) / len(rows)
    return {"count": len(rows), "default_count": len(positives),
            "mean_predicted_pd": predicted, "observed_default_rate": observed,
            "calibration_gap_observed_minus_predicted": observed - predicted,
            "brier_score": _sum((r["predicted_pd"] - int(r["defaulted"])) ** 2 for r in rows) / len(rows),
            "auc": auc}


def credit_parameter_review(records, *, observation_horizon_months=12):
    """Review fixed-horizon PD predictions, using only mature, available labels.

    Each record requires id, predicted_pd, defaulted (bool or None), label_mature
    (bool), exposure (nonnegative), and group (string). The caller declares one
    common horizon and independently observed labels, with one independent unit
    per record. Exposures are shown but do not weight borrower-level PD metrics.
    """
    if (isinstance(observation_horizon_months, bool) or not isinstance(observation_horizon_months, int)
            or observation_horizon_months <= 0):
        raise ValueError("observation_horizon_months must be a positive integer")
    result, seen = [], set()
    for raw in _records(records, "records"):
        required = {"id", "predicted_pd", "defaulted", "label_mature", "exposure", "group"}
        if not required <= raw.keys():
            raise ValueError(f"record requires {sorted(required)}")
        identity = _text(raw["id"], "id")
        if identity in seen:
            raise ValueError("duplicate record id")
        seen.add(identity)
        label = raw["defaulted"]
        if label is not None:
            _boolean(label, "defaulted")
        mature = _boolean(raw["label_mature"], "label_mature")
        reason = "immature_horizon" if not mature else "missing_label" if label is None else None
        result.append({"id": identity, "predicted_pd": _number(raw["predicted_pd"], "predicted_pd", minimum=0, maximum=1),
                       "defaulted": label, "label_mature": mature,
                       "exposure": _number(raw["exposure"], "exposure", minimum=0),
                       "group": _text(raw["group"], "group"), "eligible": reason is None,
                       "exclusion_reason": reason})
    eligible = [r for r in result if r["eligible"]]
    grouped = []
    for group in sorted({r["group"] for r in result}):
        members = [r for r in result if r["group"] == group]
        grouped.append({"group": group, "total_records": len(members),
                        "excluded_records": sum(not r["eligible"] for r in members),
                        "metrics": _pd_metrics([r for r in members if r["eligible"]])})
    actions = ["Review sample representativeness, horizon alignment and economic causes before any model decision."]
    if len(eligible) != len(result):
        actions.append("Resolve missing labels and wait for immature horizons; excluded observations may bias the remaining sample.")
    if not eligible or _pd_metrics(eligible)["auc"] is None:
        actions.append("Discrimination is undefined without both mature defaults and non-defaults.")
    return {"observation_horizon_months": observation_horizon_months,
            "metrics": _pd_metrics(eligible), "grouped_results": grouped,
            "label_integrity": {"total": len(result), "eligible": len(eligible),
                                "immature": sum(not r["label_mature"] for r in result),
                                "missing_label": sum(r["defaulted"] is None for r in result)},
            "records": result, "action_needed": actions,
            "assumptions_and_limits": ["Independent, same-horizon observations and predictions fixed before outcomes are caller obligations.",
                                       "Mature available labels only; unweighted borrower-level calibration is not a lending or model approval.",
                                       "Small-sample descriptive metrics have no confidence intervals; repeated borrowers and censoring need additional treatment.",
                                       "AUC uses default as the positive class, high PD as high risk, and half credit for ties."]}


def recovery_lgd(default_ead, cashflows, effective_annual_rate, *, workout_complete):
    """Discount recovery and direct workout costs to default time; never clip LGD.

    cashflows: list of {year, recovery, cost}. Year is time since default in years,
    may be fractional or zero, and must increase strictly. All cash amounts share
    one currency. Incomplete workouts return provisional rather than final LGD.
    """
    ead = _number(default_ead, "default_ead", minimum=0)
    if ead == 0:
        raise ValueError("default_ead must be positive")
    rate = _number(effective_annual_rate, "effective_annual_rate")
    if rate <= -1:
        raise ValueError("effective_annual_rate must be > -1")
    complete = _boolean(workout_complete, "workout_complete")
    rows, previous = [], -1
    for raw in _records(cashflows, "cashflows"):
        if not {"year", "recovery", "cost"} <= raw.keys():
            raise ValueError("cashflow requires year, recovery and cost")
        year = _number(raw["year"], "year", minimum=0)
        if year <= previous:
            raise ValueError("cashflow years must increase strictly; aggregate same-time flows")
        previous = year
        recovery = _number(raw["recovery"], "recovery", minimum=0)
        cost = _number(raw["cost"], "cost", minimum=0)
        discounted = _number((recovery - cost) * _discount(rate, year), "discounted_net_recovery")
        rows.append({"year": year, "recovery": recovery, "cost": cost, "discounted_net_recovery": discounted})
    present_value = _sum(r["discounted_net_recovery"] for r in rows)
    lgd = _number(1 - present_value / ead, "lgd")
    actions = ["Reconcile recoveries/costs and justify discount rate, collateral realization and workout status."]
    if not complete:
        actions.append("Workout is incomplete: observed LGD is provisional and omitted future recoveries/costs must be assessed.")
    if not 0 <= lgd <= 1:
        actions.append("LGD is outside [0,1]; investigate excess recoveries or costs rather than silently clipping.")
    return {"default_ead": ead, "discounted_net_recovery": present_value,
            "observed_lgd": lgd, "workout_complete": complete, "final_lgd": lgd if complete else None,
            "records": rows, "action_needed": actions,
            "assumptions_and_limits": ["Default-time valuation in one currency; net cash recoveries are supplied explicitly.",
                                       "Observed workout arithmetic is not a calibrated downturn LGD, accounting approval or population estimate."]}


def ead_from_utilization(drawn, undrawn, ccf):
    """Teaching exposure = drawn + stated CCF times eligible undrawn commitment."""
    drawn = _number(drawn, "drawn", minimum=0)
    undrawn = _number(undrawn, "undrawn", minimum=0)
    ccf = _number(ccf, "ccf", minimum=0, maximum=1)
    amount = _sum([drawn, ccf * undrawn])
    return {"ead": amount, "records": [{"drawn": drawn, "undrawn": undrawn, "ccf": ccf}],
            "action_needed": ["Verify facility limits, cancellability, utilization history and CCF suitability before use."],
            "assumptions_and_limits": ["One still-outstanding commitment, one currency; drawn and undrawn do not overlap.",
                                       "CCF is a supplied teaching assumption in [0,1], not a regulatory factor or calibrated default-time utilization model.",
                                       "Settled facilities, accrued interest, future limit changes and over-limit drawings require separate treatment."]}


def _snapshot(raw):
    if not isinstance(raw, dict):
        raise ValueError("snapshot must be an object")
    required = {"report_date", "entity_id", "currency", "effective_annual_rate", "default_window_years", "sicr_flag", "scenarios"}
    if not required <= raw.keys():
        raise ValueError(f"snapshot requires {sorted(required)}")
    date = raw["report_date"]
    if not isinstance(date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("report_date must be YYYY-MM-DD")
    datetime.date.fromisoformat(date)
    window = raw["default_window_years"]
    if isinstance(window, bool) or not isinstance(window, int) or not 1 <= window <= 3:
        raise ValueError("default_window_years must explicitly be 1, 2 or 3")
    result = {"report_date": date, "entity_id": _text(raw["entity_id"], "entity_id"),
              "currency": _text(raw["currency"], "currency"),
              "effective_annual_rate": _number(raw["effective_annual_rate"], "effective_annual_rate"),
              "default_window_years": window,
              "sicr_flag": _boolean(raw["sicr_flag"], "sicr_flag"), "scenarios": {}}
    for scenario in _records(raw["scenarios"], "scenarios"):
        if not {"name", "weight", "conditional_pds", "lgds", "eads"} <= scenario.keys():
            raise ValueError("scenario requires name, weight, conditional_pds, lgds and eads")
        name = _text(scenario["name"], "name")
        if name in result["scenarios"]:
            raise ValueError("duplicate scenario name")
        for field in ("conditional_pds", "lgds", "eads"):
            if not isinstance(scenario[field], list) or len(scenario[field]) != 3:
                raise ValueError("each scenario must supply three annual PD, LGD and EAD values")
        result["scenarios"][name] = copy.deepcopy(scenario)
    _snapshot_value(result)  # Validate every vector, probability and weight.
    return result


def _snapshot_value(state):
    amounts, weights, records = [], [], []
    for name in sorted(state["scenarios"]):
        scenario = state["scenarios"][name]
        calculation = simplified_ecl(scenario["conditional_pds"], scenario["lgds"], scenario["eads"],
                                     state["effective_annual_rate"], default_window_years=state["default_window_years"])
        amounts.append(calculation["ecl"])
        weights.append(scenario["weight"])
        records.append({"scenario": name, "weight": scenario["weight"], "ecl": calculation["ecl"],
                        "annual_results": calculation["annual_results"]})
    return weighted_scenario_ecl(amounts, weights)["weighted_ecl"], records


def ecl_movement(opening, closing):
    """Ordered same-entity three-year proxy ECL bridge across two report snapshots.

    Required snapshot schema is validated by _snapshot. Explicit policy SICR flags
    are recorded, never inferred and never assign Stage 3. Window changes are
    supplied separately. Horizons are relative to each report date; the parameter
    step includes any ageing/reforecast effect, not an isolated time-unwind term.
    """
    before, after = _snapshot(opening), _snapshot(closing)
    if before["report_date"] >= after["report_date"]:
        raise ValueError("closing report_date must be after opening report_date")
    if any(before[key] != after[key] for key in ("entity_id", "currency")):
        raise ValueError("bridge requires the same entity and currency")
    if before["scenarios"].keys() != after["scenarios"].keys():
        raise ValueError("bridge requires unchanged scenario names")
    state = copy.deepcopy(before)
    opening_amount, opening_records = _snapshot_value(state)
    previous = opening_amount
    bridge = []
    for step in ("exposure", "default_window", "parameters", "scenario_weights"):
        if step == "default_window":
            state["default_window_years"] = after["default_window_years"]
        elif step == "parameters":
            state["effective_annual_rate"] = after["effective_annual_rate"]
        for name in state["scenarios"]:
            fields = {"exposure": ("eads",), "default_window": (),
                      "parameters": ("conditional_pds", "lgds"), "scenario_weights": ("weight",)}[step]
            for field in fields:
                state["scenarios"][name][field] = copy.deepcopy(after["scenarios"][name][field])
        amount, scenario_records = _snapshot_value(state)
        movement = _number(amount - previous, "movement")
        bridge.append({"step": step, "before_ecl": previous, "after_ecl": amount,
                       "movement": movement, "scenario_records": scenario_records})
        previous = amount
    closing_amount, closing_records = _snapshot_value(after)
    net = _number(closing_amount - opening_amount, "net_movement")
    residual = _number(net - _sum(r["movement"] for r in bridge), "reconciliation_residual")
    return {"entity_id": before["entity_id"], "currency": before["currency"],
            "opening_report_date": before["report_date"], "closing_report_date": after["report_date"],
            "opening_ecl": opening_amount, "closing_ecl": closing_amount, "net_movement": net,
            "reconciliation_residual": residual, "records": bridge,
            "opening_scenarios": opening_records, "closing_scenarios": closing_records,
            "supplied_sicr_flags": {"opening": before["sicr_flag"], "closing": after["sicr_flag"]},
            "action_needed": ["Review each driver against source changes and documented window/SICR policy; no automatic approval.",
                              "Separate additions, derecognition, FX, time unwind, recoveries and model changes for a production allowance bridge."],
            "assumptions_and_limits": ["Fixed order exposure → default_window → parameters → scenario_weights; interactions are order-dependent.",
                                       "PD/LGD/EAD are three annual vectors relative to each reporting date; no independently isolated ageing/unwind effect.",
                                       "Full conditional lifetime LGD is approximated as default-year-end loss; one-year window selects default events, not only one-year cash shortfalls.",
                                       "SICR flags are supplied policy facts only; no universal threshold, Stage 3 inference, or complete IFRS 9 allowance calculation."]}
