"""Receipt-ordered replay of E001-capture-v1 into auditable state, not model rows."""

from collections import Counter, deque
from dataclasses import replace
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re

from .capture_health import FeedError, FeedMonitor
from .capture_store import sha256
from .collect import FEEDS, SNAPSHOT_URL
from .timing import ClockEvidence, EvidenceTimeline

NS = 1_000_000_000
BAND = Decimal('0.0025')


class ReplayError(ValueError):
    pass


def levels(rows):
    result = {}
    for price, size in rows:
        try:
            p, q = Decimal(price), Decimal(size)
        except (InvalidOperation, TypeError, ValueError):
            raise ReplayError('invalid level number') from None
        if not p.is_finite() or p <= 0 or not q.is_finite() or q < 0 or p in result:
            raise ReplayError('invalid or duplicate level')
        result[p] = q
    return result


class Book:
    def __init__(self, limit=None):
        self.limit = limit
        self.bids, self.asks = {}, {}
        self.ready = False
        self.last_id = self.seq = None
        self.event_ns = self.available_ns = None
        self.quote_event_ns = self.quote_available_ns = None
        self.bid_floor = self.ask_ceiling = None
        self.reason = 'awaiting_snapshot'
        self.receipt_clock_valid = False
        self._top = None

    def invalidate(self, reason):
        self.ready = False
        self.receipt_clock_valid = False
        self.reason = reason
        self._top = None
        self.quote_event_ns = self.quote_available_ns = None

    def replace(self, bids, asks):
        self.bids = {p: q for p, q in levels(bids).items() if q}
        self.asks = {p: q for p, q in levels(asks).items() if q}
        self._trim()
        self.bid_floor = min(self.bids, default=None)
        self.ask_ceiling = max(self.asks, default=None)
        self._top = None
        self.quote_event_ns = self.quote_available_ns = None

    def _trim(self):
        if self.limit:
            self.bids = dict(sorted(self.bids.items(), reverse=True)[:self.limit])
            self.asks = dict(sorted(self.asks.items())[:self.limit])

    def patch(self, bids, asks):
        incoming = (levels(bids), levels(asks))
        for side, updates in zip((self.bids, self.asks), incoming):
            for price, size in updates.items():
                if size:
                    side[price] = size
                else:
                    side.pop(price, None)
        self._trim()
        if self.limit:
            # Bybit's feed is the current top N. Binance's snapshot boundary
            # stays fixed: isolated outside updates cannot fill unknown levels.
            self.bid_floor = min(self.bids, default=None)
            self.ask_ceiling = max(self.asks, default=None)

    def top(self):
        if not self.bids or not self.asks:
            return None
        bid, ask = max(self.bids), min(self.asks)
        if bid >= ask or self.bid_floor is None or self.ask_ceiling is None:
            return None
        if bid < self.bid_floor or ask > self.ask_ceiling:
            return None
        return bid, self.bids[bid], ask, self.asks[ask]

    def observe(self, event_ns, available_ns):
        self.event_ns, self.available_ns = event_ns, available_ns
        top = self.top()
        if top is None:
            raise ReplayError('empty_crossed_or_outside_known_book')
        self.receipt_clock_valid = event_ns <= available_ns
        if top != self._top:
            self.quote_event_ns, self.quote_available_ns = event_ns, available_ns
        self._top = top
        self.ready, self.reason = True, None

    def quote(self, boundary):
        if not self.ready:
            return {'valid': False, 'reason': self.reason}
        if not self.receipt_clock_valid:
            return {'valid': False, 'reason': 'source_event_after_receipt'}
        if self.quote_event_ns is None or self.quote_available_ns > boundary:
            return {'valid': False, 'reason': 'quote_not_available'}
        age = boundary - self.quote_event_ns
        if age < 0 or age > 5 * NS:
            return {'valid': False, 'reason': 'quote_not_fresh', 'age_ns': age}
        top = self.top()
        return {'valid': True, 'midpoint': (top[0] + top[2]) / 2,
                'source_event_ns': self.quote_event_ns, 'available_ns': self.quote_available_ns,
                'age_ns': age}

    def view(self, boundary):
        result = {'ready': self.ready, 'reason': self.reason,
                  'receipt_clock_valid': self.receipt_clock_valid,
                  'update_id': self.last_id, 'sequence': self.seq,
                  'source_event_ns': self.event_ns, 'available_ns': self.available_ns}
        if not self.ready:
            return result
        bid, _, ask, _ = self.top()
        mid = (bid + ask) / 2
        lower, upper = mid * (1 - BAND), mid * (1 + BAND)
        bid_covered = self.bid_floor <= lower
        ask_covered = self.ask_ceiling >= upper
        observed_bid = sum((p*q for p, q in self.bids.items() if p >= lower), Decimal(0))
        observed_ask = sum((p*q for p, q in self.asks.items() if p <= upper), Decimal(0))
        result.update(midpoint=mid, bid_levels=len(self.bids), ask_levels=len(self.asks),
                      book_age_ns=boundary-self.event_ns,
                      known_bid_floor=self.bid_floor, known_ask_ceiling=self.ask_ceiling,
                      bid_band_covered=bid_covered, ask_band_covered=ask_covered,
                      observed_bid_notional_25bps=observed_bid,
                      observed_ask_notional_25bps=observed_ask,
                      bid_notional_25bps=observed_bid if bid_covered else None,
                      ask_notional_25bps=observed_ask if ask_covered else None)
        return result


