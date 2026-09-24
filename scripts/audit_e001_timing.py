"""Audit sealed BTC capture timing and compare timing candidates without fitting models.

Candidate B counts receipt-age quote opportunities only. It cannot certify
source freshness without same-domain evidence; its counts are diagnostic.
"""

import argparse
from collections import Counter, deque
from datetime import datetime, timezone
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.replay import CaptureInput, NS, Replay, replay_grid


def utc(ns):
    return datetime.fromtimestamp(ns/NS, timezone.utc).isoformat()


def timestamp_roles(row):
    if row['kind'] != 'ws_message':
        return ()
    message = json.loads(row['raw'])
    source = row['source']
    if source.startswith('bybit'):
        topic = message.get('topic', '')
        roles = [(source+':'+topic+':envelope_ts', int(message['ts'])*1_000_000)] if 'ts' in message else []
        if topic in ('publicTrade.BTCUSDT', 'allLiquidation.BTCUSDT'):
            roles.extend((source+':'+topic+':item_T', int(item['T'])*1_000_000)
                         for item in message.get('data', []) if 'T' in item)
        return roles
    data = message.get('data', {})
    topic = message.get('stream', '')
    roles = [(source+':'+topic+':event_E', int(data['E'])*1_000_000)] if 'E' in data else []
    if 'T' in data:
        roles.append((source+':'+topic+':trade_T', int(data['T'])*1_000_000))
    return roles


