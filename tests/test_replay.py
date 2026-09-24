from decimal import Decimal as D
import json

import pytest

from mfsm_e001.collect import SNAPSHOT_URL
from mfsm_e001.replay import (NS, BinanceBook, BybitBook, CaptureInput, Replay, ReplayError,
                              Ticker, replay_grid)
from mfsm_e001.capture_store import CaptureStore, atomic_json


def delta(first, last, *, event_ms=1000, bids=(), asks=()):
    return {'s': 'BTCUSDT', 'e': 'depthUpdate', 'U': first, 'u': last, 'E': event_ms,
            'b': list(bids), 'a': list(asks)}


def snapshot(last=10):
    return {'lastUpdateId': last, 'bids': [['99.9', '1'], ['99', '2']],
            'asks': [['100.1', '1'], ['101', '2']]}


def bybit(kind='snapshot', u=1, seq=1, ts=1000, bids=None, asks=None):
    return {'topic': 'orderbook.50.BTCUSDT', 'type': kind, 'ts': ts,
            'data': {'s': 'BTCUSDT', 'u': u, 'seq': seq,
                     'b': [['99.9', '1'], ['99', '2']] if bids is None else bids,
                     'a': [['100.1', '1'], ['101', '2']] if asks is None else asks}}


def test_binance_buffer_bridge_is_only_available_after_snapshot_receipt():
    book = BinanceBook()
    book.delta(delta(8, 10), NS)
    book.delta(delta(10, 12, bids=[['99.9', '3']]), NS + 1)
    assert not book.ready
    book.snapshot(snapshot(), 2*NS)
    assert book.ready and book.last_id == 12
    assert book.bids[D('99.9')] == 3
    assert not book.quote(2*NS-1)['valid']
    assert book.quote(2*NS)['valid']


def test_binance_snapshot_without_bridge_never_supplies_quote_timestamp():
    book = BinanceBook()
    book.snapshot(snapshot(), NS)
    assert not book.quote(2*NS)['valid']
    book.delta(delta(11, 12), 2*NS)
    assert book.quote(2*NS)['valid']


def test_binance_rejects_stale_snapshot_and_gap_until_new_snapshot():
    book = BinanceBook()
    book.delta(delta(20, 21), NS)
    with pytest.raises(ReplayError, match='snapshot_too_old'):
        book.snapshot(snapshot(10), 2*NS)
    book.delta(delta(22, 23), 3*NS)
    assert not book.ready
    book.snapshot(snapshot(23), 4*NS)
    book.delta(delta(24, 25), 4*NS)
    assert book.ready
    with pytest.raises(ReplayError, match='sequence_gap'):
        book.delta(delta(27, 28), 4*NS)


def test_binance_deep_changes_and_duplicate_updates_do_not_refresh_quote():
    book = BinanceBook()
    book.snapshot(snapshot(), NS)
    book.delta(delta(11, 12), NS)
    book.delta(delta(13, 14, event_ms=5000, bids=[['98', '9']]), 5*NS)
    book.delta(delta(13, 14, event_ms=6000), 6*NS)
    assert book.quote(6*NS)['valid']
    assert not book.quote(6*NS+1)['valid']
    assert book.quote_event_ns == NS


def test_binance_sparse_outside_updates_do_not_expand_known_depth_band():
    book = BinanceBook()
    shallow = {'lastUpdateId': 10, 'bids': [['99.9', '1']], 'asks': [['100.1', '1']]}
    book.snapshot(shallow, NS)
    book.delta(delta(11, 12, bids=[['99', '9']], asks=[['101', '9']]), NS)
    view = book.view(NS)
    assert not view['bid_band_covered'] and view['bid_notional_25bps'] is None
    assert view['observed_bid_notional_25bps'] == D('99.9')


def test_bybit_absolute_sizes_deletion_trim_and_reset():
    book = BybitBook(2)
    book.update(bybit(), NS)
    book.update(bybit('delta', 20, 100, bids=[['99.9', '3'], ['99.8', '4']], asks=[]), NS)
    assert book.bids == {D('99.9'): D('3'), D('99.8'): D('4')}
    book.update(bybit('delta', 21, 200, bids=[['99.9', '0']], asks=[]), NS)
    assert D('99.9') not in book.bids
    book.update(bybit(u=1, seq=1), NS)
    assert book.bids[D('99.9')] == 1
    assert book.view(NS)['bid_band_covered']


def test_bybit_repeated_l1_snapshot_does_not_extend_quote_age():
    book = BybitBook(1)
    book.update(bybit(), NS)
    book.update(bybit(ts=5000), 5*NS)
    assert book.quote_event_ns == NS
    assert not book.quote(6*NS+1)['valid']


