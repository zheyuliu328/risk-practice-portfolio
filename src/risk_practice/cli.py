"""Run an explicit learning-model request and retain readable evidence."""

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

from . import __version__
from .models import (
    exposure_concentration,
    fixed_cashflow_rate_shock,
    liquidity_runway,
    simplified_ecl,
    weighted_scenario_ecl,
)

from .credit import credit_parameter_review, recovery_lgd, ead_from_utilization, ecl_movement
from .market import historical_var_es, counterparty_exposure, broker_margin
from .alm import alm_nmd
from .controls import model_monitoring, alert_capacity_review, ai_release_review

MODEL_NOTES = {
    "ecl": ["Annual conditional PDs become marginal PDs using survival.", "LGD represents lifetime loss conditional on default, placed at default-year end in this simplification.", "A one-year default window is not twelve-month cash-shortfall truncation. No stage assignment or complete IFRS 9 calculation."],
    "weighted-ecl": ["Scenario amounts must already share currency, horizon, valuation date and methodology.", "This calculator checks weights, not scenario validity or accounting approval."],
    "liquidity": ["One currency; end-of-day balances only. Intraday deficits are not assessed.", "Realized proceeds must be available that day, net of costs, and not double-counted in inflows.", "A negative balance identifies a funding gap under supplied assumptions; this is not LCR."],
    "rates": ["Fixed cash flows, positive whole-year times and a flat effective annual discount rate.", "A 0.01 shock means 100 basis points. Signed cash flows need not decrease in PV when rates rise.", "No NMD behaviour, options, nonparallel curves or complete bank EVE/NII measurement."],
    "concentration": ["Aggregate exposures to the intended connected entity before calculation.", "Gross nonnegative amounts in one unit. Zero-total metrics are undefined.", "HHI does not measure default correlation, regulatory capital or diversification of losses."],
}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"non-finite JSON constant: {value}")


def calculate(model, inputs):
    if not isinstance(inputs, dict):
        raise ValueError("inputs must be a JSON object")
    functions = {
        "ecl": simplified_ecl,
        "weighted-ecl": weighted_scenario_ecl,
        "liquidity": liquidity_runway,
        "rates": fixed_cashflow_rate_shock,
        "concentration": exposure_concentration,
    }
    functions["credit-parameters"] = credit_parameter_review
    functions["recovery-lgd"] = recovery_lgd
    functions["ead-utilization"] = ead_from_utilization
    functions["ecl-movement"] = ecl_movement
    functions["historical-var-es"] = historical_var_es
    functions["counterparty"] = counterparty_exposure
    functions["broker-margin"] = broker_margin
    functions["alm-nmd"] = alm_nmd
    functions["model-monitoring"] = model_monitoring
    functions["alert-capacity"] = alert_capacity_review
    functions["ai-release-review"] = ai_release_review
    if model not in functions:
        raise ValueError("unknown learning model")
    return functions[model](**inputs)


def _table(value):
    if isinstance(value, dict):
        rows = "".join(
            f"<tr><th scope='row'>{html.escape(str(k))}</th><td>{_table(v)}</td></tr>"
            for k, v in value.items()
        )
        return "<table><tbody>" + rows + "</tbody></table>"
    if isinstance(value, list):
        return "<ol>" + "".join(f"<li>{_table(v)}</li>" for v in value) + "</ol>"
    return html.escape("undefined" if value is None else str(value))


def run_request(request_path, output):
    request_path, output = Path(request_path), Path(output)
    raw = request_path.read_bytes()
    request = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    if not isinstance(request, dict) or set(request) != {"model", "inputs"}:
        raise ValueError("request must contain exactly model and inputs")
    result = calculate(request["model"], request["inputs"])
    evidence = {
        "schema_version": 1,
        "package_version": __version__,
        "model": request["model"],
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_provenance": "caller-supplied; origin and business suitability are unverified",
        "interpretation": "learning calculation, not regulatory or model approval",
        "assumptions_and_limits": MODEL_NOTES.get(request["model"], ["Read the method-specific assumptions, limits and human actions in Results.", "Supplied labels, scenarios, legal permissions and thresholds require independent review."]),
        "request": request,
        "result": result,
    }
    result_bytes = (json.dumps(evidence, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()
    markup = (
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Risk practice — worked result</title>"
        "<style>body{font:16px/1.6 system-ui;margin:3rem auto;padding:0 1rem;max-width:1000px;color:#172c3c}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #cbd5dd;padding:.5rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}"
        "th{background:#eef4f6}ol{padding-left:1.4rem}h1{line-height:1.2}</style>"
        "<h1>Risk practice — " + html.escape(str(request["model"])) + "</h1>"
        "<p>Learning calculation using caller-supplied assumptions. Execution does not approve a model or a business decision.</p>"
        "<h2>Assumptions and limits</h2>" + _table(evidence["assumptions_and_limits"])
        + "<h2>Results</h2>" + _table(result)
        + "<h2>Inputs</h2>" + _table(request["inputs"])
        + "<p>Keep request.json, result.json and manifest.json together. The manifest detects changed bytes; it is not an authenticity signature.</p></html>"
    ).encode()
    payloads = {"request.json": raw, "result.json": result_bytes, "report.html": markup}
    manifest = {"schema_version": 1, "complete": True, "sha256": {
        name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()
    }}
    # Exclusive allocation preserves previous outputs. The manifest is written last;
    # an interrupted export without it must not be treated as a complete bundle.
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        with (output / name).open("xb") as handle:
            handle.write(data)
    with (output / "manifest.json").open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON containing model and explicit inputs")
    parser.add_argument("--output", required=True, type=Path, help="A directory that does not exist")
    args = parser.parse_args(argv)
    try:
        result = run_request(args.input, args.output)
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        print(f"Cannot complete calculation: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"model": result["model"], "output": str(args.output), "meaning": result["interpretation"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
