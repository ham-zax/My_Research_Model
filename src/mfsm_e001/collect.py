"""Bounded, BTC-only public-feed recorder. No credentials or trading operations."""

import argparse
import asyncio
from collections import Counter
from dataclasses import asdict, dataclass
import importlib.metadata
import json
import math
from pathlib import Path
import signal
import time
import urllib.request
import uuid

from .capture_health import FeedError, FeedMonitor
from .capture_store import CaptureStore, StorageLimit, atomic_json, sha256


@dataclass(frozen=True)
class Feed:
    name: str
    url: str
    topics: tuple[str, ...]


FEEDS = (
    Feed("binance_spot", "wss://data-stream.binance.vision/stream?streams=btcusdt@depth@100ms/btcusdt@trade",
         ("btcusdt@depth@100ms", "btcusdt@trade")),
    Feed("bybit_spot", "wss://stream.bybit.com/v5/public/spot",
         ("orderbook.1.BTCUSDT", "orderbook.50.BTCUSDT", "publicTrade.BTCUSDT")),
    Feed("bybit_linear", "wss://stream.bybit.com/v5/public/linear",
         ("orderbook.50.BTCUSDT", "orderbook.1000.BTCUSDT", "publicTrade.BTCUSDT",
          "allLiquidation.BTCUSDT", "tickers.BTCUSDT")),
)
SNAPSHOT_URL = "https://data-api.binance.vision/api/v3/depth?symbol=BTCUSDT&limit=5000"
SCHEMA = "E001-capture-v1"


def stamp():
    return {"received_ns": time.time_ns(), "monotonic_ns": time.monotonic_ns()}