class BinanceBook(Book):
    def __init__(self):
        super().__init__()
        self.buffer = deque()
        self.snapshot_loaded = False
        self.broken = False

    def snapshot(self, message, available_ns):
        self.replace(message['bids'], message['asks'])
        self.last_id = int(message['lastUpdateId'])
        self.ready, self.snapshot_loaded, self.broken = False, True, False
        self.reason = 'awaiting_snapshot_bridge'
        pending = list(self.buffer)
        self.buffer.clear()
        if pending and self.last_id < int(pending[0][0]['U']):
            self.broken = True
            raise ReplayError('binance_snapshot_too_old')
        for event, receipt_ns in pending:
            self.delta(event, max(available_ns, receipt_ns))

    def delta(self, data, available_ns):
        if self.broken:
            return
        if not self.snapshot_loaded:
            if len(self.buffer) >= 4096:
                self.broken = True
                raise ReplayError('binance_snapshot_buffer_limit')
            self.buffer.append((data, available_ns))
            return
        first, last = int(data['U']), int(data['u'])
        if first > last:
            self.broken = True
            raise ReplayError('invalid_binance_update_range')
        if last <= self.last_id:
            return  # Does not refresh quote age.
        if first > self.last_id + 1:
            self.broken = True
            raise ReplayError('binance_sequence_gap')
        self.patch(data['b'], data['a'])
        self.last_id = last
        self.observe(int(data['E']) * 1_000_000, available_ns)


class BybitBook(Book):
    def update(self, message, available_ns):
        data = message['data']
        update_id, seq = int(data['u']), int(data['seq'])
        if message['type'] == 'snapshot':
            # A repeated identical L1 snapshot isn't a new quote change.
            old_top = self._top
            old_quote = self.quote_event_ns, self.quote_available_ns
            self.replace(data['b'], data['a'])
            if self.limit == 1 and old_top == self.top():
                self._top = old_top
                self.quote_event_ns, self.quote_available_ns = old_quote
        elif message['type'] == 'delta':
            if not self.ready:
                raise ReplayError('bybit_delta_without_snapshot')
            if update_id <= self.last_id or seq <= self.seq:
                raise ReplayError('bybit_sequence_regression')
            self.patch(data['b'], data['a'])
        else:
            raise ReplayError('unknown_book_message_type')
        self.last_id, self.seq = update_id, seq
        self.observe(int(message['ts']) * 1_000_000, available_ns)


class Ticker:
    def __init__(self):
        self.fields = {}
        self.ready = False
        self.seq = None
        self.reason = 'awaiting_snapshot'
        self.receipt_clock_valid = False

    def invalidate(self, reason):
        self.fields = {}
        self.ready = False
        self.receipt_clock_valid = False
        self.reason = reason

    def update(self, message, available_ns):
        seq = int(message['cs'])
        event_ns = int(message['ts']) * 1_000_000
        self.receipt_clock_valid = event_ns <= available_ns
        if message['type'] == 'snapshot':
            self.fields = {}
        elif message['type'] != 'delta' or not self.ready:
            raise ReplayError('ticker_delta_without_snapshot')
        elif seq <= self.seq:
            raise ReplayError('ticker_sequence_regression')
        for name, value in message['data'].items():
            self.fields[name] = {'value': value, 'source_event_ns': event_ns,
                                 'available_ns': available_ns}
        self.seq, self.ready, self.reason = seq, True, None

    def view(self):
        return {'ready': self.ready, 'reason': self.reason,
                'receipt_clock_valid': self.receipt_clock_valid,
                'sequence': self.seq, 'fields': dict(self.fields)}


