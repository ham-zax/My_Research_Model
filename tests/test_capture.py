import asyncio
import json
from pathlib import Path

import pytest

from mfsm_e001.capture_health import FeedError, FeedMonitor
from mfsm_e001.capture_store import CaptureStore, StorageLimit, sha256
from mfsm_e001 import collect


def book(kind="snapshot", u=1, seq=10, symbol="BTCUSDT"):
    return {"topic": "orderbook.50.BTCUSDT", "type": kind, "ts": 1000,
            "data": {"s": symbol, "u": u, "seq": seq, "b": [["100", "1"]], "a": [["101", "1"]]}}


def test_bybit_reset_noncontiguous_ids_and_delta_without_snapshot():
    monitor = FeedMonitor("bybit_linear", ("orderbook.50.BTCUSDT",))
    with pytest.raises(FeedError, match="without snapshot"):
        monitor.inspect(book("delta", 5))
    monitor.inspect(book())
    assert monitor.inspect(book("delta", 10, 200)) == []
    with pytest.raises(FeedError, match="regression"):
        monitor.inspect(book("delta", 9, 201))
    assert monitor.inspect(book(u=1, seq=1))[0]["kind"] == "book_snapshot_reset"
    monitor.inspect(book("delta", 2, 2))


def test_scope_rejects_unrequested_symbol_and_unscoped_payload():
    monitor = FeedMonitor("bybit_linear", ("orderbook.50.BTCUSDT",))
    with pytest.raises(FeedError, match="non-BTC"):
        monitor.inspect(book(symbol="ETHUSDT"))
    with pytest.raises(FeedError, match="unscoped"):
        monitor.inspect({"data": [{"s": "ETHUSDT"}]})


def test_binance_detects_actual_range_gap_but_allows_overlapping_ranges():
    monitor = FeedMonitor("binance_spot", ("btcusdt@depth@100ms",))
    def update(first, last):
        return monitor.inspect({"stream": "btcusdt@depth@100ms", "data": {
            "s": "BTCUSDT", "e": "depthUpdate", "U": first, "u": last}})
    update(1, 10)
    update(9, 15)
    assert update(9, 15)[0]["kind"] == "duplicate_or_old_depth"
    with pytest.raises(FeedError, match="sequence gap"):
        update(17, 20)


def test_ticker_requires_initial_snapshot_after_reconnect():
    monitor = FeedMonitor("bybit_linear", ("tickers.BTCUSDT",))
    message = {"topic": "tickers.BTCUSDT", "type": "delta", "data": {"symbol": "BTCUSDT"}}
    with pytest.raises(FeedError, match="without snapshot"):
        monitor.inspect(message)
    monitor.inspect({**message, "type": "snapshot"})
    monitor.inspect(message)
    with pytest.raises(FeedError, match="rejected"):
        monitor.inspect({"op": "subscribe", "success": False})


def test_storage_rotation_hashes_and_total_budget_across_restarts(tmp_path):
    store = CaptureStore(tmp_path, max_bytes=80, segment_bytes=20)
    store.append({"a": "1234567890"})
    store.append({"a": "abcdefghij"})
    with pytest.raises(RuntimeError, match="another collector"):
        CaptureStore(tmp_path, max_bytes=80)
    store.close()
    files = sorted(tmp_path.glob("*.jsonl"))
    assert len(files) == 2
    for path in files:
        metadata = json.loads(path.with_suffix(".meta.json").read_text())
        assert metadata["sha256"] == sha256(path)
    before = {p.name: p.read_bytes() for p in files}
    restarted = CaptureStore(tmp_path, max_bytes=80)
    with pytest.raises(StorageLimit):
        restarted.append({"too_large": "x" * 80})
    restarted.close()
    assert before == {p.name: p.read_bytes() for p in files}


def test_unclean_restart_preserves_truncated_original_bytes(tmp_path):
    tail = tmp_path / "old-000001.open"
    raw = b'{"valid":true}\n{"interrupted":'
    tail.write_bytes(raw)
    store = CaptureStore(tmp_path, max_bytes=1000)
    assert store.recovered == ["old-000001.unclean"]
    assert (tmp_path / store.recovered[0]).read_bytes() == raw
    store.close()


