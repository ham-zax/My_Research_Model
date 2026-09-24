import json
from pathlib import Path
from decimal import Decimal

from mfsm_e001.capture_store import CaptureStore, atomic_json
from mfsm_e001.collect import SNAPSHOT_URL
from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
from mfsm_e001.replay import CaptureInput
from mfsm_e001.replay import Replay
from mfsm_e001.timing import (ClockEvidence, EvidenceTimeline, arrival_class,
                              dwell_complete, event_interval, quote_freshness,
                              receipt_membership, window_membership)


def evidence(*, available=210, source='bybit', domain='http_server_time',
             role='server_time', epoch=0):
    row = {'status': 'ok', 'source': source, 'domain': domain, 'role': role,
           'epoch': epoch, 'request_start_ns': 100,
           'request_start_monotonic_ns': 1000, 'received_ns': 200,
           'received_monotonic_ns': 1100, 'available_ns': available,
           'server_ns': 500, 'resolution_ns': 1,
           'offset_lower_ns': 299, 'offset_upper_ns': 401}
    return ClockEvidence.from_probe(row)


def test_legacy_replay_permanently_invalidates_after_331859_ns_inversion():
    replay = Replay()
    replay.process({'kind': 'connected', 'source': 'bybit_spot', 'connection_id': 'a',
                    'received_ns': 900_000_000}, 900_000_000)
    def book(ts, sequence):
        return {'topic': 'orderbook.1.BTCUSDT', 'type': 'snapshot', 'ts': ts,
                'data': {'s': 'BTCUSDT', 'u': sequence, 'seq': sequence,
                         'b': [['99', '1']], 'a': [['101', '1']]}}
    inverted = 1_000_000_000-331_859
    replay.process({'kind': 'ws_message', 'source': 'bybit_spot', 'connection_id': 'a',
                    'received_ns': inverted, 'raw': json.dumps(book(1000, 1))}, inverted)
    assert not replay.clock_valid
    replay.process({'kind': 'ws_message', 'source': 'bybit_spot', 'connection_id': 'a',
                    'received_ns': 1_002_000_000, 'raw': json.dumps(book(1001, 2))},
                   1_002_000_000)
    assert replay.books['bybit_spot:orderbook.1.BTCUSDT'].receipt_clock_valid
    assert not replay.grid(2)['clock_valid']
    assert replay.diagnostics['bybit_spot:source_event_after_receipt'] == 1


def test_evidence_selection_is_causal_explicitly_expiring_and_domain_specific():
    timeline = EvidenceTimeline()
    timeline.add(evidence())
    assert timeline.select('bybit', 'http_server_time', 'server_time', 209, 0,
                           max_age_ns=100) is None
    assert timeline.select('bybit', 'http_server_time', 'server_time', 210, 0,
                           max_age_ns=100) == evidence()
    assert timeline.select('bybit', 'websocket_envelope', 'ts', 211, 0,
                           max_age_ns=100) is None
    assert timeline.select('bybit', 'http_server_time', 'server_time', 211, 1,
                           max_age_ns=100) is None
    assert timeline.select('bybit', 'http_server_time', 'server_time', 311, 0,
                           max_age_ns=100) is None
    timeline.add(evidence(available=400))
    assert timeline.select('bybit', 'http_server_time', 'server_time', 300, 0,
                           max_age_ns=100) == evidence()
    timeline.add(evidence(available=250, epoch=1))  # wall clock can step backward
    assert timeline.select('bybit', 'http_server_time', 'server_time', 250, 1,
                           max_age_ns=100) == evidence(available=250, epoch=1)


def test_replay_only_exposes_probe_after_capture_record_and_in_matching_epoch():
    replay = Replay()
    probe = dict(evidence().__dict__, status='ok')
    replay.process({'kind': 'clock_probe', 'source': 'collector', 'received_ns': 250,
                    'evidence': probe}, 250)
    assert replay.clock_valid
    assert replay.clock_evidence.select('bybit', 'http_server_time', 'server_time',
                                        249, 0, max_age_ns=100) is None
    assert replay.clock_evidence.select('bybit', 'http_server_time', 'server_time',
                                        250, 0, max_age_ns=100) is not None
    assert replay.clock_evidence.select('bybit', 'websocket_envelope', 'ts',
                                        250, 0, max_age_ns=100) is None
    replay.process({'kind': 'clock_step', 'source': 'collector', 'received_ns': 260}, 260)
    assert replay.clock_evidence.select('bybit', 'http_server_time', 'server_time',
                                        260, replay.clock_epoch, max_age_ns=100) is None
    replay.process({'kind': 'clock_probe', 'source': 'collector', 'received_ns': 270,
                    'evidence': []}, 270)
    assert replay.diagnostics['clock_probe_invalid'] == 1


def test_inconsistent_probe_and_wall_step_cannot_supply_evidence():
    row = dict(evidence().__dict__)
    row.update(status='ok', offset_lower_ns=300)
    try:
        ClockEvidence.from_probe(row)
    except ValueError as exc:
        assert 'inconsistent' in str(exc)
    else:
        raise AssertionError('accepted inconsistent clock bounds')
    row.update(offset_lower_ns=299, received_monotonic_ns=999)
    try:
        ClockEvidence.from_probe(row)
    except ValueError as exc:
        assert 'local clock' in str(exc)
    else:
        raise AssertionError('accepted mismatched elapsed time')


