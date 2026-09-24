"""Hand-computed contracts for live, receipt-aware feature extraction."""

from decimal import Decimal as D
import importlib
import json

import pytest

from mfsm_e001.replay import NS


def record(kind, received, source='bybit_linear', connection='c', **extra):
    return dict(kind=kind, received_ns=received, source=source,
                connection_id=connection, **extra)


def message(payload, received):
    return record('ws_message', received, raw=json.dumps(payload))


def connected():
    return [record('connected', 0), message({'op': 'subscribe', 'success': True}, 0)]


def trade(event_ms, received, ident='a', side='Sell', price='100', size='2'):
    return message({'topic': 'publicTrade.BTCUSDT', 'ts': event_ms, 'data': [
        {'s': 'BTCUSDT', 'T': event_ms, 'i': ident, 'S': side, 'p': price, 'v': size}]}, received)


def book(t, *, bids=(), asks=(), snapshot=False, seq=None):
    return message({'topic': 'orderbook.1000.BTCUSDT',
                    'type': 'snapshot' if snapshot else 'delta', 'ts': int(t*1000),
                    'data': {'s': 'BTCUSDT', 'u': seq or int(t*1000)+1,
                             'seq': seq or int(t*1000)+1, 'b': list(bids), 'a': list(asks)}},
                   int(t*NS))


def snapshot(t=0, **extra):
    return book(t, snapshot=True, bids=[['99.9', '1'], ['99', '2']],
                asks=[['100.1', '1'], ['101', '2']], **extra)


def extract(rows, second):
    module = importlib.import_module('mfsm_e001.capture_features')
    rows = sorted([*rows, record('noop', second*NS)], key=lambda r: r['received_ns'])
    return list(module.feature_rows(rows, [second]))[0]


def test_trade_windows_obey_receipt_boundary_event_window_and_duplicate_ids():
    rows = connected() + [trade(2000, 2*NS), trade(2000, 3*NS),
                          trade(1000, 4*NS, 'left-edge'),
                          trade(5000, 6*NS+1, 'too-late')]
    output = extract(rows, 6)
    assert output['raw']['aggressive_sell_notional_5s'] == D('200')
    assert output['raw']['aggressive_sell_rate_5s'] == D('40')
    assert output['raw']['aggressive_buy_notional_5s'] == 0
    assert output['latest_input_available_ns'] <= 6*NS


def test_quiet_subscribed_flow_is_zero_but_unknown_history_is_missing():
    assert extract(connected(), 5)['raw']['aggressive_sell_notional_5s'] == 0
    output = extract([record('connected', NS)], 5)
    assert output['raw']['aggressive_sell_notional_5s'] is None
    assert output['missing_reasons']['aggressive_sell_notional_5s']


def test_disconnect_reconnect_does_not_fill_missing_window_with_zero():
    rows = connected() + [record('disconnected', 3*NS), record('connected', 4*NS, connection='d'),
                         record('ws_message', 4*NS, connection='d',
                                raw=json.dumps({'op': 'subscribe', 'success': True}))]
    assert extract(rows, 6)['raw']['aggressive_sell_notional_5s'] is None
    assert extract(rows, 9)['raw']['aggressive_sell_notional_5s'] == 0


def test_liquidation_side_and_size_preserved_without_bankruptcy_notional():
    liq = message({'topic': 'allLiquidation.BTCUSDT', 'ts': 2000, 'data': [
        {'s': 'BTCUSDT', 'T': 2000, 'S': 'Buy', 'v': '3', 'p': '50'}]}, 2*NS)
    output = extract(connected()+[liq], 5)
    assert output['raw']['liquidation_sell_size_base_5s'] == D('3')
    assert output['raw']['liquidation_sell_notional_5s'] is None
    assert output['raw']['cancel_bid_rate_5s'] is None
    assert output['limitations']['aggressive_sell_may_include_liquidations']


