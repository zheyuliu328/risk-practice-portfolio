"""Regression check for the published teaching case, not evidence of human acceptance."""
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / 'flagship/forecast-review/inputs'


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load_series(name, date, value):
    with (INPUTS / name).open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    check(len({r[date] for r in rows}) == len(rows), 'Duplicate fixture key')
    return {r[date]: Decimal(r[value]) for r in rows}


def verify(runner, output):
    provenance = json.loads((INPUTS / 'PROVENANCE.json').read_text())
    for name, digest in provenance['sha256'].items():
        check(hashlib.sha256((INPUTS / name).read_bytes()).hexdigest() == digest, 'Fixture provenance changed')
    output.mkdir(parents=True, exist_ok=False)
    results = {}
    for name, request, code in [('intake', 'request.json', 1), ('comparison', 'request-accepted.json', 0), ('conflicting-unit', 'request-conflicting-unit.json', 1)]:
        destination = output / name
        command = [runner, '--review', str(INPUTS / request), '--output', str(destination)]
        run = subprocess.run(command, capture_output=True, text=True)
        check(run.returncode == code, f'{name}: expected exit {code}, got {run.returncode}: {run.stderr}')
        result = json.loads((destination / 'results.json').read_text())
        manifest = json.loads((destination / 'manifest.json').read_text())
        for file, digest in manifest['files_sha256'].items():
            check(hashlib.sha256((destination / file).read_bytes()).hexdigest() == digest, 'Export hash mismatch')
        before = {p.name: p.read_bytes() for p in destination.iterdir()}
        retry = subprocess.run(command, capture_output=True)
        check(retry.returncode == 2, 'Existing output must be refused')
        check(before == {p.name: p.read_bytes() for p in destination.iterdir()}, 'Output changed on retry')
        check(json.loads((destination / 'review-notes.json').read_text())['notes'] == [], 'CLI invented a human opinion')
        results[name] = result
    check(not results['intake']['comparison_ready'], 'Intake must require explicit acceptance')
    check(results['comparison']['comparison_ready'], 'Accepted common-sample comparison should run')
    check(not results['conflicting-unit']['comparison_ready'], 'Unit conflict must block despite acceptance')
    conflict = results['conflicting-unit']
    check(conflict['accepted_common_sample'] is True, 'Conflict case must remain explicitly accepted')
    check(conflict['contract_errors'] == [{'source_id': 'model-a', 'field': 'unit', 'expected': 'USD', 'received': 'EUR'}], 'Expected USD/EUR contract conflict')
    check(all(m['metrics'] is None and m['available_metrics'] is None for m in conflict['models']), 'Incompatible-unit metrics must not be calculated')
    check(all(all(v is None for v in r['residuals'].values()) for r in conflict['rows']), 'Incompatible-unit residuals must not be calculated')
    actual = load_series('actual.csv', 'Month', 'Observed')
    candidates = {'model-a': load_series('candidate-a.csv', 'period', 'Forecast'), 'model-b': load_series('candidate-b.csv', 'snapshot', 'prediction'), 'baseline': load_series('baseline.csv', 'Month', 'Reference')}
    common = set(actual).intersection(*(set(v) for v in candidates.values()))
    check(len(actual) == 12 and len(common) == 7, 'Unexpected coverage')
    excluded = sorted(set(actual) - common)
    check(excluded == ['2024-04', '2024-05', '2024-10', '2024-11', '2024-12'], 'Excluded population changed')
    check([r['period'] for r in results['comparison']['rows'] if not r['included']] == excluded, 'Excluded rows hidden')
    oracles = {}
    with localcontext() as ctx:
        ctx.prec = 40
        for model in results['comparison']['models']:
            expected = {}
            for field, keys in [('metrics', common), ('available_metrics', set(actual) & set(candidates[model['id']]))]:
                errors = [candidates[model['id']][k] - actual[k] for k in sorted(keys)]
                values = {'mae': sum(map(abs, errors)) / len(errors), 'bias': sum(errors) / len(errors), 'rmse': (sum(e * e for e in errors) / len(errors)).sqrt()}
                check(model[field]['n'] == len(keys), 'Metric sample changed')
                for metric, value in values.items():
                    check(abs(Decimal(model[field][metric]) - value) < Decimal('1e-30'), f'Independent {metric} mismatch')
                expected[field] = {k: str(v) for k, v in values.items()}
            oracles[model['id']] = expected
    evidence = {'source_commit': provenance['source_commit'], 'states': {'intake_exit': 1, 'accepted_exit': 0, 'conflict_exit': 1, 'overwrite_exit': 2}, 'expected_months': 12, 'common_months': 7, 'excluded_months': excluded, 'independent_raw_csv_metrics': oracles, 'preservation_and_hashes': 'passed', 'human_adoption': 'not assessed', 'meaning': 'Automated replay of teaching fixtures; acceptance in the test is not a human review.'}
    (output / 'verification.json').write_text(json.dumps(evidence, indent=2) + '\n')
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runner', default=shutil.which('forecast-review'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if not args.runner:
        parser.error('Install the pinned Forecast Review Workbench first')
    try:
        evidence = verify(args.runner, args.output)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'Flagship verification failed: {exc}\n')
    print(json.dumps({'output': str(args.output), 'common_months': evidence['common_months'], 'meaning': evidence['meaning']}))
