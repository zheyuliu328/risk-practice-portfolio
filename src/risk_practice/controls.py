"""Explicit review signals, capacity trade-offs and defensive evidence checks.

These functions inspect supplied records. They do not investigate customers,
establish criminal intent, validate semantic truth or authorise model deployment.
"""

import math
from bisect import bisect_right

from .models import _number, _vector


def _records(records, required):
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a nonempty list")
    seen = set()
    for row in records:
        if not isinstance(row, dict) or set(row) != required:
            raise ValueError(f"each record must have exactly {sorted(required)}")
        key = row["id"]
        if not isinstance(key, str) or not key or key != key.strip() or key in seen:
            raise ValueError("IDs must be unique, nonempty exact strings without outer whitespace")
        seen.add(key)
    return records


def model_monitoring(reference_values, current_values, cutpoints, psi_review_threshold,
                     *, reference_losses=None, current_losses=None, mean_loss_increase_threshold=None):
    """PSI with declared bins covering both tails; optional observed-loss monitoring.

    Bins are (-inf,c0), [c0,c1), ..., [ck,+inf); boundary values enter the bin on
    their right. Add 0.5 to every bin count before normalising each population.
    This is an explicit smoothing choice. Thresholds are caller example policies,
    not universal regulatory limits. Losses are caller-supplied observed losses;
    the function cannot prove sample comparability or label maturity.
    """
    reference = _vector(reference_values, "reference_values")
    current = _vector(current_values, "current_values")
    cuts = _vector(cutpoints, "cutpoints")
    if any(b <= a for a, b in zip(cuts, cuts[1:])):
        raise ValueError("cutpoints must be strictly increasing")
    threshold = _number(psi_review_threshold, "psi_review_threshold", minimum=0)
    counts = []
    for values in (reference, current):
        buckets = [0] * (len(cuts) + 1)
        for value in values:
            buckets[bisect_right(cuts, value)] += 1
        counts.append(buckets)
    proportions = [[(n + .5) / (sum(bucket) + .5 * len(bucket)) for n in bucket] for bucket in counts]
    rows = []
    for i, (p, q) in enumerate(zip(*proportions)):
        rows.append({"bin": i, "lower_inclusive": None if i == 0 else cuts[i-1],
                     "upper_exclusive": None if i == len(cuts) else cuts[i],
                     "reference_count": counts[0][i], "current_count": counts[1][i],
                     "reference_smoothed_share": p, "current_smoothed_share": q,
                     "psi_contribution": (q-p) * math.log(q/p)})
    psi = math.fsum(row["psi_contribution"] for row in rows)
    signals = []
    if psi > threshold:
        signals.append("distribution_change_exceeds_declared_review_threshold")
    performance = None
    supplied = (reference_losses is not None, current_losses is not None)
    if any(supplied) and not all(supplied):
        raise ValueError("supply both reference and current losses, or neither")
    if all(supplied):
        if mean_loss_increase_threshold is None:
            raise ValueError("observed-loss review requires a declared increase threshold")
        limit = _number(mean_loss_increase_threshold, "mean_loss_increase_threshold", minimum=0)
        old = _vector(reference_losses, "reference_losses", minimum=0)
        new = _vector(current_losses, "current_losses", minimum=0)
        old_mean = math.fsum(v/len(old) for v in old)
        new_mean = math.fsum(v/len(new) for v in new)
        performance = {"reference_count": len(old), "current_count": len(new),
                       "reference_mean_loss": old_mean, "current_mean_loss": new_mean,
                       "absolute_mean_increase": new_mean-old_mean, "declared_review_threshold": limit}
        if new_mean-old_mean > limit:
            signals.append("observed_loss_increase_exceeds_declared_review_threshold")
    else:
        if mean_loss_increase_threshold is not None:
            raise ValueError("loss threshold without loss observations is ambiguous")
        signals.append("performance_unassessed_no_observed_losses")
    return {"psi": psi, "declared_psi_review_threshold": threshold, "bins": rows,
            "performance": performance, "review_signals": signals,
            "human_review": "Check population, timing, labels and use changes; owner proposes remediation and independent reviewer checks it. No automatic approval or retraining.",
            "assumptions_and_limits": ["Cutpoints are declared before review; both infinite tails are included.", "Half-count smoothing affects PSI, especially with small samples.", "No signal does not prove model suitability. Supplied losses do not prove independent or mature evaluation."]}