class Replay:
    def __init__(self):
        self.connections = {}
        self.books = {}
        self.ticker = Ticker()
        self.diagnostics = Counter()
        self.clock_valid = True
        self.clock_epoch = 0
        self.clock_evidence = EvidenceTimeline()
        self.clock_lag_ms = {}
        self.max_source_lead_ns = 0
        self.scope = {feed.name: FeedMonitor(feed.name, feed.topics) for feed in FEEDS}

    def reset(self, source, reason):
        for key in list(self.books):
            if key.startswith(source + ':'):
                del self.books[key]
        if source == 'binance_spot':
            self.books['binance_spot:depth'] = BinanceBook()
        if source == 'bybit_linear':
            self.ticker = Ticker()
        self.diagnostics[reason] += 1

    def process(self, row, available_ns):
        kind, source = row['kind'], row.get('source')
        connection = row.get('connection_id')
        if kind == 'clock_step':
            self.clock_valid = False
            self.clock_epoch += 1
            self.diagnostics['clock_step'] += 1
            return
        if kind == 'clock_probe':
            probe = row.get('evidence', {})
            if not isinstance(probe, dict):
                self.diagnostics['clock_probe_invalid'] += 1
                return
            if probe.get('status') != 'ok':
                self.diagnostics['clock_probe_error'] += 1
                return
            try:
                evidence = ClockEvidence.from_probe(probe)
                evidence = replace(evidence, available_ns=max(evidence.available_ns, available_ns))
                self.clock_evidence.add(evidence)
                self.diagnostics['clock_probe_ok'] += 1
            except (ValueError, KeyError, TypeError):
                self.diagnostics['clock_probe_invalid'] += 1
            return
        if kind in ('connected', 'disconnected', 'connection_error'):
            if source not in self.scope:
                raise ReplayError('unapproved source')
            if kind == 'connected':
                self.connections[source] = connection
                self.reset(source, kind)
            elif self.connections.get(source) == connection:
                self.connections.pop(source, None)
                self.reset(source, kind)
            return
        if kind not in ('ws_message', 'rest_snapshot'):
            return
        if source not in self.scope:
            raise ReplayError('unapproved source')
        if self.connections.get(source) != connection:
            self.diagnostics['message_outside_connection'] += 1
            return
        message = json.loads(row['raw'])
        target = None
        try:
            if kind == 'rest_snapshot':
                if source != 'binance_spot' or row['url'] != SNAPSHOT_URL:
                    raise ReplayError('unapproved snapshot URL')
                target = self.books['binance_spot:depth']
                target.snapshot(message, available_ns)
            else:
                self.scope[source].validate_scope(message)
                timestamp = message.get('ts') if source.startswith('bybit') else message['data'].get('E')
                if timestamp is not None:
                    event_ns = int(timestamp) * 1_000_000
                    lag = row['received_ns'] - event_ns
                    self.clock_lag_ms.setdefault(source, Counter())[round(lag / 1_000_000)] += 1
                    if lag < 0:
                        self.max_source_lead_ns = max(self.max_source_lead_ns, -lag)
                        self.clock_valid = False
                        self.diagnostics[source + ':source_event_after_receipt'] += 1
                if source == 'binance_spot' and message['data'].get('e') == 'depthUpdate':
                    target = self.books['binance_spot:depth']
                    target.delta(message['data'], available_ns)
                elif source.startswith('bybit') and message.get('topic', '').startswith('orderbook.'):
                    topic = message['topic']
                    key = source + ':' + topic
                    target = self.books.setdefault(key, BybitBook(int(topic.split('.')[1])))
                    target.update(message, available_ns)
                elif source == 'bybit_linear' and message.get('topic') == 'tickers.BTCUSDT':
                    target = self.ticker
                    target.update(message, available_ns)
        except FeedError as exc:
            raise ReplayError(str(exc)) from exc  # Scope violations fail the replay.
        except (ReplayError, KeyError, ValueError, TypeError, InvalidOperation) as exc:
            if target is None:
                raise
            reason = str(exc)
            target.invalidate(reason)
            if isinstance(target, BinanceBook):
                target.broken = True
            self.diagnostics[reason] += 1

    def grid(self, second):
        boundary = second * NS
        quotes = {}
        for name, key in (('binance', 'binance_spot:depth'),
                          ('bybit', 'bybit_spot:orderbook.1.BTCUSDT')):
            book = self.books.get(key)
            quotes[name] = book.quote(boundary) if book else {'valid': False, 'reason': 'not_connected_or_initialized'}
        valid = self.clock_valid and all(q['valid'] for q in quotes.values())
        return {'second': second, 'clock_valid': self.clock_valid, 'quotes': quotes,
                'composite_price': (quotes['binance']['midpoint'] + quotes['bybit']['midpoint']) / 2 if valid else None,
                'books': {name: book.view(boundary) for name, book in self.books.items()},
                'bybit_linear_ticker': self.ticker.view(),
                'model_ready': False}