def test_bounded_event_age_arrival_window_and_dwell_are_conservative():
    bounds = event_interval(1000, evidence())
    assert bounds == (599, 701)
    assert arrival_class(bounds, 598) == 'impossible'
    assert arrival_class(bounds, 650) == 'ambiguous'
    assert arrival_class(bounds, 701) == 'possible'
    assert quote_freshness(bounds, 701, 900, max_age_ns=300) == 'stale_or_ambiguous'
    assert quote_freshness(bounds, 701, 899, max_age_ns=300) == 'fresh'
    assert quote_freshness(bounds, 701, 700, max_age_ns=300) == 'unavailable'
    assert window_membership(bounds, 600, 800) == 'ambiguous'
    assert window_membership(bounds, 599, 701) == 'ambiguous'
    assert window_membership(bounds, 599, 701, left_inclusive=True) == 'in'
    assert window_membership(bounds, 702, 800) == 'out'
    assert dwell_complete(bounds, 1000, dwell_ns=300) == 'ambiguous'
    assert dwell_complete(bounds, 1001, dwell_ns=300) == 'in'
    assert receipt_membership(700, 600, 800) == 'in'
    assert receipt_membership(600, 600, 800) == 'out'
    assert receipt_membership(600, 600, 800, left_inclusive=True) == 'in'
    assert receipt_membership(700, 600, 800, same_epoch=False) == 'unknown'


def test_missing_domain_evidence_never_turns_into_zero_offset():
    assert event_interval(1000, None) is None
    assert arrival_class(None, 1000) == 'unknown'
    assert quote_freshness(None, 1000, 1000) == 'unknown'
    assert window_membership(None, 0, 1000) == 'unknown'
    assert dwell_complete(None, 1000) == 'unknown'


def test_receipt_jitter_moves_candidate_b_window_but_never_backdates_availability():
    bounds = (900, 920)
    assert window_membership(bounds, 910, 1000) == 'ambiguous'
    assert receipt_membership(1000, 910, 1000) == 'in'
    assert receipt_membership(1001, 910, 1000) == 'out'
    assert quote_freshness(bounds, 1001, 1000) == 'unavailable'
    assert quote_freshness(bounds, 1000, 1000) == 'fresh'


def test_clock_probe_failure_is_explicit_and_not_usable(monkeypatch):
    from mfsm_e001 import timing
    def failed_request(*args, **kwargs):
        raise TimeoutError('simulated timeout')
    monkeypatch.setattr(timing.urllib.request, 'urlopen', failed_request)
    result = timing.probe_server_clock('bybit')
    assert result['status'] == 'error'
    assert result['error_type'] == 'TimeoutError'
    assert result['received_ns'] >= result['request_start_ns']
    replay = Replay()
    replay.process({'kind': 'clock_probe', 'source': 'collector',
                    'received_ns': result['available_ns'], 'evidence': result},
                   result['available_ns'])
    assert replay.diagnostics['clock_probe_error'] == 1
    assert not replay.clock_evidence.rows


def test_timing_audit_keeps_legacy_and_receipt_candidates_separate(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    from audit_e001_timing import audit
    store = CaptureStore(tmp_path, max_bytes=100_000)
    records = [
        ('connected', 1_000_000_000, 'binance_spot', 'b', {}),
        ('connected', 1_000_000_001, 'bybit_spot', 'a', {}),
        ('rest_snapshot', 1_000_000_002, 'binance_spot', 'b',
         {'url': SNAPSHOT_URL, 'raw': json.dumps({'lastUpdateId': 10,
                                                   'bids': [['99', '1']], 'asks': [['101', '1']]})}),
        ('ws_message', 1_000_000_003, 'binance_spot', 'b',
         {'raw': json.dumps({'stream': 'btcusdt@depth@100ms', 'data': {
             'e': 'depthUpdate', 'E': 1000, 's': 'BTCUSDT', 'U': 11, 'u': 11,
             'b': [['99', '1']], 'a': [['101', '1']]}})}),
        ('ws_message', 1_099_668_141, 'bybit_spot', 'a',
         {'raw': json.dumps({'topic': 'orderbook.1.BTCUSDT', 'type': 'snapshot',
                             'ts': 1100, 'data': {'s': 'BTCUSDT', 'u': 1, 'seq': 1,
                                                   'b': [['99', '1']], 'a': [['101', '1']]}})}),
        ('noop', 3_000_000_000, 'collector', None, {}),
    ]
    for number, (kind, received, source, connection, fields) in enumerate(records):
        store.append({'schema': 'E001-capture-v1', 'kind': kind, 'received_ns': received,
                      'source': source, 'connection_id': connection,
                      'record_id': number, **fields})
    store.append({'schema': 'E001-capture-v1', 'kind': 'run_stopped',
                  'received_ns': 3_000_000_001})
    store.close()
    manifest = tmp_path/f'{store.run_id}.manifest.json'
    atomic_json(manifest, {'schema': 'E001-capture-v1', 'asset': 'BTC',
                           'symbol': 'BTCUSDT', 'run_id': store.run_id,
                           'status': 'duration_reached', 'records_written': store.records,
                           'records_emitted': len(records)})
    report = audit(manifest)
    assert report['first_envelope_negative']['lag_ns'] == -331_859
    assert report['grid_counts']['legacy_valid_composite'] == 0
    assert report['grid_counts']['legacy_clock_invalid'] == 2
    assert report['grid_counts']['candidate_b_receipt_quote_opportunity'] == 2
    assert report['candidate_b']['source_freshness_certified'] is False
    assert report['candidate_a']['qualifying_grid_seconds'] == 0
    capture = CaptureInput(manifest)
    candidate = CaptureFeatureReplay(timing_candidate='receipt_diagnostic')
    rows = list(feature_rows(capture.records(), [2], candidate))
    assert candidate.states[2]['spot'] == Decimal('100')
    assert rows[0]['primary_eligible'] is False
