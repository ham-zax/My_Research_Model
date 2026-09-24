"""Run the separate first-of-month BTC observational study on free Tardis data."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import sklearn

from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.exploratory import (
    InsufficientDataError, build_exploratory_day, evaluate_exploratory,
    validate_protocol,
)


ROOT = Path(__file__).resolve().parents[1]
CODE_FILES = (
    'scripts/run_e001_exploratory.py', 'src/mfsm_e001/exploratory.py',
    'src/mfsm_e001/spot_quotes.py', 'src/mfsm_e001/validation.py',
    'src/mfsm_e001/models.py', 'src/mfsm_e001/capture_store.py',
    'uv.lock', 'pyproject.toml',
)


def _report(result):
    lines = [
        '# E001 separate exploratory BTC study', '',
        f"Status: **{result['status']}**", '',
        f"Protocol SHA-256: `{result['protocol_sha256']}`",
        f"Scheduled hourly decisions: {result['scheduled_decisions']}",
        f"Eligible decisions: {result['eligible_decisions']}",
        f"Eligible outcome counts: {result['eligible_outcome_counts']}",
        f"Exclusion counts (reasons can overlap): {result['exclusion_counts']}", '',
    ]
    score = result.get('evaluation')
    if score is not None:
        lines += [
            f"Paired test decisions: {score['test_episodes']}",
            f"Baseline Brier: {score['b4_brier']:.8f}",
            f"MFSM Brier: {score['mfsm_brier']:.8f}",
            f"Brier improvement (baseline minus MFSM): {score['paired_brier_improvement']:+.8f}",
            '',
        ]
    if result.get('reason'):
        lines += [f"Reason: {result['reason']}", '']
    lines += [
        '## Interpretation', '',
        'This is an exploratory association measured on nonconsecutive first-of-month BTC days. '
        'It uses local receipt timestamps and observed trades; feed completeness and per-message '
        'source age are not independently certified. The 30-minute first-passage label uses '
        '−0.5% downside and +0.375% upside barriers. Neither-by-horizon is class 0. '
        'A lower Brier score does not establish net trading profit or validate the original '
        'shock-triggered E001 liquidation claim. ETH was not accessed.', '',
    ]
    return '\n'.join(lines)


def run(protocol_path, output):
    output = Path(output).resolve()
    if 'eth' in str(output).lower():
        raise ValueError('ETH holdout is sealed')
    output.mkdir(parents=True, exist_ok=False)
    protocol_path = Path(protocol_path).resolve()
    protocol_hash = sha256(protocol_path) if protocol_path.is_file() else None
    base = {'schema': 'E001-OBS-run-result-1', 'data_kind': 'exploratory_tardis_btc',
            'protocol_sha256': protocol_hash, 'scheduled_decisions': 0,
            'eligible_decisions': 0, 'eligible_outcome_counts': {},
            'exclusion_counts': {}, 'model_fitted': False, 'evaluation': None,
            'eth_accessed': False}
    day_receipts = []
    episodes = []
    try:
        protocol = json.loads(protocol_path.read_text())
        validate_protocol(protocol)
        for index, day in enumerate(protocol['dates']):
            observed = build_exploratory_day(ROOT, day, index, protocol)
            day_receipts.append({key: value for key, value in observed.items()
                                 if key != 'episodes'})
            episodes.extend(observed['episodes'])
            print(f"{day}: {observed['eligible_decisions']}/{observed['scheduled_decisions']} eligible",
                  flush=True)
        with (output/'episodes.jsonl').open('w', encoding='utf-8') as stream:
            for episode in episodes:
                stream.write(json.dumps(episode, sort_keys=True)+'\n')
        base['scheduled_decisions'] = len(episodes)
        base['eligible_decisions'] = sum(e['primary_eligible'] for e in episodes)
        base['eligible_outcome_counts'] = dict(sorted(Counter(
            e['primary_label']['state'] for e in episodes if e['primary_eligible']).items()))
        base['exclusion_counts'] = dict(sorted(sum(
            (Counter(e['exclusion_reasons']) for e in episodes), Counter()).items()))
        try:
            score = evaluate_exploratory(episodes, protocol)
        except InsufficientDataError as exc:
            base.update(status='INSUFFICIENT_DATA', reason=str(exc))
        else:
            base.update(status='EXPLORATORY_SCORED', model_fitted=True, evaluation=score)
    except Exception as exc:
        base.update(status='ERROR', reason=f'{type(exc).__name__}: {exc}')
    base['days'] = day_receipts
    atomic_json(output/'result.json', base)
    (output/'report.md').write_text(_report(base), encoding='utf-8')
    atomic_json(output/'manifest.json', {
        'schema': 'E001-OBS-run-manifest-1', 'status': base['status'],
        'protocol_sha256': protocol_hash,
        'code_sha256': {name: sha256(ROOT/name) for name in CODE_FILES},
        'source_sha256_by_day': {row['date']: row['source_sha256'] for row in day_receipts},
        'episodes_sha256': sha256(output/'episodes.jsonl')
            if (output/'episodes.jsonl').is_file() else None,
        'result_sha256': sha256(output/'result.json'),
        'report_sha256': sha256(output/'report.md'),
        'python_version': sys.version.split()[0], 'sklearn_version': sklearn.__version__,
    })
    return base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', default=str(ROOT/'experiments'/
                        'e001_observational_exploratory_protocol.yaml'))
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = run(args.protocol, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'exploratory run setup error: {exc}\n')
    print(json.dumps({'status': result['status'],
                      'eligible_decisions': result['eligible_decisions'],
                      'model_fitted': result['model_fitted'],
                      'result_path': str(Path(args.output).resolve()/'result.json')},
                     sort_keys=True))
    return {'EXPLORATORY_SCORED': 0, 'INSUFFICIENT_DATA': 2, 'ERROR': 1}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())