def test_ticker_missing_fields_preserve_value_and_own_availability():
    ticker = Ticker()
    ticker.update({'type': 'snapshot', 'cs': 1, 'ts': 1000,
                   'data': {'openInterest': '1', 'markPrice': '100'}}, NS)
    ticker.update({'type': 'delta', 'cs': 3, 'ts': 2000, 'data': {'markPrice': '101'}}, 2*NS)
    assert ticker.fields['openInterest'] == {'value': '1', 'source_event_ns': NS, 'available_ns': NS}
    assert ticker.fields['markPrice']['available_ns'] == 2*NS
    ticker.update({'type': 'snapshot', 'cs': 1, 'ts': 3000, 'data': {'markPrice': '102'}}, 3*NS)
    assert 'openInterest' not in ticker.fields
    ticker.invalidate('disconnect')
    with pytest.raises(ReplayError, match='without_snapshot'):
        ticker.update({'type': 'delta', 'cs': 4, 'ts': 4000, 'data': {}}, 4*NS)


def row(kind, time, source='bybit_spot', connection='a', **kw):
    return {'kind': kind, 'received_ns': time, 'source': source, 'connection_id': connection, **kw}


def test_disconnect_and_old_connection_frames_cannot_revive_state():
    replay = Replay()
    replay.process(row('connected', NS), NS)
    msg = bybit();msg['topic'] = 'orderbook.1.BTCUSDT'
    replay.process(row('ws_message', NS, raw=json.dumps(msg)), NS)
    assert replay.grid(1)['quotes']['bybit']['valid']
    replay.process(row('disconnected', NS+1), NS+1)
    replay.process(row('ws_message', 2*NS, raw=json.dumps(msg)), 2*NS)
    assert not replay.grid(2)['quotes']['bybit']['valid']
    assert replay.diagnostics['message_outside_connection'] == 1


def test_grid_does_not_use_quote_received_one_nanosecond_after_boundary():
    msg = bybit();msg['topic'] = 'orderbook.1.BTCUSDT'
    rows = [row('connected', NS), row('ws_message', NS+1, raw=json.dumps(msg)), row('noop', 2*NS)]
    grid = list(replay_grid(rows, Replay()))
    assert not grid[0]['quotes']['bybit']['valid']
    assert grid[1]['quotes']['bybit']['valid']


def test_delayed_rest_result_cannot_be_backdated_in_capture_order():
    rows = [row('connected', NS, 'binance_spot'),
            row('ws_message', 2*NS, 'binance_spot', raw=json.dumps({'stream': 'btcusdt@depth@100ms',
                                                               'data': delta(10, 11)})),
            row('noop', 4*NS),
            row('rest_snapshot', 3*NS, 'binance_spot', url=SNAPSHOT_URL, raw=json.dumps(snapshot())),
            row('noop', 5*NS)]
    replay = Replay()
    grid = list(replay_grid(rows, replay))
    assert not grid[2]['quotes']['binance']['valid']  # second 3
    assert grid[3]['quotes']['binance']['available_ns'] == 4*NS
    assert replay.diagnostics['receipt_order_clamped'] == 1


def test_clock_step_invalidates_composite_and_eth_scope_fails():
    replay = Replay()
    replay.process(row('clock_step', NS, 'collector', None), NS)
    assert not replay.grid(1)['clock_valid']
    replay.process(row('connected', NS), NS)
    msg = bybit();msg['data']['s'] = 'ETHUSDT'
    with pytest.raises(ReplayError, match='non-BTC'):
        replay.process(row('ws_message', NS, raw=json.dumps(msg)), NS)


def test_capture_prefix_freezes_sealed_files_and_checks_tampering(tmp_path):
    store = CaptureStore(tmp_path, max_bytes=100000)
    store.append({'schema': 'E001-capture-v1', 'kind': 'noop', 'received_ns': NS, 'record_id': 0})
    store.seal()
    manifest = tmp_path/'run.manifest.json'
    atomic_json(manifest, {'run_id': store.run_id, 'asset': 'BTC', 'symbol': 'BTCUSDT',
                          'schema': 'E001-capture-v1', 'status': 'running'})
    with pytest.raises(ReplayError, match='sealed-prefix'):
        CaptureInput(manifest)
    frozen = CaptureInput(manifest, sealed_prefix=True)
    store.append({'schema': 'E001-capture-v1', 'kind': 'noop', 'received_ns': 2*NS, 'record_id': 1})
    store.close()
    assert len(list(frozen.records())) == 1
    limited = CaptureInput(manifest, sealed_prefix=True, segment_limit=1)
    assert len(list(limited.records())) == 1
    with pytest.raises(ReplayError, match='segment limit'):
        CaptureInput(manifest, sealed_prefix=True, segment_limit=3)
    first = frozen.segments[0]
    first.write_bytes(first.read_bytes()+b'bad')
    with pytest.raises(ReplayError, match='integrity'):
        list(frozen.records())