def replay_grid(records, replay):
    """Stream grid rows; never backdate a delayed REST result in capture order."""
    next_second = None
    last_available = 0
    for row in records:
        received = row['received_ns']
        available = max(last_available, received)
        if available != received:
            replay.diagnostics['receipt_order_clamped'] += 1
        if next_second is None:
            next_second = (available + NS - 1) // NS
        while next_second * NS < available:
            yield replay.grid(next_second)
            next_second += 1
        replay.process(row, available)
        last_available = available
    if next_second is not None:
        while next_second * NS <= last_available:
            yield replay.grid(next_second)
            next_second += 1


class CaptureInput:
    """Freeze and verify immutable segments; a running prefix is explicitly partial."""
    def __init__(self, manifest_path, *, sealed_prefix=False, segment_limit=None):
        self.path = Path(manifest_path)
        if 'eth' in str(self.path.resolve()).lower():
            raise ReplayError('ETH holdout is sealed')
        raw = self.path.read_bytes()
        self.manifest = json.loads(raw)
        m = self.manifest
        if m['asset'] != 'BTC' or m['symbol'] != 'BTCUSDT' or m['schema'] != 'E001-capture-v1':
            raise ReplayError('unsupported capture scope/schema')
        if not re.fullmatch('[0-9a-f]{32}', m['run_id']):
            raise ReplayError('invalid run ID')
        if m['status'] == 'running' and not sealed_prefix:
            raise ReplayError('running capture requires explicit sealed-prefix mode')
        self.partial = sealed_prefix
        self.segments = tuple(sorted(self.path.parent.glob(m['run_id'] + '-*.jsonl')))
        # Rotation renames the segment before writing its sidecar. Omit only a
        # still-unpublished last segment when explicitly selecting a live prefix.
        if sealed_prefix and self.segments and not self.segments[-1].with_suffix('.meta.json').exists():
            self.segments = self.segments[:-1]
        if segment_limit is not None:
            if not sealed_prefix or segment_limit < 1 or segment_limit > len(self.segments):
                raise ReplayError('segment limit requires that many sealed prefix segments')
            self.segments = self.segments[:segment_limit]
        if not self.segments:
            raise ReplayError('no sealed segments yet')
        self.hashes = {}
        import hashlib
        self.manifest_sha256 = hashlib.sha256(raw).hexdigest()

    def records(self):
        expected_id = count = 0
        terminal = False
        for index, path in enumerate(self.segments, 1):
            if path.name != f"{self.manifest['run_id']}-{index:06d}.jsonl":
                raise ReplayError('missing capture segment')
            meta = json.loads(path.with_suffix('.meta.json').read_text())
            digest = sha256(path)
            if digest != meta['sha256'] or path.stat().st_size != meta['bytes'] or meta['status'] != 'closed':
                raise ReplayError('segment integrity mismatch')
            self.hashes[path.name] = digest
            lines = 0
            with path.open() as stream:
                for line in stream:
                    row = json.loads(line)
                    if terminal:
                        raise ReplayError('records after terminal marker')
                    if row['schema'] != 'E001-capture-v1' or not isinstance(row['received_ns'], int):
                        raise ReplayError('invalid record envelope')
                    if row['kind'] == 'run_stopped':
                        terminal = True
                    else:
                        if row['record_id'] != expected_id:
                            raise ReplayError('missing capture record')
                        expected_id += 1
                    count += 1
                    lines += 1
                    yield row
            if lines != meta['records']:
                raise ReplayError('segment record count mismatch')
        if not self.partial:
            if not terminal or count != self.manifest['records_written']:
                raise ReplayError('incomplete capture run')
            if expected_id != self.manifest.get('records_emitted', expected_id):
                raise ReplayError('unwritten emitted records')