def test_queue_overflow_is_explicit_and_does_not_overwrite():
    recorder = collect.Recorder(queue_size=1)
    recorder.emit("collector", None, "first")
    with pytest.raises(RuntimeError, match="overflow"):
        recorder.emit("collector", None, "second")
    assert recorder.queue.get_nowait()["kind"] == "first"


def test_live_transport_records_reconnect_and_drains_every_record(tmp_path, monkeypatch):
    websockets = pytest.importorskip("websockets.asyncio.server")
    async def scenario():
        connections = 0
        async def handler(ws):
            nonlocal connections
            connections += 1
            await ws.recv()  # Public subscription only.
            await ws.send(json.dumps({"op": "subscribe", "success": True}))
            await ws.send(json.dumps(book()))
            if connections == 1:
                await ws.close()
            else:
                await ws.wait_closed()
        async with websockets.serve(handler, "127.0.0.1", 0) as server:
            port = server.sockets[0].getsockname()[1]
            feed = collect.Feed("bybit_linear", f"ws://127.0.0.1:{port}", ("orderbook.50.BTCUSDT",))
            monkeypatch.setattr(collect, "FEEDS", (feed,))
            manifest_path, manifest, error = await collect.run_capture(tmp_path, duration=2.6, max_bytes=100000)
        assert error is None
        assert manifest["status"] == "duration_reached"
        assert manifest["feeds_observed"]["bybit_linear"]["connections"] == 2
        assert manifest["queued_records_not_written"] == 0
        rows = [json.loads(line) for p in sorted(tmp_path.glob("*.jsonl")) for line in p.read_text().splitlines()]
        assert len(rows) == manifest["records_written"] == manifest["records_emitted"] + 1
        assert [r["record_id"] for r in rows[:-1]] == list(range(manifest["records_emitted"]))
        assert len({r["connection_id"] for r in rows if r["kind"] == "connected"}) == 2
        assert any(r["kind"] == "connection_error" for r in rows)
        assert rows[-1]["kind"] == "run_stopped"
        monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
        from audit_e001_capture import audit
        assert audit(manifest_path)["integrity_checks_passed"]
        segment = next(tmp_path.glob("*.jsonl"))
        segment.write_bytes(segment.read_bytes() + b"tampered")
        with pytest.raises(ValueError, match="integrity failure"):
            audit(manifest_path)
    asyncio.run(scenario())


def test_capture_storage_limit_marks_run_failed_and_releases_lock(tmp_path, monkeypatch):
    pytest.importorskip("websockets")
    monkeypatch.setattr(collect, "FEEDS", ())
    _, manifest, error = asyncio.run(collect.run_capture(tmp_path, duration=.05, max_bytes=10))
    assert isinstance(error, StorageLimit)
    assert manifest["status"] == "storage_limit"
    store = CaptureStore(tmp_path, max_bytes=1000)
    store.close()


def test_heartbeat_rejects_acknowledged_but_missing_required_topics(monkeypatch):
    async def immediate(_):
        pass
    monkeypatch.setattr(collect.asyncio, "sleep", immediate)
    async def scenario():
        ack = asyncio.Event()
        ack.set()
        with pytest.raises(FeedError, match="required topic absent"):
            await collect.Recorder().heartbeat(None, collect.FEEDS[1], "test", ack, {})
    asyncio.run(scenario())


def test_raw_btc_message_preserved_before_ordering_error():
    class Socket:
        def __init__(self):
            self.messages = iter([book(), book("delta", u=1, seq=9)])
        async def recv(self):
            return json.dumps(next(self.messages))
    async def scenario():
        recorder = collect.Recorder()
        with pytest.raises(FeedError, match="regression"):
            await recorder.receive(Socket(), collect.FEEDS[2], "test", asyncio.Event(), {})
        rows = []
        while not recorder.queue.empty():
            rows.append(recorder.queue.get_nowait())
        assert len([r for r in rows if r["kind"] == "ws_message"]) == 2
    asyncio.run(scenario())


def test_queue_byte_cap_rejects_large_message_before_memory_backlog():
    recorder = collect.Recorder(queue_bytes=1024)
    with pytest.raises(RuntimeError, match="byte limit"):
        recorder.emit("collector", None, "large", raw="x" * 1024)
    assert recorder.queue.empty()