def test_conflicting_trade_ids_fail_instead_of_changing_the_total():
    with pytest.raises(ValueError, match='conflicting duplicate trade'):
        extract(connected()+[trade(1000, NS), trade(1000, 2*NS, size='9')], 5)


def test_persistence_charges_reductions_and_uses_full_fifteen_seconds():
    rows = connected()+[snapshot(), book(1, bids=[['99.9', '3']]),
                        book(1.5, bids=[['99.9', '2']])]
    rows += [book(t) for t in range(2, 16)]
    output = extract(rows, 15)
    assert output['raw']['persistent_bid_add_rate_15s'] == D('99.9')/15
    assert output['raw']['gross_bid_add_rate_15s'] == D('199.8')/15
    assert output['raw']['observed_bid_decrease_rate_15s'] == D('99.9')/15
    assert output['raw']['cancel_bid_rate_15s'] is None


def test_persistence_censors_unfinished_dwell_and_replenishment_after_removal():
    rows = connected()+[snapshot(), book(1, bids=[['99.9', '3']]),
                        book(1.5, bids=[['99.9', '1']]), book(1.7, bids=[['99.9', '3']])]
    rows += [book(t) for t in range(2, 15)]
    rows += [book(14.5, bids=[['99.9', '5']]), book(15)]
    assert extract(rows, 15)['raw']['persistent_bid_add_rate_15s'] == D('199.8')/15


@pytest.mark.parametrize('disturbance', ['reset', 'partial', 'sequence_gap'])
def test_book_reset_partial_band_or_sequence_failure_make_required_window_missing(disturbance):
    rows = connected()+[snapshot()] + [book(t) for t in range(1, 10)]
    if disturbance == 'reset':
        rows.append(snapshot(10))
    elif disturbance == 'partial':
        rows.append(book(10, bids=[['99', '0']]))
    else:
        rows.append(book(10, seq=2))
    rows += [book(t) for t in range(11, 16)]
    output = extract(rows, 15)
    assert output['raw']['persistent_bid_add_rate_15s'] is None
    assert output['raw']['capacity_proxy'] is None


def test_future_inputs_do_not_change_decision_features():
    rows = connected()+[snapshot()]+[book(t) for t in range(1, 16)]
    a = extract(rows, 15)
    b = extract(rows+[trade(15000, 15*NS+1), book(16, bids=[['99.9', '1000']])], 15)
    assert a == b


def test_clock_failure_blocks_every_numeric_feature():
    rows = connected()+[snapshot(), record('clock_step', 3*NS, 'collector', None)]
    output = extract(rows, 5)
    assert not output['clock_valid']
    assert all(value is None for value in output['raw'].values())
    assert all(value is None for value in output['shared'].values())


def test_receipt_diagnostic_counts_future_source_trade_at_receipt_window_only():
    from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
    rows = connected() + [trade(6000, 5*NS, ident='ahead'),
                          trade(6000, 6*NS+1, ident='too_late'),
                          record('noop', 7*NS)]
    strict = list(feature_rows(rows, [6], CaptureFeatureReplay()))[0]
    receipt = list(feature_rows(rows, [6],
                                CaptureFeatureReplay(timing_candidate='receipt_diagnostic')))[0]
    assert strict['raw']['aggressive_sell_notional_5s'] is None
    assert receipt['raw']['aggressive_sell_notional_5s'] == D('200')
    assert receipt['strict_cross_clock_valid'] is False
    assert receipt['source_freshness_certified'] is False
    assert receipt['primary_eligible'] is False and not receipt['model_ready']