def alert_capacity_review(records, capacity, score_threshold, false_positive_cost, false_negative_cost):
    """Prioritise supplied alert scores under an explicitly declared capacity.

    Scores are ranking values, not calibrated probabilities. Boolean labels are
    supplied adjudications; None means unknown. Metrics describe only labelled
    rows and may be selection-biased. No inference is made about unknown cases.
    """
    rows = _records(records, {"id", "score", "label"})
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 0:
        raise ValueError("capacity must be a nonnegative integer")
    threshold = _number(score_threshold, "score_threshold")
    fp_cost = _number(false_positive_cost, "false_positive_cost", minimum=0)
    fn_cost = _number(false_negative_cost, "false_negative_cost", minimum=0)
    normalized = []
    for row in rows:
        if row["label"] is not None and not isinstance(row["label"], bool):
            raise ValueError("label must be true, false or null")
        normalized.append({**row, "score": _number(row["score"], "score")})
    eligible = sorted((r for r in normalized if r["score"] >= threshold), key=lambda r: (-r["score"], r["id"]))
    selected = {r["id"] for r in eligible[:capacity]}
    counts = dict(tp=0, fp=0, tn=0, fn=0, unknown_selected=0, unknown_not_selected=0)
    output = []
    for row in normalized:
        pick = row["id"] in selected
        label = row["label"]
        if label is None:
            counts["unknown_selected" if pick else "unknown_not_selected"] += 1
        else:
            counts[("tp" if label else "fp") if pick else ("fn" if label else "tn")] += 1
        output.append({**row, "selected_for_review": pick,
                       "reason": "selected" if pick else "below_threshold" if row["score"] < threshold else "capacity_deferred"})
    known_picks = counts["tp"]+counts["fp"]
    known_positive = counts["tp"]+counts["fn"]
    cost = counts["fp"]*fp_cost + counts["fn"]*fn_cost
    if not math.isfinite(cost):
        raise ValueError("observed cost is not representable")
    return {"capacity": capacity, "eligible": len(eligible), "selected": len(selected),
            "observed_counts": counts,
            "precision_on_known_labels": counts["tp"]/known_picks if known_picks else None,
            "recall_on_known_labels": counts["tp"]/known_positive if known_positive else None,
            "illustrative_cost_on_known_labels": cost, "records": output,
            "human_review": "Investigators adjudicate selected cases; assess deferred cases and unknown-label bias before changing rules. Authorised AML staff decide escalation/reporting.",
            "assumptions_and_limits": ["Capacity is a supplied review budget, not a regulatory safe level.", "Unknown labels remain unknown; observed recall is not population recall.", "Costs are illustrative and omit unknown outcomes and wider business effects.", "Score ties are ordered by exact ID for reproducibility, not because one case is economically riskier."]}


def ai_release_review(records, absolute_tolerance):
    """Deterministic checks on supplied AI outputs against an explicit benchmark.

    Reference-ID presence is not semantic support. semantic_supported must be
    independently adjudicated (true/false/null). Requested actions are strings
    checked against each case's allowlist; this function never executes actions.
    """
    rows = _records(records, {"id", "expected_value", "reported_value", "required_sources",
                              "cited_sources", "semantic_supported", "allowed_actions", "requested_actions"})
    tolerance = _number(absolute_tolerance, "absolute_tolerance", minimum=0)
    result = []
    for row in rows:
        for name in ("required_sources", "cited_sources", "allowed_actions", "requested_actions"):
            values = row[name]
            if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique nonempty strings")
        semantic = row["semantic_supported"]
        if semantic is not None and not isinstance(semantic, bool):
            raise ValueError("semantic_supported must be true, false or null")
        expected = _number(row["expected_value"], "expected_value")
        reported = None if row["reported_value"] is None else _number(row["reported_value"], "reported_value")
        difference = None if reported is None else reported-expected
        if difference is not None and not math.isfinite(difference):
            raise ValueError("numerical difference is not representable")
        missing = sorted(set(row["required_sources"])-set(row["cited_sources"]))
        unauthorized = sorted(set(row["requested_actions"])-set(row["allowed_actions"]))
        issues = []
        if difference is None:
            issues.append("numerical_answer_missing")
        elif abs(difference) > tolerance:
            issues.append("numerical_difference")
        if missing:
            issues.append("required_source_missing")
        if semantic is not True:
            issues.append("semantic_support_unassessed" if semantic is None else "semantic_support_failed")
        if unauthorized:
            issues.append("unauthorized_action_requested")
        result.append({**row, "difference": difference, "missing_sources": missing,
                       "unauthorized_actions": unauthorized, "issues": issues,
                       "status": "requires_resolution" if issues else "eligible_for_human_review"})
    return {"case_count": len(result), "requires_resolution": sum(bool(r["issues"]) for r in result),
            "records": result,
            "human_review": "A responsible reviewer checks supplied benchmark evidence, semantic labels and business use before release. No automated approval.",
            "assumptions_and_limits": ["This evaluates supplied responses; it does not run an AI model or test all prompt attacks.", "Semantic labels and expected answers are assessor inputs, not facts discovered by this checker.", "A passing finite benchmark cannot establish production safety; changes to models, prompts, inputs or permissions need new checks."]}