class LagSummary:
    def __init__(self):
        self.count = self.negative = 0
        self.minimum = self.maximum = None
        self.histogram_ms = Counter()
        self.first_negative = None

    def add(self, row, lag_ns):
        self.count += 1
        self.negative += lag_ns < 0
        self.minimum = lag_ns if self.minimum is None else min(self.minimum, lag_ns)
        self.maximum = lag_ns if self.maximum is None else max(self.maximum, lag_ns)
        self.histogram_ms[lag_ns//1_000_000] += 1
        if lag_ns < 0 and self.first_negative is None:
            self.first_negative = {'record_id': row['record_id'],
                                   'received_ns': row['received_ns'],
                                   'receipt_utc': utc(row['received_ns']),
                                   'lag_ns': lag_ns}

    def percentile_bucket(self, percent):
        rank = max(1, (self.count*percent+99)//100)
        seen = 0
        for bucket, count in sorted(self.histogram_ms.items()):
            seen += count
            if seen >= rank:
                return bucket
        return None

    def report(self):
        return {'count': self.count, 'negative_count': self.negative,
                'min_ns': self.minimum, 'max_ns': self.maximum,
                'p01_floor_ms': self.percentile_bucket(1),
                'p50_floor_ms': self.percentile_bucket(50),
                'p99_floor_ms': self.percentile_bucket(99),
                'first_negative': self.first_negative}


def receipt_quote_valid(book, boundary):
    if book is None or not book.ready or book.quote_available_ns is None:
        return False
    if book.quote_available_ns > boundary or boundary-book.quote_available_ns > 5*NS:
        return False
    return book.top() is not None


class TimingReplay(Replay):
    def __init__(self):
        super().__init__()
        self.linear_connected_since = None
        self.epoch_start_ns = None
        self.linear_flow_receipts = deque()
        self.linear_book_receipts = deque()
        self.last_linear_book_snapshot_ns = None
        self.spot_connected_since = {}

    def process(self, row, available_ns):
        if self.epoch_start_ns is None:
            self.epoch_start_ns = available_ns
        if row['kind'] == 'clock_step':
            self.epoch_start_ns = available_ns
            self.linear_connected_since = None
            self.linear_flow_receipts.clear()
            self.linear_book_receipts.clear()
            self.last_linear_book_snapshot_ns = None
            self.spot_connected_since.clear()
        if row.get('source') in ('binance_spot', 'bybit_spot'):
            spot_source = row['source']
            if row['kind'] == 'connected':
                self.spot_connected_since[spot_source] = available_ns
            elif (row['kind'] in ('disconnected', 'connection_error') and
                  self.connections.get(spot_source) == row.get('connection_id')):
                self.spot_connected_since.pop(spot_source, None)
        active_linear = (row.get('source') == 'bybit_linear' and
                         self.connections.get('bybit_linear') == row.get('connection_id'))
        if row.get('source') == 'bybit_linear':
            if row['kind'] == 'connected':
                self.linear_connected_since = available_ns
                self.linear_flow_receipts.clear()
                self.linear_book_receipts.clear()
                self.last_linear_book_snapshot_ns = None
            elif (row['kind'] in ('disconnected', 'connection_error') and
                  active_linear):
                self.linear_connected_since = None
                self.linear_flow_receipts.clear()
                self.linear_book_receipts.clear()
                self.last_linear_book_snapshot_ns = None
        super().process(row, available_ns)
        if active_linear and row['kind'] == 'ws_message':
            message = json.loads(row['raw'])
            topic = message.get('topic')
            if topic in ('publicTrade.BTCUSDT', 'allLiquidation.BTCUSDT'):
                self.linear_flow_receipts.append((available_ns, len(message.get('data', []))))
            if topic == 'orderbook.1000.BTCUSDT':
                if message.get('type') == 'snapshot':
                    self.linear_book_receipts.clear()
                    self.last_linear_book_snapshot_ns = available_ns
                book = self.books.get('bybit_linear:orderbook.1000.BTCUSDT')
                if book and book.ready:
                    self.linear_book_receipts.append(available_ns)


def audit(manifest, *, sealed_prefix=False, segment_limit=None):
    capture = CaptureInput(manifest, sealed_prefix=sealed_prefix, segment_limit=segment_limit)
    lag = {}
    kinds = Counter()
    probe_status = Counter()
    first_envelope_negative = None
    clock_steps = []

    def observed_records():
        nonlocal first_envelope_negative
        for row in capture.records():
            kinds[row['kind']] += 1
            if row['kind'] == 'clock_step':
                clock_steps.append({'record_id': row['record_id'],
                                    'received_ns': row['received_ns'],
                                    'discrepancy_ns': row.get('discrepancy_ns')})
            if row['kind'] == 'clock_probe':
                e = row.get('evidence', {})
                probe_status[e.get('source', 'unknown')+':'+e.get('status', 'unknown')] += 1
            for role, source_ns in timestamp_roles(row):
                lag_ns = row['received_ns']-source_ns
                lag.setdefault(role, LagSummary()).add(row, lag_ns)
                if (first_envelope_negative is None and lag_ns < 0 and
                        (role.endswith(':envelope_ts') or role.endswith(':event_E'))):
                    first_envelope_negative = {'record_id': row['record_id'],
                                               'source': row['source'], 'role': role,
                                               'source_ns': source_ns,
                                               'received_ns': row['received_ns'],
                                               'receipt_utc': utc(row['received_ns']),
                                               'lag_ns': lag_ns}
            yield row

    replay = TimingReplay()
    grids = Counter({key: 0 for key in (
        'total', 'legacy_valid_composite', 'legacy_clock_invalid',
        'candidate_b_receipt_quote_opportunity',
        'candidate_b_30s_linear_receipt_history_present',
        'candidate_b_30s_flow_items_in_receipt_windows',
        'candidate_b_30s_linear_book_state_ready',
        'candidate_b_30s_book_window_membership_available',
        'candidate_b_30s_book_updates_in_receipt_windows')})
    first_grid = last_grid = first_legacy_invalid_grid = None
    for grid in replay_grid(observed_records(), replay):
        second = grid['second']
        boundary = second*NS
        first_grid = second if first_grid is None else first_grid
        last_grid = second
        grids['total'] += 1
        if grid['composite_price'] is not None:
            grids['legacy_valid_composite'] += 1
        if not grid['clock_valid']:
            grids['legacy_clock_invalid'] += 1
            if first_legacy_invalid_grid is None:
                first_legacy_invalid_grid = second
        if (all(source in replay.spot_connected_since and
                replay.spot_connected_since[source] >= replay.epoch_start_ns
                for source in ('binance_spot', 'bybit_spot')) and
                all(receipt_quote_valid(replay.books.get(key), boundary) for key in
                    ('binance_spot:depth', 'bybit_spot:orderbook.1.BTCUSDT'))):
            grids['candidate_b_receipt_quote_opportunity'] += 1
        if (replay.linear_connected_since is not None and
                replay.linear_connected_since <= boundary-30*NS and
                replay.epoch_start_ns <= boundary-30*NS):
            grids['candidate_b_30s_linear_receipt_history_present'] += 1
            left = boundary-30*NS
            while replay.linear_flow_receipts and replay.linear_flow_receipts[0][0] <= left:
                replay.linear_flow_receipts.popleft()
            while (len(replay.linear_book_receipts) > 1 and
                   replay.linear_book_receipts[1] <= left):
                replay.linear_book_receipts.popleft()
            grids['candidate_b_30s_flow_items_in_receipt_windows'] += sum(
                count for _, count in replay.linear_flow_receipts)
            book = replay.books.get('bybit_linear:orderbook.1000.BTCUSDT')
            if book and book.ready and book.available_ns <= boundary:
                grids['candidate_b_30s_linear_book_state_ready'] += 1
                if (replay.linear_book_receipts and
                        replay.linear_book_receipts[0] <= left and
                        (replay.last_linear_book_snapshot_ns is None or
                         replay.last_linear_book_snapshot_ns <= left)):
                    grids['candidate_b_30s_book_window_membership_available'] += 1
                    grids['candidate_b_30s_book_updates_in_receipt_windows'] += sum(
                        received > left for received in replay.linear_book_receipts)

    root = Path(__file__).resolve().parents[1]
    return {
        'schema': 'E001-timing-audit-v1',
        'scope': 'sealed_prefix_only' if sealed_prefix else 'completed_capture',
        'run_id': capture.manifest['run_id'],
        'capture_status_at_selection': capture.manifest['status'],
        'manifest_path': str(capture.path),
        'manifest_sha256': capture.manifest_sha256,
        'segment_sha256': capture.hashes,
        'code_sha256': {name: sha256(root/name) for name in
                        ('src/mfsm_e001/timing.py', 'src/mfsm_e001/replay.py',
                         'scripts/audit_e001_timing.py')},
        'record_kinds': dict(kinds), 'lag_by_timestamp_role': {key: item.report()
                                                            for key, item in sorted(lag.items())},
        'first_envelope_negative': first_envelope_negative,
        'clock_steps': clock_steps, 'http_probe_status': dict(probe_status),
        'first_grid_second': first_grid, 'last_grid_second': last_grid,
        'first_legacy_invalid_grid_second': first_legacy_invalid_grid,
        'grid_counts': dict(grids), 'legacy_diagnostics': dict(replay.diagnostics),
        'candidate_a': {'websocket_domain_evidence': 'absent',
                        'qualifying_grid_seconds': 0,
                        'reason': 'HTTP server-time evidence does not bound WebSocket timestamp domains'},
        'candidate_b': {'measurement': 'receipt_time_quote_age_and_30s_window_membership',
                        'source_freshness_certified': False,
                        'feature_windows_complete': False,
                        'flow_and_book_counts_are_window_membership_diagnostics': True,
                        'window_item_counts_repeat_across_overlapping_grid_windows': True,
                        'primary_eligibility_changed': False},
        'histogram_note': 'Percentiles are floor-millisecond buckets; extrema are exact nanoseconds.',
        'model_fitted': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', required=True)
    parser.add_argument('--sealed-prefix', action='store_true')
    parser.add_argument('--max-segments', type=int)
    args = parser.parse_args()
    report = audit(args.manifest, sealed_prefix=args.sealed_prefix,
                   segment_limit=args.max_segments)
    target = Path(args.output)
    if 'eth' in str(target.resolve()).lower():
        parser.error('ETH holdout is sealed')
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(target, report)
    print(json.dumps({'run_id': report['run_id'], 'grid_counts': report['grid_counts'],
                      'first_envelope_negative': report['first_envelope_negative']}, indent=2))


if __name__ == '__main__':
    main()