def test_receipt_diagnostic_book_dwell_uses_receipt_times_and_keeps_economics_missing():
    from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
    future_delta = book(1.2, bids=[['99.9', '2']], asks=[])
    payload = json.loads(future_delta['raw'])
    payload['ts'] += 1  # source timestamp is 1 ms after actual receipt
    future_delta['raw'] = json.dumps(payload)
    rows = connected() + [snapshot(0), future_delta, record('noop', 6*NS)]
    receipt = list(feature_rows(rows, [6],
                                CaptureFeatureReplay(timing_candidate='receipt_diagnostic')))[0]
    assert receipt['raw']['persistent_bid_add_rate_5s'] > 0
    assert receipt['raw']['liquidation_sell_notional_5s'] is None
    assert receipt['raw']['cancel_bid_rate_5s'] is None
    assert receipt['primary_eligible'] is False


def test_receipt_diagnostic_clock_step_still_blocks_every_numeric_feature():
    from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
    rows = connected() + [snapshot(), record('clock_step', 3*NS, 'collector', None),
                          record('noop', 5*NS)]
    result = list(feature_rows(rows, [5],
                               CaptureFeatureReplay(timing_candidate='receipt_diagnostic')))[0]
    assert result['clock_valid'] is False
    assert all(value is None for value in result['raw'].values())
    assert result['primary_eligible'] is False


def test_receipt_v1_reports_missing_delay_proof_and_keeps_late_packet_out():
    from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
    rows = connected() + [trade(5001, 5*NS, ident='on_time'),
                          trade(6000, 6*NS+1, ident='after_decision'),
                          record('noop', 7*NS)]
    result = list(feature_rows(rows, [6], CaptureFeatureReplay(timing_candidate='receipt_v1')))[0]
    assert result['schema'] == 'E001-live-features-receipt-candidate-1'
    assert result['raw']['aggressive_sell_notional_5s'] == D('200')
    assert result['timing_quality']['state'] == 'warming'
    assert 'independent_utc_clock_evidence_missing' in result['timing_quality']['reasons']
    assert 'websocket_role_delay_bound_missing' in result['timing_quality']['reasons']
    assert result['timing_quality']['source_delay_bound_ns'] is None
    assert result['timing_quality']['max_observed_source_lead_ns'] == 1_000_000
    assert result['primary_eligible'] is False and result['model_ready'] is False


def test_receipt_v1_protective_cutoff_rejects_gross_source_clock_lead():
    from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
    rows = connected() + [trade(8300, 5*NS), record('noop', 7*NS)]
    result = list(feature_rows(rows, [6], CaptureFeatureReplay(timing_candidate='receipt_v1')))[0]
    assert result['timing_quality']['state'] == 'quarantined'
    assert result['timing_quality']['max_observed_source_lead_ns'] == 3_300_000_000
    assert 'source_clock_lead_exceeds_protective_cutoff' in result['timing_quality']['reasons']
    assert result['primary_eligible'] is False


def test_receipt_v1_grid_exposes_same_spot_reference_used_by_features():
    from mfsm_e001.capture_features import CaptureFeatureReplay
    from mfsm_e001.collect import SNAPSHOT_URL
    from mfsm_e001.replay import replay_grid
    rows = [record('connected', 0, 'binance_spot'),
            record('connected', 0, 'bybit_spot'),
            record('rest_snapshot', 0, 'binance_spot', url=SNAPSHOT_URL,
                   raw=json.dumps({'lastUpdateId': 10,
                                   'bids': [['99.9', '1']], 'asks': [['100.1', '1']]})),
            record('ws_message', NS, 'binance_spot', raw=json.dumps({
                'stream': 'btcusdt@depth@100ms',
                'data': {'e': 'depthUpdate', 's': 'BTCUSDT', 'E': 5000,
                         'U': 11, 'u': 11, 'b': [], 'a': []}})),
            record('ws_message', NS, 'bybit_spot', raw=json.dumps({
                'topic': 'orderbook.1.BTCUSDT', 'type': 'snapshot', 'ts': 5000,
                'data': {'s': 'BTCUSDT', 'u': 1, 'seq': 1,
                         'b': [['99.9', '1']], 'a': [['100.1', '1']]}})),
            record('noop', 7*NS)]
    replay = CaptureFeatureReplay(timing_candidate='receipt_v1')
    grid = {row['second']: row for row in replay_grid(rows, replay)}
    assert grid[2]['strict_composite_price'] is None
    assert grid[2]['composite_price'] == D('100')
    assert grid[2]['quotes']['binance']['age_ns'] == NS
    assert replay.states[2]['spot'] == grid[2]['composite_price']
    assert grid[6]['composite_price'] == D('100')
    assert grid[7]['composite_price'] is None


