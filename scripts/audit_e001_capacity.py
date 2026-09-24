"""Audit the E001 visible-capacity proxy on predefined BTC selloff crossings."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import sys

from mfsm_e001.capacity_audit import (
    audit_capacity_event,
    read_capacity_trades,
    reconstruct_book_inputs,
    summarize_capacity_audit,
)
from mfsm_e001.capture_store import atomic_json, sha256


ROOT = Path(__file__).resolve().parents[1]
CODE_FILES = (
    'scripts/audit_e001_capacity.py',
    'src/mfsm_e001/capacity_audit.py',
    'src/mfsm_e001/capture_features.py',
    'src/mfsm_e001/replay.py',
)


def _json_ready(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _load_protocol(path):
    protocol = json.loads(path.read_text(encoding='utf-8'))
    if protocol.get('schema') not in {
            'E001-capacity-audit-protocol-1',
            'E001-shallow-capacity-audit-protocol-1'}:
        raise ValueError('unsupported capacity audit protocol')
    if protocol.get('event_selection') != 'all_predefined_crossings':
        raise ValueError('capacity audit must use all predefined crossings')
    if protocol.get('analysis', {}).get('model_fit') is not False:
        raise ValueError('capacity audit protocol must disable model fitting')
    if protocol.get('analysis', {}).get('threshold_tuning') is not False:
        raise ValueError('capacity audit protocol must disable threshold tuning')
    return protocol


def _load_events(protocol):
    source = ROOT/protocol['event_source']
    if sha256(source) != protocol['event_source_sha256']:
        raise ValueError('predefined event source hash does not match protocol')
    payload = json.loads(source.read_text(encoding='utf-8'))
    if payload.get('status') not in (None, 'COMPLETE'):
        raise ValueError('predefined event source is incomplete')
    events = []
    for day in payload['days']:
        ledger = day.get('event_ledger') or []
        if len(ledger) != day['crossings']:
            raise ValueError(f"{day['date']} crossing ledger count mismatch")
        for row in ledger:
            event = {'date': day['date'], **row}
            event.setdefault('trigger_utc', datetime.fromtimestamp(
                event['trigger_s'], timezone.utc).isoformat())
            events.append(event)
    if len(events) != protocol['expected_crossings']:
        raise ValueError('predefined crossing count does not match protocol')
    if len({(row['date'], row['trigger_s']) for row in events}) != len(events):
        raise ValueError('duplicate predefined crossing')
    expected_qualified = protocol.get('expected_history_qualified_independent_episodes')
    if (expected_qualified is not None and
            sum(row.get('history_qualified', False) for row in events) != expected_qualified):
        raise ValueError('history-qualified event count does not match protocol')
    return source, events


def _verified_source(date, kind):
    directory = ROOT/'data/raw/tardis'/date
    filename = f'bybit_{kind}_{date}_BTCUSDT.csv.gz'
    path = directory/filename
    manifest_path = directory/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    entry = manifest.get(filename)
    if entry is None or entry.get('sha256') != sha256(path):
        raise ValueError(f'{filename} failed source manifest verification')
    return path, entry['sha256']


def _report(result):
    summary = result['summary']
    lines = [
        '# E001 visible-capacity audit', '',
        f"Status: **{result['status']}**", '',
        f"Visible bid band: {result['capacity_band_bps']} bps",
        f"Predefined sharp-selloff crossings: {summary['crossings']}",
        f"Crossings with complete capacity measurement: {summary['valid_crossings']}",
        f"Valid independent episodes: {summary['valid_independent_episodes']}",
        f"Crossings excluded by reason: {summary['exclusion_counts']}",
        f"25 bps breaches within 30 seconds: {summary['breached_crossings']}",
        f"Right-censored no-breach crossings: {summary['right_censored_crossings']}",
        ('No-breach crossings where observed sell flow exceeded the proxy: '
         f"{summary['capacity_under_observed_no_breach_crossings']}"), '',
        '## Result', '',
    ]
    if summary.get('excluded_pretrigger_minimum_bid_coverage_bps'):
        coverage = summary['excluded_pretrigger_minimum_bid_coverage_bps']
        lines += [
            'For excluded events, the minimum available pretrigger bid coverage per event '
            f"ranged from {float(coverage['minimum']):.3f} to "
            f"{float(coverage['maximum']):.3f} bps (median "
            f"{float(coverage['median']):.3f} bps), versus the fixed 25 bps requirement.", '',
        ]
    correlations = summary['rank_correlations']
    if correlations['status'] == 'not_computed':
        lines += [
            'The audit cannot estimate whether the capacity proxy ranks independent episodes '
            f"reliably: {correlations['reason']}. Locked-out crossings are retained as "
            'diagnostics and are not counted as independent evidence.', '',
        ]
    else:
        lines += [
            'Descriptive Spearman rank correlations across independent episodes:', '',
            f"`{correlations['metrics']}`", '',
        ]
    lines += [
        'A no-breach row is right-censored: its sell flow is a lower bound on the amount '
        'observed without a 25 bps midpoint decline. A breached row records sell flow only '
        'through the first observed breach. These are observational measurements because '
        'simultaneous buy flow, cancellations, hidden liquidity and cross-venue activity are '
        'not controlled.', '',
        '## Event measurements', '',
        '| UTC trigger | Independent | Measurement | Capacity USDT | Sell 30s USDT | '
        'First breach | Depth 30s | Mid 30s bps |',
        '|---|---:|---|---:|---:|---:|---:|---:|',
    ]
    for row in result['events']:
        if row['valid']:
            values = (row['capacity_proxy'], row['future_sell_notional_30s'],
                      row['first_25bps_breach_seconds'], row['depth_ratio_30s'],
                      row['mid_return_bps_30s'])
            formatted = [f'{float(values[0]):.2f}', f'{float(values[1]):.2f}',
                         'none' if values[2] is None else str(values[2]),
                         f'{float(values[3]):.4f}', f'{float(values[4]):+.2f}']
            measurement = 'valid'
        else:
            formatted = ['—']*5
            measurement = row['reason']
        independent = row.get('history_qualified', row['accepted'])
        lines.append(f"| {row['trigger_utc']} | {'yes' if independent else 'no'} | "
                     f"{measurement} | {' | '.join(formatted)} |")
    lines += [
        '', '## Scope', '',
        'This audit uses Bybit perpetual normalized L2 and trade files on receipt time. '
        'It does not identify liquidation executions, prove a causal mechanism, fit a model, '
        'or establish trading profitability. The original E001 timing status remains blocked.', '',
    ]
    return '\n'.join(lines)


def _audit_day(date, day_events, protocol):
    book_path, book_hash = _verified_source(date, 'incremental_book_L2')
    trade_path, trade_hash = _verified_source(date, 'trades')
    targets = set()
    observation_ranges = []
    trade_windows = []
    for event in day_events:
        trigger, decision = event['trigger_s'], event['decision_s']
        targets.update(range(trigger-1800, decision+31))
        observation_ranges.append((decision-20, decision))
        trade_windows.append((decision-30, decision+30))
    states, observations, book_diagnostics = reconstruct_book_inputs(
        book_path, target_seconds=targets,
        observation_ranges=observation_ranges,
        band_bps=protocol['capacity']['visible_bid_band_bps'])
    trades, trade_diagnostics = read_capacity_trades(
        trade_path, windows=trade_windows)
    rows = []
    for event in day_events:
        measured = audit_capacity_event(
            states, observations, trades, trigger_s=event['trigger_s'],
            capacity_band_bps=protocol['capacity']['visible_bid_band_bps'],
            breach_bps=-protocol['outcomes']['midpoint_breach_bps'])
        row = {**event, **measured}
        if row['valid']:
            row['right_censored'] = row['first_25bps_breach_seconds'] is None
            row['future_sell_to_capacity'] = (
                row['future_sell_notional_30s']/row['capacity_proxy'])
            row['sell_before_breach_to_capacity'] = (
                row['sell_notional_before_25bps_breach']/row['capacity_proxy'])
        rows.append(row)
    diagnostics = {
        'date': date, 'crossings': len(day_events),
        'reconstructed_book_seconds': len(states),
        'decision_window_cohorts': len(observations),
        'selected_trades': len(trades),
        'book_diagnostics': book_diagnostics,
        'trade_diagnostics': trade_diagnostics,
    }
    return rows, diagnostics, {'book': book_hash, 'trades': trade_hash}


def run(protocol_path, output, *, workers=2):
    protocol_path, output = Path(protocol_path).resolve(), Path(output).resolve()
    if 'eth' in str(output).lower():
        raise ValueError('ETH holdout is sealed')
    output.mkdir(parents=True, exist_ok=False)
    protocol = _load_protocol(protocol_path)
    event_source, events = _load_events(protocol)
    rows = []
    days = []
    source_hashes = {}
    try:
        by_day = {date: [row for row in events if row['date'] == date]
                  for date in sorted({row['date'] for row in events})}
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_audit_day, date, day_events, protocol): date
                       for date, day_events in by_day.items()}
            for future in as_completed(futures):
                date = futures[future]
                day_rows, diagnostics, hashes = future.result()
                rows.extend(day_rows)
                days.append(diagnostics)
                source_hashes[date] = hashes
                print(f"{date}: reconstructed "
                      f"{diagnostics['reconstructed_book_seconds']} book seconds, "
                      f"{diagnostics['decision_window_cohorts']} decision-window cohorts, "
                      f"{diagnostics['selected_trades']} selected trades", flush=True)
        rows.sort(key=lambda row: (row['date'], row['trigger_s']))
        days.sort(key=lambda row: row['date'])
        summary = summarize_capacity_audit(
            rows, minimum_independent=protocol['analysis'][
                'minimum_independent_episodes_for_rank_correlation'])
        if (summary['valid_crossings'] == 0 and
                summary['exclusion_counts'] == {
                    'incomplete_pretrigger_bid_band': len(rows)}):
            status = 'BLOCKED_DEPTH_COVERAGE'
        elif summary['rank_correlations']['status'] == 'not_computed':
            status = 'INSUFFICIENT_INDEPENDENT_EPISODES'
        else:
            status = 'CAPACITY_AUDIT_COMPLETE'
        result = {
            'schema': 'E001-capacity-audit-result-1', 'status': status,
            'data_kind': protocol['data_kind'], 'model_fitted': False,
            'thresholds_tuned': False, 'protocol_sha256': sha256(protocol_path),
            'capacity_band_bps': protocol['capacity']['visible_bid_band_bps'],
            'event_source_sha256': sha256(event_source), 'summary': summary,
            'days': days, 'events': rows,
        }
    except Exception as exc:
        result = {
            'schema': 'E001-capacity-audit-result-1', 'status': 'ERROR',
            'data_kind': protocol.get('data_kind'), 'model_fitted': False,
            'thresholds_tuned': False, 'protocol_sha256': sha256(protocol_path),
            'capacity_band_bps': protocol.get('capacity', {}).get('visible_bid_band_bps'),
            'event_source_sha256': sha256(event_source),
            'reason': f'{type(exc).__name__}: {exc}', 'summary': {},
            'days': days, 'events': rows,
        }
    serializable = _json_ready(result)
    atomic_json(output/'result.json', serializable)
    if result['status'] != 'ERROR':
        (output/'report.md').write_text(_report(result), encoding='utf-8')
    else:
        (output/'report.md').write_text(
            f"# E001 visible-capacity audit\n\nStatus: **ERROR**\n\n{result['reason']}\n",
            encoding='utf-8')
    atomic_json(output/'manifest.json', {
        'schema': 'E001-capacity-audit-manifest-1', 'status': result['status'],
        'protocol_sha256': sha256(protocol_path),
        'event_source_sha256': sha256(event_source),
        'source_sha256_by_day': source_hashes,
        'code_sha256': {name: sha256(ROOT/name) for name in CODE_FILES},
        'result_sha256': sha256(output/'result.json'),
        'report_sha256': sha256(output/'report.md'),
        'python_version': sys.version.split()[0],
    })
    return serializable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', default=str(
        ROOT/'experiments/e001_capacity_audit_protocol.yaml'))
    parser.add_argument('--output', required=True)
    parser.add_argument('--workers', type=int, choices=(1, 2, 3), default=2)
    args = parser.parse_args()
    try:
        result = run(args.protocol, args.output, workers=args.workers)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'capacity audit setup error: {exc}\n')
    print(json.dumps({'status': result['status'],
                      'valid_crossings': result.get('summary', {}).get('valid_crossings'),
                      'output': str(Path(args.output).resolve())}, sort_keys=True))
    return 1 if result['status'] == 'ERROR' else 0


if __name__ == '__main__':
    raise SystemExit(main())
