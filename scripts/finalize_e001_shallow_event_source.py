"""Attach conservative lockout history to a shallow-capacity event discovery."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

from e001_monthly_report import load_points
from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.sampling import audit_episode_history


ROOT = Path(__file__).resolve().parents[1]
CODE_FILES = (
    'scripts/finalize_e001_shallow_event_source.py',
    'scripts/e001_monthly_report.py', 'src/mfsm_e001/sampling.py',
)


def _utc(second):
    return datetime.fromtimestamp(second, timezone.utc).isoformat()


def run(discovery_path, output):
    discovery_path, output = Path(discovery_path).resolve(), Path(output).resolve()
    if 'eth' in str(output).lower():
        raise ValueError('ETH holdout is sealed')
    output.mkdir(parents=True, exist_ok=False)
    discovery = json.loads(discovery_path.read_text(encoding='utf-8'))
    if (discovery.get('schema') != 'E001-shallow-capacity-event-source-1' or
            discovery.get('status') != 'COMPLETE' or discovery.get('failures')):
        raise ValueError('event discovery is incomplete')
    counts = Counter()
    days = []
    for original in discovery['days']:
        day = {**original, 'event_ledger': [dict(row) for row in original['event_ledger']]}
        grid_path = ROOT/day['grid_file']
        points = load_points(grid_path)
        history = audit_episode_history(points)
        by_trigger = {row['trigger_s']: row for row in history['crossings']}
        if list(by_trigger) != [row['trigger_s'] for row in day['event_ledger']]:
            raise ValueError(f"{day['date']} lockout history crossing mismatch")
        for event in day['event_ledger']:
            state = by_trigger[event['trigger_s']]
            event['trigger_utc'] = _utc(event['trigger_s'])
            event['history_status'] = state['status']
            event['history_qualified'] = (
                event['accepted'] and state['status'] == 'accepted_with_observed_lockout')
            counts[state['status']] += 1
        day['episode_history'] = history
        day['grid_sha256'] = sha256(grid_path)
        days.append(day)
    result = {
        'schema': 'E001-shallow-capacity-final-event-source-1',
        'status': 'COMPLETE', 'data_kind': discovery['data_kind'],
        'discovery_sha256': sha256(discovery_path),
        'dates': discovery['dates_completed'], 'crossings': discovery['crossings'],
        'nominal_independent_episodes': discovery['nominal_independent_episodes'],
        'history_qualified_independent_episodes': sum(
            event['history_qualified'] for day in days for event in day['event_ledger']),
        'crossing_history_status_counts': dict(sorted(counts.items())),
        'spot_labels_computed': False, 'l2_or_trade_outcomes_read': False,
        'days': days,
    }
    atomic_json(output/'result.json', result)
    atomic_json(output/'manifest.json', {
        'schema': 'E001-shallow-capacity-final-event-manifest-1',
        'status': 'COMPLETE', 'discovery_sha256': sha256(discovery_path),
        'code_sha256': {name: sha256(ROOT/name) for name in CODE_FILES},
        'result_sha256': sha256(output/'result.json'),
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--discovery', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = run(args.discovery, args.output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'event source finalization error: {exc}\n')
    print(json.dumps({'crossings': result['crossings'],
                      'nominal_independent_episodes':
                          result['nominal_independent_episodes'],
                      'history_qualified_independent_episodes':
                          result['history_qualified_independent_episodes']}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