def test_receipt_v1_quarantines_clock_step_and_marks_loop_gap_history():
    from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
    gap = connected() + [record('event_loop_delay', 3*NS, 'collector', None),
                         record('noop', 5*NS)]
    candidate = CaptureFeatureReplay(timing_candidate='receipt_v1')
    result = list(feature_rows(gap, [5], candidate))[0]
    assert result['timing_quality']['state'] == 'warming'
    assert 'required_receipt_history_incomplete' in result['timing_quality']['reasons']
    assert result['timing_quality']['latest_disruption_ns'] == 3*NS
    assert result['timing_quality']['latest_disruption_kind'] == 'event_loop_delay'
    stepped = connected() + [record('clock_step', 3*NS, 'collector', None),
                             record('noop', 5*NS)]
    result = list(feature_rows(stepped, [5],
                    CaptureFeatureReplay(timing_candidate='receipt_v1')))[0]
    assert result['timing_quality']['state'] == 'quarantined'
    assert result['timing_quality']['clock_epoch'] == 1
    assert all(value is None for value in result['raw'].values())


@pytest.mark.parametrize('message_time', [5000, 5001])
def test_future_trade_clock_is_reported_without_aborting_earlier_diagnostics(message_time):
    future = trade(5001, 5*NS)
    payload = json.loads(future['raw'])
    payload['ts'] = message_time
    future['raw'] = json.dumps(payload)
    output = extract(connected()+[future], 6)
    assert not output['clock_valid']
    assert all(value is None for value in output['raw'].values())
    assert set(output['missing_reasons'].values()) == {'receipt_clock_review_required'}


def test_pretrigger_denominators_use_exact_1800_grid_points_and_shared_normalization():
    module = importlib.import_module('mfsm_e001.capture_features')
    states = {}
    for s in range(1816):
        states[s] = {'second': s, 'depth_bid': D('100') if s < 1800 else D('10000'),
                     'oi': D('10') if s < 1800 else D('1000')}
    scales = module.pretrigger_scales(states, 1815)
    assert scales == {'depth': D('100'), 'oi': D('10')}
    del states[900]
    assert module.pretrigger_scales(states, 1815) == {'depth': None, 'oi': None}


def test_dimensionless_model_inputs_exclude_raw_notionals_and_share_every_component():
    module = importlib.import_module('mfsm_e001.capture_features')
    raw = {'depth_bid': D('200'), 'depth_ask': D('100'),
           'persistent_bid_add_rate_15s': D('10'), 'aggressive_sell_notional_15s': D('50'),
           'aggressive_sell_notional_30s': D('50'), 'liquidation_sell_notional_30s': None,
           'oi': D('20'), 'funding_bps': D('1')}
    shared, mfsm = module.normalized_features(raw, {'depth': D('100'), 'oi': D('10')})
    assert shared['depth_bid_relative'] == D('2')
    assert shared['aggressive_sell_notional_15s_relative_depth'] == D('0.5')
    assert shared['oi_relative_pretrigger'] == D('1')
    assert mfsm['sell_pressure_ratio_contaminated'] == D('0.1')
    assert mfsm['liquidation_pressure_ratio'] is None
    assert all(mfsm[k] == v for k, v in shared.items())
    assert 'oi' not in shared and 'depth_bid' not in shared
    assert 'aggressive_sell_notional_15s' not in shared