def fetch_snapshot():
    started = stamp()
    request = urllib.request.Request(SNAPSHOT_URL, headers={"User-Agent": "MFSM-E001-public-recorder/1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        raw = response.read(4_000_001)
        received = stamp()
        if len(raw) > 4_000_000:
            raise FeedError("snapshot exceeds size limit")
    payload = raw.decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data.get("lastUpdateId"), int) or not all(k in data for k in ("bids", "asks")):
        raise FeedError("invalid Binance snapshot")
    return {"kind": "rest_snapshot", "url": SNAPSHOT_URL, "request_started": started,
            **received, "raw": payload}


class Recorder:
    def __init__(self, queue_size=8192, queue_bytes=32 << 20):
        self.queue = asyncio.Queue(maxsize=queue_size)
        self.queue_byte_limit = queue_bytes
        self.queued_bytes = 0
        self.queued_sizes = {}
        self.sequence = 0
        self.stats = {f.name: {"connections": 0, "disconnects": 0, "messages": 0,
                              "topics": Counter(), "subscription_acknowledged": False}
                      for f in FEEDS}

    def emit(self, source, connection_id, kind, **fields):
        clocks = stamp()
        record = {"schema": SCHEMA, "source": source, "connection_id": connection_id,
                  "kind": kind, **clocks, **fields, "record_id": self.sequence}
        size = len(json.dumps(record, ensure_ascii=False).encode())
        if self.queued_bytes + size > self.queue_byte_limit:
            raise RuntimeError("capture queue byte limit reached; run stopped rather than dropping messages")
        try:
            self.queue.put_nowait(record)
        except asyncio.QueueFull:
            raise RuntimeError("capture queue overflow; run stopped rather than dropping messages") from None
        self.queued_sizes[self.sequence] = size
        self.queued_bytes += size
        self.sequence += 1

    async def write(self, store):
        while True:
            try:
                row = await asyncio.wait_for(self.queue.get(), timeout=1)
            except TimeoutError:
                store.flush()
                continue
            if row is None:
                self.queue.task_done()
                return
            self.queued_bytes -= self.queued_sizes.pop(row["record_id"])
            store.append(row)
            self.queue.task_done()

    async def receive(self, ws, feed, connection_id, ack, activity):
        monitor = FeedMonitor(feed.name, feed.topics)
        count = self.stats[feed.name]
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=45)
            clocks = stamp()  # Application receive time, before JSON decoding.
            if not isinstance(raw, str):
                raise FeedError("unexpected binary frame")
            message = json.loads(raw)
            monitor.validate_scope(message)
            self.emit(feed.name, connection_id, "ws_message", **clocks, raw=raw)
            diagnostics = monitor.inspect(message)
            count["messages"] += 1
            count["last_received_ns"] = clocks["received_ns"]
            if feed.name == "binance_spot":
                topic = message["stream"]
            else:
                topic = message.get("topic")
                if message.get("op") == "subscribe" and message.get("success") is True:
                    ack.set()
                    count["subscription_acknowledged"] = True
            if topic:
                count["topics"][topic] += 1
                activity[topic] = time.monotonic()
            for event in diagnostics:
                self.emit(feed.name, connection_id, **event)

    async def heartbeat(self, ws, feed, connection_id, ack, activity):
        while True:
            await asyncio.sleep(20)
            if not ack.is_set():
                raise FeedError("subscription acknowledgement timeout")
            for topic in feed.topics:
                if topic.startswith(("orderbook.", "tickers.")) or "@depth" in topic:
                    if topic not in activity or time.monotonic() - activity[topic] > 30:
                        raise FeedError(f"required topic absent or idle: {topic}")
            if feed.name != "binance_spot":
                request = json.dumps({"op": "ping"})
                await ws.send(request)
                self.emit(feed.name, connection_id, "application_ping_sent", raw=request)
            waiter = await ws.ping()
            latency = await asyncio.wait_for(waiter, timeout=10)
            self.emit(feed.name, connection_id, "transport_pong", round_trip_seconds=latency)

    async def snapshot(self, feed, connection_id):
        if feed.name == "binance_spot":
            # Receive loop is already running while the REST snapshot is fetched.
            row = await asyncio.to_thread(fetch_snapshot)
            self.emit(feed.name, connection_id, **row)

    async def feed(self, feed):
        from websockets.asyncio.client import connect
        from websockets.exceptions import WebSocketException

        failures = 0
        while True:
            connection_id = uuid.uuid4().hex
            connected_at = None
            self.emit(feed.name, connection_id, "connection_attempt", url=feed.url)
            try:
                async with connect(feed.url, open_timeout=15, close_timeout=3,
                                   ping_interval=None, max_size=4_000_000, max_queue=16) as ws:
                    connected_at = time.monotonic()
                    self.stats[feed.name]["connections"] += 1
                    self.stats[feed.name]["subscription_acknowledged"] = feed.name == "binance_spot"
                    self.emit(feed.name, connection_id, "connected", url=feed.url,
                              requires_new_snapshot=True)
                    ack = asyncio.Event()
                    activity = {}
                    if feed.name == "binance_spot":
                        ack.set()  # Combined streams are selected in the URL.
                    else:
                        raw = json.dumps({"op": "subscribe", "args": feed.topics,
                                          "req_id": connection_id})
                        await ws.send(raw)
                        self.emit(feed.name, connection_id, "subscribe_sent", raw=raw)
                    tasks = [asyncio.create_task(self.receive(ws, feed, connection_id, ack, activity)),
                             asyncio.create_task(self.heartbeat(ws, feed, connection_id, ack, activity)),
                             asyncio.create_task(self.snapshot(feed, connection_id))]
                    try:
                        # Binance has a 24-hour connection lifetime. Rotate before that.
                        await asyncio.wait_for(asyncio.gather(*tasks), timeout=23 * 3600)
                    finally:
                        for task in tasks:
                            task.cancel()
                        await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError:
                raise
            except (OSError, WebSocketException, TimeoutError, FeedError, ValueError, KeyError, TypeError) as exc:
                failures = 0 if connected_at and time.monotonic() - connected_at >= 60 else failures
                failures += 1
                # Store exception class and bounded reason; no credentials are used.
                self.emit(feed.name, connection_id, "connection_error", error_type=type(exc).__name__,
                          reason=str(exc)[:300], retry=failures)
                if failures >= 5:
                    raise RuntimeError(f"{feed.name}: five consecutive short/failed connections") from exc
            finally:
                self.stats[feed.name]["disconnects"] += 1
                self.emit(feed.name, connection_id, "disconnected", continuity_lost=True)
            await asyncio.sleep(min(30, 2 ** min(failures, 5)))

    async def clock_watch(self):
        previous = stamp()
        while True:
            await asyncio.sleep(1)
            current = stamp()
            drift = (current["received_ns"] - previous["received_ns"] -
                     current["monotonic_ns"] + previous["monotonic_ns"])
            if abs(drift) > 100_000_000:
                self.emit("collector", None, "clock_step", discrepancy_ns=drift,
                          requires_clock_audit=True)
            elapsed = current["monotonic_ns"] - previous["monotonic_ns"]
            if elapsed > 1_100_000_000:
                self.emit("collector", None, "event_loop_delay", interval_ns=elapsed)
            previous = current