def test_future_source_time_preserves_sequence_state_but_blocks_primary_grid():
    replay = Replay()
    replay.process(row('connected', NS), NS)
    msg = bybit(ts=4000);msg['topic'] = 'orderbook.1.BTCUSDT'
    replay.process(row('ws_message', NS, raw=json.dumps(msg)), NS)
    view = replay.grid(1)
    assert view['books']['bybit_spot:orderbook.1.BTCUSDT']['ready']
    assert not view['books']['bybit_spot:orderbook.1.BTCUSDT']['receipt_clock_valid']
    assert view['composite_price'] is None and not view['clock_valid']
    assert replay.diagnostics['bybit_spot:source_event_after_receipt'] == 1


def test_replay_gap_invalidates_binance_until_new_snapshot_and_bridge():
    replay = Replay()
    replay.process(row('connected', NS, 'binance_spot'), NS)
    def snap(t):
        replay.process(row('rest_snapshot', t, 'binance_spot', url=SNAPSHOT_URL,
                           raw=json.dumps(snapshot())), t)
    def update(first, last):
        replay.process(row('ws_message', NS, 'binance_spot', raw=json.dumps({
            'stream': 'btcusdt@depth@100ms', 'data': delta(first, last)})), NS)
    snap(NS)
    update(11, 12)
    update(14, 15)
    assert not replay.grid(1)['quotes']['binance']['valid']
    update(16, 17)
    assert not replay.grid(1)['quotes']['binance']['valid']
    snap(NS)
    update(11, 12)
    assert replay.grid(1)['quotes']['binance']['valid']
    assert replay.diagnostics['binance_sequence_gap'] == 1


def test_replay_keeps_depth_streams_distinct_and_ticker_clears_on_reconnect():
    replay = Replay()
    replay.process(row('connected', NS, 'bybit_linear'), NS)
    for depth in (50, 1000):
        msg = bybit();msg['topic'] = f'orderbook.{depth}.BTCUSDT'
        replay.process(row('ws_message', NS, 'bybit_linear', raw=json.dumps(msg)), NS)
    assert len(replay.books) == 2
    message = {'topic': 'tickers.BTCUSDT', 'type': 'snapshot', 'cs': 1, 'ts': 1000,
               'data': {'symbol': 'BTCUSDT', 'markPrice': '100'}}
    replay.process(row('ws_message', NS, 'bybit_linear', raw=json.dumps(message)), NS)
    replay.process(row('connected', 2*NS, 'bybit_linear', 'b'), 2*NS)
    assert not replay.books and not replay.ticker.ready
    assert replay.ticker.fields == {}


def test_clock_probe_bounds_do_not_assume_symmetric_latency(monkeypatch):
    from pathlib import Path
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    from probe_e001_clock import offset_interval
    assert offset_interval(100, 200, 100, 500, 1) == {'offset_lower_ns': 299, 'offset_upper_ns': 401}
    with pytest.raises(ValueError, match='clock moved'):
        offset_interval(100, 200_000_200, 100, 500)


def test_primary_composite_uses_equal_weights_and_exact_five_second_expiry():
    replay = Replay()
    replay.process(row('connected', NS, 'binance_spot'), NS)
    replay.process(row('rest_snapshot', NS, 'binance_spot', url=SNAPSHOT_URL,
                       raw=json.dumps(snapshot())), NS)
    replay.process(row('ws_message', NS, 'binance_spot', raw=json.dumps({
        'stream': 'btcusdt@depth@100ms', 'data': delta(11, 12)})), NS)
    replay.process(row('connected', NS), NS)
    message = bybit(bids=[['100', '1']], asks=[['100.2', '1']])
    message['topic'] = 'orderbook.1.BTCUSDT'
    replay.process(row('ws_message', NS, raw=json.dumps(message)), NS)
    assert replay.grid(1)['composite_price'] == D('100.05')
    assert replay.grid(6)['composite_price'] == D('100.05')
    assert replay.grid(7)['composite_price'] is None


def test_replay_grid_artifact_is_deterministic_for_same_sealed_input(tmp_path, monkeypatch):
    from pathlib import Path
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    from replay_e001_capture import run
    capture_dir = tmp_path/'capture'
    store = CaptureStore(capture_dir, max_bytes=100000)
    for index in range(3):
        store.append({'schema': 'E001-capture-v1', 'kind': 'noop',
                      'received_ns': (index+1)*NS, 'record_id': index})
    store.close()
    manifest = capture_dir/'run.manifest.json'
    atomic_json(manifest, {'run_id': store.run_id, 'asset': 'BTC', 'symbol': 'BTCUSDT',
                          'schema': 'E001-capture-v1', 'status': 'running'})
    a = run(manifest, tmp_path/'a', sealed_prefix=True, segment_limit=1)
    b = run(manifest, tmp_path/'b', sealed_prefix=True, segment_limit=1)
    assert a['grid_sha256'] == b['grid_sha256']
    assert a['counts']['valid_composite_seconds'] == 0
