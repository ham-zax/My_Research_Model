"""Discover fixed-calendar BTC selloff events before shallow-capacity outcomes."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date
import json
from pathlib import Path
import subprocess
import sys

from e001_monthly_scan import pipeline_digest, valid_checkpoint
from e001_quote_audit import audit_day
from mfsm_e001.capture_store import atomic_json, sha256


ROOT = Path(__file__).resolve().parents[1]
CODE_FILES = (
    'scripts/discover_e001_shallow_capacity_events.py',
    'scripts/e001_quote_audit.py', 'scripts/fetch_e001_tardis_sample.py',
    'src/mfsm_e001/events.py', 'src/mfsm_e001/spot_quotes.py',
)


def _next_month(day):
    return date(day.year+(day.month == 12), day.month % 12+1, 1)


def _validate_protocol(protocol):
    if protocol.get('schema') != 'E001-shallow-capacity-discovery-1':
        raise ValueError('unsupported shallow-capacity discovery protocol')
    days = [date.fromisoformat(value) for value in protocol['dates']]
    if len(days) != 42 or len(set(days)) != len(days):
        raise ValueError('discovery protocol must contain 42 unique dates')
    if any(day.day != 1 for day in days):
        raise ValueError('discovery dates must be first of month')
    if any(right != _next_month(left) for left, right in zip(days, days[1:])):
        raise ValueError('discovery calendar must be contiguous by month')
    rules = protocol['rules']
    if any(rules[key] for key in ('compute_spot_labels_during_discovery',
                                  'read_l2_or_trade_outcomes_during_discovery',
                                  'fit_model', 'tune_thresholds', 'eth_access')):
        raise ValueError('discovery protocol enables a prohibited outcome action')
    return [day.isoformat() for day in days]


def _discovery_view(result):
    keep = ('date', 'spot_source_sha256', 'grid_file', 'sensitivity',
            'primary_invalid_venue_seconds', 'crossings', 'accepted_events',
            'event_ledger')
    return {key: result[key] for key in keep}


def _download(date_value):
    command = [sys.executable, str(ROOT/'scripts/fetch_e001_tardis_sample.py'),
               '--date', date_value, '--profile', 'spot-quotes']
    completed = subprocess.run(command, capture_output=True, text=True)
    return completed.returncode, completed.stdout+completed.stderr


def run(protocol_path, output, *, download, workers):
    protocol_path, output = Path(protocol_path).resolve(), Path(output).resolve()
    if 'eth' in str(output).lower():
        raise ValueError('ETH holdout is sealed')
    output.mkdir(parents=True, exist_ok=False)
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    dates = _validate_protocol(protocol)
    pipeline_sha = pipeline_digest()
    results, failures = {}, {}
    prior_directory = ROOT/'data/derived/e001_monthly_scan'
    pending = []
    for date_value in dates:
        cached = valid_checkpoint(prior_directory/f'{date_value}.json',
                                  date_value, pipeline_sha)
        if cached is not None:
            results[date_value] = _discovery_view(cached)
            print(f'{date_value}: reused hash-verified quote checkpoint', flush=True)
            continue
        if download:
            code, log = _download(date_value)
            (output/f'{date_value}-download.log').write_text(log, encoding='utf-8')
            if code:
                failures[date_value] = {'stage': 'download', 'returncode': code}
                continue
        pending.append(date_value)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(audit_day, value, include_labels=False): value
                   for value in pending}
        for future in as_completed(futures):
            date_value = futures[future]
            try:
                results[date_value] = _discovery_view(future.result())
                print(f"{date_value}: {results[date_value]['crossings']} crossings, "
                      f"{results[date_value]['accepted_events']} nominal independent",
                      flush=True)
            except Exception as exc:
                failures[date_value] = {
                    'stage': 'event_discovery',
                    'reason': f'{type(exc).__name__}: {exc}',
                }
    ordered = [results[value] for value in dates if value in results]
    event_count = sum(row['crossings'] for row in ordered)
    accepted = sum(row['accepted_events'] for row in ordered)
    status = 'COMPLETE' if len(ordered) == len(dates) and not failures else 'INCOMPLETE'
    result = {
        'schema': 'E001-shallow-capacity-event-source-1', 'status': status,
        'data_kind': protocol['data_kind'], 'protocol_sha256': sha256(protocol_path),
        'dates_requested': dates, 'dates_completed': [row['date'] for row in ordered],
        'crossings': event_count, 'nominal_independent_episodes': accepted,
        'spot_labels_computed': False, 'l2_or_trade_outcomes_read': False,
        'failures': failures, 'days': ordered,
    }
    atomic_json(output/'result.json', result)
    source_hashes = {row['date']: row['spot_source_sha256'] for row in ordered}
    atomic_json(output/'manifest.json', {
        'schema': 'E001-shallow-capacity-discovery-manifest-1', 'status': status,
        'protocol_sha256': sha256(protocol_path), 'pipeline_sha256': pipeline_sha,
        'source_sha256_by_day': source_hashes,
        'code_sha256': {name: sha256(ROOT/name) for name in CODE_FILES},
        'result_sha256': sha256(output/'result.json'),
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', default=str(
        ROOT/'experiments/e001_shallow_capacity_discovery_protocol.yaml'))
    parser.add_argument('--output', required=True)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--workers', type=int, choices=(1, 2, 3), default=2)
    args = parser.parse_args()
    try:
        result = run(args.protocol, args.output, download=args.download,
                     workers=args.workers)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'shallow-capacity discovery setup error: {exc}\n')
    print(json.dumps({'status': result['status'], 'crossings': result['crossings'],
                      'nominal_independent_episodes':
                          result['nominal_independent_episodes']}, sort_keys=True))
    return 0 if result['status'] == 'COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