async def run_capture(output, *, duration, max_bytes, segment_bytes=8 << 20):
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration must be positive and finite")
    store = CaptureStore(output, max_bytes=max_bytes, segment_bytes=segment_bytes)
    recorder = Recorder()
    start = stamp()
    package_root = Path(__file__).resolve().parent
    manifest = {"schema": SCHEMA, "run_id": store.run_id, "asset": "BTC", "symbol": "BTCUSDT",
                "purpose": "forward_capture_software_and_data_readiness_no_model_scoring",
                "start": start, "planned_duration_seconds": duration,
                "planned_end_ns": start["received_ns"] + int(duration * 1e9),
                "max_raw_bytes_in_directory": max_bytes, "segment_bytes": segment_bytes,
                "feeds": [asdict(f) for f in FEEDS], "binance_snapshot_url": SNAPSHOT_URL,
                "websockets_version": importlib.metadata.version("websockets"),
                "code_sha256": {name: sha256(package_root / name)
                                for name in ("collect.py", "capture_health.py", "capture_store.py")},
                "recovered_unclean_segments": store.recovered,
                "receipt_clock": "application_recv_wall_ns_and_monotonic_ns_not_kernel_timestamp",
                "feed_completeness_verified": False, "model_fitting_enabled": False,
                "status": "running"}
    manifest_path = store.root / f"{store.run_id}.manifest.json"
    atomic_json(manifest_path, manifest)  # Commit period and source policy before capture.
    recorder.emit("collector", None, "run_started", run_id=store.run_id,
                  prior_history_unknown=True, planned_end_ns=manifest["planned_end_ns"])
    writer = asyncio.create_task(recorder.write(store))
    tasks = [asyncio.create_task(recorder.feed(feed)) for feed in FEEDS]
    tasks.append(asyncio.create_task(recorder.clock_watch()))
    timer = asyncio.create_task(asyncio.sleep(duration))
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    installed_signals = []
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
            installed_signals.append(sig)
        except (NotImplementedError, RuntimeError):
            pass
    stopped = asyncio.create_task(stop.wait())
    error = None
    try:
        done, _ = await asyncio.wait([writer, timer, stopped, *tasks], return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task not in (timer, stopped):
                task.result()
        manifest["status"] = "interrupted" if stopped in done else "duration_reached"
    except Exception as exc:
        error = exc
        manifest["status"] = "storage_limit" if isinstance(exc, StorageLimit) else "failed"
        manifest["error"] = {"type": type(exc).__name__, "reason": str(exc)[:300]}
    finally:
        timer.cancel()
        stopped.cancel()
        for task in tasks:
            task.cancel()
        await asyncio.gather(timer, stopped, *tasks, return_exceptions=True)
        try:
            # Drain through the same writer. Cancelling a pending queue.get can
            # race with delivery, so never cancel it on an orderly shutdown.
            if not writer.done():
                putter = asyncio.create_task(recorder.queue.put(None))
                await asyncio.wait([writer, putter], return_when=asyncio.FIRST_COMPLETED)
                if not putter.done():
                    putter.cancel()
                await asyncio.gather(putter, return_exceptions=True)
            await writer
            store.append({"schema": SCHEMA, "kind": "run_stopped", **stamp(),
                          "run_id": store.run_id, "status": manifest["status"]})
        except Exception as exc:
            error = error or exc
            manifest["status"] = "storage_limit" if isinstance(exc, StorageLimit) else "failed"
            manifest["error"] = {"type": type(exc).__name__, "reason": str(exc)[:300]}
        try:
            store.close()
        finally:
            manifest.update(end=stamp(), records_written=store.records,
                            records_emitted=recorder.sequence,
                            queued_records_not_written=recorder.queue.qsize(),
                            raw_bytes_in_directory=store.total_bytes, feeds_observed=recorder.stats)
            atomic_json(manifest_path, manifest)
            for sig in installed_signals:
                loop.remove_signal_handler(sig)
    return manifest_path, manifest, error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/raw/live_btc")
    parser.add_argument("--duration", type=float, default=60, help="Fixed run length in seconds (default: 60)")
    parser.add_argument("--max-mib", type=int, default=2048, help="Total raw storage budget, including prior runs")
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration) or args.duration <= 0 or args.max_mib <= 0:
        parser.error("duration and storage budget must be positive and finite")
    path, manifest, error = asyncio.run(run_capture(args.output, duration=args.duration,
                                                  max_bytes=args.max_mib << 20))
    print(json.dumps({"manifest": str(path), "status": manifest["status"],
                      "records_written": manifest["records_written"],
                      "feeds_observed": manifest["feeds_observed"]}, indent=2))
    return 1 if error else 0


if __name__ == "__main__":
    raise SystemExit(main())
