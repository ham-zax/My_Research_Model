"""Top-50 liquidity-state replay over sealed E001 public capture segments."""

from collections import deque
from decimal import Decimal
import json

from .data import DataError, normalize_bybit_message
from .liquidity_state import NS, decision_liquidity_state, top_level_book
from .replay import Replay, ReplayError


BOOK_KEY = 'bybit_linear:orderbook.50.BTCUSDT'
ZERO = Decimal(0)
MAX_SOURCE_LEAD_NS = 100_000_000  # Diagnostic protective guard, not a venue delay bound.


class LiquidityReplay(Replay):
    """Measure only fields observable by each local receipt-time grid boundary."""

    def __init__(self, *, levels=50):
        super().__init__()
        if type(levels) is not int or levels < 1 or levels > 50:
            raise ValueError('live top-level count must be between 1 and 50')
        self.levels = levels
        self.liquidity_epoch = 0
        self.states = {}
        self.observations = deque()
        self.trades = deque()
        self.trade_ids = {}
        self.trade_expiry = deque()
        self.capture_start_ns = None

    def _clear_linear_history(self):
        self.liquidity_epoch += 1
        self.observations.clear()
        self.trades.clear()
        self.trade_ids.clear()
        self.trade_expiry.clear()

    def process(self, row, available_ns):
        if self.capture_start_ns is None:
            self.capture_start_ns = available_ns
        kind, source = row['kind'], row.get('source')
        active = self.connections.get(source) == row.get('connection_id')
        message = (json.loads(row['raw']) if kind == 'ws_message' and
                   source == 'bybit_linear' and active else None)
        topic = message.get('topic') if message else None
        is_book = topic == 'orderbook.50.BTCUSDT'
        prior_book = self.books.get(BOOK_KEY)
        before = (dict(prior_book.bids), dict(prior_book.asks)) if (
            is_book and prior_book and prior_book.ready) else None
        super().process(row, available_ns)
        if kind == 'clock_step' or (source == 'bybit_linear' and
                                   kind in ('connected', 'disconnected', 'connection_error')
                                   and (kind == 'connected' or active)):
            self._clear_linear_history()
            return
        if not message:
            return
        if is_book:
            reset = message['type'] == 'snapshot'
            if reset:
                self._clear_linear_history()
            book = self.books.get(BOOK_KEY)
            if book is None or not book.ready:
                self._clear_linear_history()
                return
            viewed = top_level_book(
                book.bids, book.asks, levels=self.levels,
                epoch=self.liquidity_epoch, last_us=book.available_ns//1000,
                boundary_us=available_ns//1000)
            changes = []
            known = True
            if before is not None and not reset:
                for side_name, old, current in zip(
                        ('bid', 'ask'), before, (book.bids, book.asks)):
                    prior_boundary = (min(old) if side_name == 'bid' else max(old))
                    for price in old.keys() | current.keys():
                        delta = current.get(price, ZERO)-old.get(price, ZERO)
                        if not delta:
                            continue
                        changes.append((side_name, price, delta))
                        current_prices = viewed['top_bid_prices'] if side_name == 'bid' else viewed['top_ask_prices']
                        revealed = price < prior_boundary if side_name == 'bid' else price > prior_boundary
                        if delta > 0 and price in current_prices and revealed:
                            known = False
            self.observations.append({
                'event_ns': available_ns, 'available_ns': available_ns,
                'book_epoch': self.liquidity_epoch, 'reset': reset,
                'top_level_valid': viewed['top_level_valid'],
                'top_bid_prices': viewed['top_bid_prices'],
                'top_ask_prices': viewed['top_ask_prices'],
                'bid_changes_known': known, 'changes': changes,
            })
            while (len(self.observations) > 1 and
                   self.observations[1]['event_ns'] < available_ns-20*NS):
                self.observations.popleft()
        elif topic == 'publicTrade.BTCUSDT':
            try:
                items = normalize_bybit_message(
                    message, received_ms=row['received_ns']//1_000_000,
                    market='linear', require_source_before_receipt=False)
            except DataError as exc:
                raise ReplayError(str(exc)) from exc
            for item in items:
                identity = (item.event_ms, item.taker_side, item.base_size, item.price)
                if not item.trade_id or item.trade_id == 'None':
                    raise ReplayError('missing trade ID')
                prior = self.trade_ids.get(item.trade_id)
                if prior is not None:
                    if prior != identity:
                        raise ReplayError('conflicting duplicate trade')
                    continue
                self.trade_ids[item.trade_id] = identity
                self.trade_expiry.append((available_ns, item.trade_id))
                self.trades.append({
                    'received_us': available_ns//1000,
                    'side': item.taker_side.lower(),
                    'notional': item.notional_quote,
                })
            while self.trades and self.trades[0]['received_us'] < available_ns//1000-30_000_000:
                self.trades.popleft()
            while self.trade_expiry and self.trade_expiry[0][0] < available_ns-30*NS:
                _, trade_id = self.trade_expiry.popleft()
                self.trade_ids.pop(trade_id, None)

    def grid(self, second):
        boundary_us = second*1_000_000
        book = self.books.get(BOOK_KEY)
        if book is None or not book.ready:
            state = {'top_level_valid': False, 'reason': 'book_not_initialized',
                     'book_epoch': self.liquidity_epoch}
        else:
            state = top_level_book(
                book.bids, book.asks, levels=self.levels,
                epoch=self.liquidity_epoch, last_us=book.available_ns//1000,
                boundary_us=boundary_us)
        if self.max_source_lead_ns > MAX_SOURCE_LEAD_NS:
            state['top_level_valid'] = False
            state['reason'] = 'source_clock_lead_quarantine'
        state['second'] = second
        self.states[second] = state
        while len(self.states) > 1816:
            del self.states[next(iter(self.states))]
        return state

    def features(self, trigger_s):
        return decision_liquidity_state(
            self.states, self.observations, self.trades,
            trigger_s=trigger_s, levels=self.levels)