def test_pressure_ratios_use_thirty_second_flows_not_fifteen_second_replenishment_window():
    module = importlib.import_module('mfsm_e001.capture_features')
    raw = {'depth_bid': D('200'), 'persistent_bid_add_rate_15s': D('10'),
           'aggressive_sell_notional_15s': D('0'), 'aggressive_sell_notional_30s': D('50'),
           'liquidation_sell_notional_15s': D('0'), 'liquidation_sell_notional_30s': D('25')}
    _, mfsm = module.normalized_features(raw, {'depth': D('100'), 'oi': None})
    assert mfsm['sell_pressure_ratio_contaminated'] == D('0.1')
    assert mfsm['liquidation_pressure_ratio'] == D('0.05')


def test_newly_revealed_price_outside_previous_book_boundary_is_not_a_known_addition():
    rows = connected()+[book(0, snapshot=True,
        bids=[['99.9', '1'], ['99.86', '1'], ['99.75', '1']],
        asks=[['100.1', '1'], ['100.25', '1']]),
        book(1, bids=[['99.9', '0'], ['99.74', '10'], ['99.70', '1']])]
    rows += [book(t) for t in range(2, 16)]
    output = extract(rows, 15)
    # Both depth bands are fully covered, but the prior size at99.74 is unknown.
    assert output['raw']['depth_bid'] == D('1197.01')
    assert output['raw']['gross_bid_add_rate_15s'] is None
    assert output['raw']['persistent_bid_add_rate_15s'] is None


def test_persistence_keeps_all_same_timestamp_additions_at_inclusive_left_edge():
    rows = connected()+[snapshot(), book(1, bids=[['99.9', '2']], seq=1001),
                        book(1, bids=[['99.9', '3']], seq=1002)]
    rows += [book(t) for t in range(2, 17)]
    assert extract(rows, 16)['raw']['persistent_bid_add_rate_15s'] == D('199.8')/15


def test_ticker_delta_retains_field_availability_and_gap_blocks_window_returns():
    rows = connected()+[message({'topic': 'tickers.BTCUSDT', 'type': 'snapshot', 'cs': 1,
                                'ts': 0, 'data': {'symbol': 'BTCUSDT', 'openInterest': '10',
                                'markPrice': '101', 'indexPrice': '100', 'fundingRate': '0.0001'}}, 0),
                        message({'topic': 'tickers.BTCUSDT', 'type': 'delta', 'cs': 2,
                                 'ts': 5000, 'data': {'symbol': 'BTCUSDT', 'markPrice': '102'}}, 5*NS)]
    output = extract(rows, 5)
    assert output['raw']['oi'] == D('10')
    assert output['raw']['mark_index_bps'] == D('200')
    assert output['raw']['funding_bps'] == D('1')
    assert output['ticker_provenance']['openInterest']['available_ns'] == 0
    assert output['raw']['return_5s'] is None


def test_stale_ticker_and_book_do_not_supply_current_scalars():
    rows = connected()+[snapshot(), message({'topic': 'tickers.BTCUSDT', 'type': 'snapshot',
        'cs': 1, 'ts': 0, 'data': {'symbol': 'BTCUSDT', 'openInterest': '10'}}, 0)]
    output = extract(rows, 6)
    assert output['raw']['oi'] is None
    assert output['raw']['depth_bid'] is None


def test_ask_additions_and_endpoint_band_exit_are_measured_separately():
    rows = connected()+[snapshot(), book(1, asks=[['100.1', '3']])]
    rows += [book(t) for t in range(2, 16)]
    result = extract(rows, 15)
    assert result['raw']['persistent_ask_add_rate_15s'] == D('200.2')/15
    assert result['raw']['persistent_bid_add_rate_15s'] == 0
    # The cohort at 100.1 is outside the band when midpoint falls to 99.
    shifted = connected()+[snapshot(), book(1, asks=[['100.1', '3']]),
        book(2, bids=[['99.9', '0'], ['99', '0'], ['98.9', '1'], ['98', '2']],
             asks=[['99.1', '1']])]+[book(t) for t in range(3, 16)]
    assert extract(shifted, 15)['raw']['persistent_ask_add_rate_15s'] == D('99.1')/15


def test_regressing_book_event_time_cannot_reorder_feature_history():
    rows = connected()+[snapshot(), book(2)]
    backwards = book(1, seq=3000)
    backwards['received_ns'] = 3*NS
    output = extract(rows+[backwards], 4)
    assert output['raw']['depth_bid'] is None
    assert output['raw']['persistent_bid_add_rate_1s'] is None


def test_capture_command_produces_deterministic_features_and_rejects_missing_decisions(tmp_path, monkeypatch):
    from pathlib import Path
    from mfsm_e001.capture_store import CaptureStore, atomic_json
    import gzip

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    module = importlib.import_module('build_e001_capture_features')
    root = tmp_path/'capture'
    store = CaptureStore(root, max_bytes=1000000)
    rows = connected()+[snapshot(), trade(2000, 2*NS)]+[book(t) for t in range(1, 7)]
    for i, row in enumerate(sorted(rows, key=lambda r: r['received_ns'])):
        store.append(dict(row, schema='E001-capture-v1', record_id=i))
    store.close()
    manifest = root/'run.manifest.json'
    atomic_json(manifest, {'schema': 'E001-capture-v1', 'asset': 'BTC', 'symbol': 'BTCUSDT',
                          'run_id': store.run_id, 'status': 'running'})
    a = module.run(manifest, tmp_path/'a', [5], sealed_prefix=True)
    b = module.run(manifest, tmp_path/'b', [5], sealed_prefix=True)
    assert a['features_sha256'] == b['features_sha256']
    assert a['rows'] == 1 and not a['model_fitted']
    assert a['segment_sha256']
    with gzip.open(a['features_path'], 'rt') as stream:
        row = json.loads(stream.readline())
    assert row['raw']['aggressive_sell_notional_5s'] == '200'
    diagnostic = module.run(manifest, tmp_path/'receipt', [5], sealed_prefix=True,
                            timing_candidate='receipt_diagnostic')
    assert diagnostic['schema'] == 'E001-live-features-receipt-diagnostic-1'
    assert diagnostic['primary_eligible_rows'] == 0
    with gzip.open(diagnostic['features_path'], 'rt') as stream:
        receipt_row = json.loads(stream.readline())
    assert receipt_row['primary_eligible'] is False
    candidate = module.run(manifest, tmp_path/'candidate', [5], sealed_prefix=True,
                           timing_candidate='receipt_v1')
    assert candidate['schema'] == 'E001-live-features-receipt-candidate-1'
    assert candidate['clock_valid_semantics'] == 'no_detected_local_wall_clock_step_only'
    assert candidate['timing_quality_states'] == {'warming': 1}
    assert candidate['primary_eligible_rows'] == 0
    comparison = importlib.import_module('compare_e001_timing_features')
    pair = comparison.compare_pair(tmp_path/'a'/'report.json', tmp_path/'receipt'/'report.json')
    assert pair['decisions'][0]['receipt_primary_eligible'] is False
    with pytest.raises(ValueError, match='outside captured grid'):
        module.run(manifest, tmp_path/'missing', [999], sealed_prefix=True)
    assert not (tmp_path/'missing'/'features.jsonl.gz').exists()
    with pytest.raises(ValueError, match='ETH'):
        module.run(manifest, tmp_path/'eth', [5], sealed_prefix=True)
    (tmp_path/'receipt'/'features.jsonl.gz').write_bytes(b'tampered')
    with pytest.raises(ValueError, match='hash mismatch'):
        comparison.compare_pair(tmp_path/'a'/'report.json', tmp_path/'receipt'/'report.json')
