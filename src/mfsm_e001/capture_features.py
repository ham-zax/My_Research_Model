"""Candidate BTC feature measurements from receipt-ordered capture replay.

This is an audited-input builder, not an event selector or a fitted model. Values
without identifiable feed semantics remain null. Raw notionals are diagnostics;
the common model representation contains only relative/dimensionless quantities.
"""

from bisect import bisect_left, bisect_right
from collections import deque
from decimal import Decimal, InvalidOperation
import json
from statistics import median

from .data import Liquidation, Trade, normalize_bybit_message
from .replay import BAND, NS, Replay, ReplayError, replay_grid

WINDOWS = (1, 5, 15, 30, 60, 300)
BOOK_KEY = 'bybit_linear:orderbook.1000.BTCUSDT'
MAX_STATE_AGE_NS = 5 * NS
MAX_SOURCE_SILENCE_NS = 30 * NS
ZERO = Decimal(0)
BP = Decimal(10000)


def numeric(value, *, positive=False):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return result if result.is_finite() and (not positive or result > 0) else None


def pretrigger_scales(states, decision_second):
    """Exactly [trigger-1800, trigger), with trigger = decision-15 seconds."""
    trigger = decision_second - 15
    result = {}
    for name, field in (('depth', 'depth_bid'), ('oi', 'oi')):
        values = [states.get(s, {}).get(field) for s in range(trigger-1800, trigger)]
        result[name] = (median(values) if all(v is not None and v > 0 for v in values)
                        else None)
    return result


def normalized_features(raw, scales):
    """Same neutral base for both learners; no raw cross-asset scale leakage."""
    depth, oi = scales['depth'], scales['oi']
    depth = depth if depth is not None and depth > 0 else None
    oi = oi if oi is not None and oi > 0 else None
    shared = {}
    for key, value in raw.items():
        if key in ('depth_bid', 'depth_ask') or key.startswith(('depth_bid_lag_', 'depth_ask_lag_')):
            shared[key+'_relative'] = value/depth if value is not None and depth else None
        elif key == 'oi':
            shared['oi_relative_pretrigger'] = value/oi-1 if value is not None and oi else None
            shared['oi_log_pretrigger'] = (value/oi).ln() if value is not None and oi else None
        elif key.startswith('liquidation_') and '_size_base_' in key:
            shared[key+'_relative_oi'] = value/oi if value is not None and oi else None
        elif key.startswith(('aggressive_', 'liquidation_', 'gross_', 'persistent_',
                             'observed_', 'cancel_', 'execution_')):
            shared[key+'_relative_depth'] = value/depth if value is not None and depth else None
        elif key.endswith('_bps') or key == 'book_imbalance' or key.startswith(
                ('return_', 'realized_volatility_', 'oi_change_', 'oi_log_change_')):
            shared[key] = value
    bid, replenishment = raw.get('depth_bid'), raw.get('persistent_bid_add_rate_15s')
    capacity = (max(bid + 30*replenishment, depth*Decimal('0.01'))
                if bid is not None and replenishment is not None and depth else None)
    shared['capacity_proxy_relative'] = capacity/depth if capacity is not None else None
    shared['low_capacity'] = (bid + 30*replenishment <= depth*Decimal('0.01')
                              if capacity is not None else None)
    mfsm = dict(shared)
    sell, liq = raw.get('aggressive_sell_notional_30s'), raw.get('liquidation_sell_notional_30s')
    mfsm['sell_pressure_ratio_contaminated'] = sell/capacity if sell is not None and capacity else None
    mfsm['liquidation_pressure_ratio'] = liq/capacity if liq is not None and capacity else None
    return shared, mfsm


def book_window(observations, boundary, seconds):
    """Event-time L2 windows, using only state received by the decision.

Every observed reduction is charged against each eligible addition cohort.
Positive changes never erase prior reductions. Endpoint state is the most recent
observed state at/before the dwell endpoint; no future received update is used.
"""
    left = boundary-seconds*NS
    times = [r['event_ns'] for r in observations]
    # Keep a strictly earlier anchor plus every change at the inclusive
    # persistence left edge, including multiple updates within one millisecond.
    anchor = max(0, bisect_left(times, left)-1) if times else -1
    result = {}
    for side in ('bid', 'ask'):
        names = [f'{prefix}_{side}_{suffix}_{seconds}s' for prefix, suffix in (
            ('gross', 'add_rate'), ('persistent', 'add_rate'), ('observed', 'decrease_rate'))]
        valid = anchor >= 0 and times[anchor] <= left
        relevant = observations[max(anchor, 0):]
        valid = valid and bool(relevant) and all(r['valid'] and r[side+'_covered'] for r in relevant)
        valid = valid and all(r[side+'_changes_known'] for r in relevant if r['event_ns'] >= left)
        valid = valid and not any(r['reset'] and r['event_ns'] > left for r in relevant)
        valid = valid and boundary-relevant[-1]['event_ns'] <= MAX_STATE_AGE_NS
        valid = valid and all(b['event_ns']-a['event_ns'] <= MAX_STATE_AGE_NS
                              for a, b in zip(relevant, relevant[1:]))
        if not valid:
            result.update(dict.fromkeys(names))
            continue
        # Prefix sums let each cohort query reductions without rescanning all
        # subsequent changes (which would be quadratic in active market flow).
        negatives = {}
        changes = []
        for state in relevant:
            if state['reset'] or state['event_ns'] < left:
                continue
            for change_side, price, size in state['changes']:
                if change_side != side:
                    continue
                event = state['event_ns']
                changes.append((state, price, size))
                if size < 0:
                    stamps, totals = negatives.setdefault(price, ([], [ZERO]))
                    stamps.append(event)
                    totals.append(totals[-1]-size)
        added = decreased = persistent = ZERO
        for state, price, size in changes:
            mid = state['mid']
            inside = mid*(1-BAND) <= price <= mid if side == 'bid' else mid <= price <= mid*(1+BAND)
            if inside and state['event_ns'] > left:
                added += price*max(size, ZERO)
                decreased += price*max(-size, ZERO)
            endpoint = state['event_ns'] + NS
            if size <= 0 or not inside or endpoint > boundary:
                continue
            end = observations[bisect_right(times, endpoint)-1]
            end_mid = end['mid']
            remains = (end_mid*(1-BAND) <= price <= end_mid if side == 'bid'
                       else end_mid <= price <= end_mid*(1+BAND))
            if not remains or endpoint-end['event_ns'] > MAX_STATE_AGE_NS:
                continue
            stamps, totals = negatives.get(price, ([], [ZERO]))
            reduction = totals[bisect_right(stamps, endpoint)]-totals[bisect_right(stamps, state['event_ns'])]
            persistent += price*max(ZERO, size-reduction)
        result.update(zip(names, (added/seconds, persistent/seconds, decreased/seconds)))
    return result


class CaptureFeatureReplay(Replay):
    """Extend state replay without changing the running recorder or raw input."""

    def __init__(self):
        super().__init__()
        self.flow_start = self.last_linear_ns = self.last_ticker_ns = None
        self.latest_available_ns = 0
        self.flows = deque()
        self.trade_ids = {}
        self.trade_expiry = deque()
        self.book_observations = deque()
        self.book_time_invalid = False
        self.states = {}

    def process(self, row, available_ns):
        self.latest_available_ns = available_ns
        kind, source = row['kind'], row.get('source')
        active = self.connections.get(source) == row.get('connection_id')
        message = json.loads(row['raw']) if kind == 'ws_message' and source == 'bybit_linear' and active else {}
        selected = message.get('topic') == 'orderbook.1000.BTCUSDT'
        old = self.books.get(BOOK_KEY)
        before = (dict(old.bids), dict(old.asks)) if selected and old and old.ready else None
        super().process(row, available_ns)
        if source == 'bybit_linear' and kind in ('connected', 'disconnected', 'connection_error'):
            if kind == 'connected' or active:
                self.flow_start = self.last_linear_ns = self.last_ticker_ns = None
                self.book_observations.clear()
                self.book_time_invalid = False
        if not message:
            return
        if self.last_linear_ns is not None and available_ns-self.last_linear_ns > MAX_SOURCE_SILENCE_NS:
            if self.flow_start is not None:
                self.flow_start = available_ns
        self.last_linear_ns = available_ns
        if message.get('op') == 'subscribe' and message.get('success') is True:
            if self.flow_start is None:
                self.flow_start = available_ns
        topic = message.get('topic', '')
        if topic in ('publicTrade.BTCUSDT', 'allLiquidation.BTCUSDT'):
            items = normalize_bybit_message(message, received_ms=row['received_ns']//1_000_000, market='linear')
            self._expire_flows(available_ns)
            for item in items:
                if item.event_ms*1_000_000 < available_ns-300*NS:
                    continue
                if isinstance(item, Trade):
                    identity = (item.event_ms, item.taker_side, item.base_size, item.price)
                    if not item.trade_id or item.trade_id == 'None':
                        raise ReplayError('missing trade ID')
                    if item.trade_id in self.trade_ids:
                        if self.trade_ids[item.trade_id] != identity:
                            raise ReplayError('conflicting duplicate trade')
                        continue
                    self.trade_ids[item.trade_id] = identity
                    self.trade_expiry.append((available_ns, item.trade_id))
                self.flows.append((available_ns, item))
        if topic == 'tickers.BTCUSDT':
            self.last_ticker_ns = available_ns
        if selected:
            self._observe_book(message, before, available_ns)

    def _expire_flows(self, boundary):
        while self.flows and self.flows[0][0] < boundary-300*NS:
            self.flows.popleft()
        while self.trade_expiry and self.trade_expiry[0][0] < boundary-300*NS:
            _, ident = self.trade_expiry.popleft()
            self.trade_ids.pop(ident, None)

    def _observe_book(self, message, before, available_ns):
        book = self.books[BOOK_KEY]
        event = int(message['ts'])*1_000_000
        reset = message['type'] == 'snapshot'
        if reset:
            self.book_time_invalid = False
        elif self.book_observations and event < self.book_observations[-1]['event_ns']:
            self.book_time_invalid = True
        # A reset/regression starts a new feature history. It must warm up
        # again rather than comparing unrelated price-level states.
        if reset or self.book_time_invalid or not book.ready:
            self.book_observations.clear()
        valid = book.ready and book.receipt_clock_valid and not self.book_time_invalid
        view = book.view(available_ns)
        changes = []
        known = {'bid': True, 'ask': True}
        if valid and before is not None and not reset:
            for side, previous, current in zip(('bid', 'ask'), before, (book.bids, book.asks)):
                prior_boundary = min(previous) if side == 'bid' else max(previous)
                for price in sorted(previous.keys() | current.keys()):
                    delta = current.get(price, ZERO)-previous.get(price, ZERO)
                    if delta:
                        changes.append((side, price, delta))
                        mid = view['midpoint']
                        inside = (mid*(1-BAND) <= price <= mid if side == 'bid'
                                  else mid <= price <= mid*(1+BAND))
                        prior_unknown = price < prior_boundary if side == 'bid' else price > prior_boundary
                        if delta > 0 and inside and prior_unknown:
                            # A top-N feed can reveal already-existing liquidity
                            # beyond its former boundary. Absence there was not
                            # evidence of zero size, even if both bands are full.
                            known[side] = False
        self.book_observations.append({'event_ns': event, 'available_ns': available_ns,
            'reset': reset, 'valid': valid, 'mid': view.get('midpoint'),
            'bid_covered': view.get('bid_band_covered', False),
            'ask_covered': view.get('ask_band_covered', False),
            'bid_changes_known': known['bid'], 'ask_changes_known': known['ask'], 'changes': changes})
        # Keep a single anchor at/before the oldest required flow window.
        while len(self.book_observations) > 1 and self.book_observations[1]['event_ns'] < available_ns-301*NS:
            self.book_observations.popleft()

    def grid(self, second):
        row = super().grid(second)
        boundary = second*NS
        book = self.books.get(BOOK_KEY)
        book_ok = (self.clock_valid and book and book.ready and book.receipt_clock_valid
                   and not self.book_time_invalid and 0 <= boundary-book.event_ns <= MAX_STATE_AGE_NS)
        view = row['books'].get(BOOK_KEY, {}) if book_ok else {}
        fields = row['bybit_linear_ticker']['fields']
        ticker_ok = (self.clock_valid and self.ticker.ready and self.ticker.receipt_clock_valid
                     and self.last_ticker_ns is not None
                     and 0 <= boundary-self.last_ticker_ns <= MAX_STATE_AGE_NS)
        def field(name, positive=True):
            item = fields.get(name)
            return (numeric(item['value'], positive=positive) if ticker_ok and item
                    and item['available_ns'] <= boundary and item['source_event_ns'] <= boundary else None)
        mark, index, funding = field('markPrice'), field('indexPrice'), field('fundingRate', False)
        bid, ask = view.get('bid_notional_25bps'), view.get('ask_notional_25bps')
        mid, spot = view.get('midpoint'), row['composite_price']
        top = book.top() if book_ok else None
        state = {'second': second, 'spot': spot, 'depth_bid': bid, 'depth_ask': ask,
            'oi': field('openInterest'), 'funding_bps': funding*BP if funding is not None else None,
            'mark_index_bps': (mark/index-1)*BP if mark and index else None,
            'basis_bps': (mid/spot-1)*BP if mid and spot else None,
            'spread_bps': (top[2]-top[0])/mid*BP if top else None,
            'book_imbalance': (bid-ask)/(bid+ask) if bid is not None and ask is not None and bid+ask else None}
        self.states[second] = state
        while len(self.states) > 1816:
            del self.states[next(iter(self.states))]
        self._expire_flows(boundary)
        return row

    def features(self, second):
        if second not in self.states:
            raise ReplayError('decision outside reconstructed grid')
        boundary = second*NS
        state = self.states[second]
        raw = {key: value for key, value in state.items() if key not in ('second', 'spot')}
        flow_ok = (self.clock_valid and self.flow_start is not None and self.last_linear_ns is not None
                   and boundary-self.last_linear_ns <= MAX_SOURCE_SILENCE_NS)
        observations = list(self.book_observations)
        for seconds in WINDOWS:
            left = boundary-seconds*NS
            complete = flow_ok and self.flow_start <= left
            for side in ('buy', 'sell'):
                trades = [x for _, x in self.flows if isinstance(x, Trade) and x.taker_side.lower() == side
                          and left < x.event_ms*1_000_000 <= boundary]
                liquidations = [x for _, x in self.flows if isinstance(x, Liquidation)
                                and x.pressure_side.lower() == side and left < x.event_ms*1_000_000 <= boundary]
                notional = sum((x.notional_quote for x in trades), ZERO) if complete else None
                raw[f'aggressive_{side}_notional_{seconds}s'] = notional
                raw[f'aggressive_{side}_rate_{seconds}s'] = notional/seconds if notional is not None else None
                raw[f'liquidation_{side}_size_base_{seconds}s'] = (sum((x.base_size for x in liquidations), ZERO)
                                                                  if complete else None)
                raw[f'liquidation_{side}_notional_{seconds}s'] = None
                raw[f'liquidation_{side}_rate_{seconds}s'] = None
            raw.update(book_window(observations, boundary, seconds))
            for side in ('bid', 'ask'):
                raw[f'cancel_{side}_rate_{seconds}s'] = None
                raw[f'execution_{side}_rate_{seconds}s'] = None
                raw[f'depth_{side}_lag_{seconds}s'] = self.states.get(second-seconds, {}).get('depth_'+side)
            path = [self.states.get(s, {}).get('spot') for s in range(second-seconds, second+1)]
            if all(p is not None and p > 0 for p in path):
                changes = [(b/a).ln() for a, b in zip(path, path[1:])]
                raw[f'return_{seconds}s'] = path[-1]/path[0]-1
                raw[f'realized_volatility_{seconds}s'] = sum((v*v for v in changes), ZERO).sqrt()
            else:
                raw[f'return_{seconds}s'] = raw[f'realized_volatility_{seconds}s'] = None
            oi_path = [self.states.get(s, {}).get('oi') for s in range(second-seconds, second+1)]
            good = all(v is not None and v > 0 for v in oi_path)
            raw[f'oi_change_{seconds}s'] = oi_path[-1]/oi_path[0]-1 if good else None
            raw[f'oi_log_change_{seconds}s'] = (oi_path[-1]/oi_path[0]).ln() if good else None
        scales = pretrigger_scales(self.states, second)
        bid, rate, scale = raw['depth_bid'], raw['persistent_bid_add_rate_15s'], scales['depth']
        raw['capacity_proxy'] = max(bid+30*rate, scale*Decimal('0.01')) if None not in (bid, rate, scale) else None
        if not self.clock_valid:
            raw = dict.fromkeys(raw)
            scales = dict.fromkeys(scales)
        shared, mfsm = normalized_features(raw, scales)
        missing = {}
        for key, value in raw.items():
            if value is not None:
                continue
            if not self.clock_valid:
                reason = 'receipt_clock_review_required'
            elif key.startswith('liquidation_') and '_size_base_' not in key:
                reason = 'bankruptcy_price_is_not_execution_price'
            elif key.startswith(('cancel_', 'execution_')):
                reason = 'aggregate_L2_cannot_attribute_removals'
            else:
                reason = 'insufficient_valid_history_or_coverage'
            missing[key] = reason
        return {'schema': 'E001-live-features-candidate-1', 'decision_second': second,
                'trigger_second_if_event': second-15, 'clock_valid': self.clock_valid,
                'latest_input_available_ns': self.latest_available_ns,
                'raw': raw, 'pretrigger_scales': scales, 'shared': shared, 'mfsm': mfsm,
                'missing_reasons': missing, 'ticker_provenance': self.ticker.view()['fields'],
                'limitations': {'aggressive_sell_may_include_liquidations': True,
                    'liquidation_deduplication_supported': False,
                    'trade_flow_completeness': 'observed_subscribed_connection_not_exhaustiveness_proof',
                    'depth_feed': BOOK_KEY, 'state_max_age_seconds': MAX_STATE_AGE_NS//NS},
                'full_common_feature_panel_complete': False, 'model_ready': False}


def feature_rows(records, decision_seconds, replay=None):
    decisions = set(decision_seconds)
    if not decisions or any(not isinstance(s, int) or s < 0 for s in decisions):
        raise ReplayError('explicit nonnegative integer decision seconds required')
    replay = replay or CaptureFeatureReplay()
    for row in replay_grid(records, replay):
        if row['second'] in decisions:
            yield replay.features(row['second'])
            decisions.remove(row['second'])
    if decisions:
        raise ReplayError('requested decision outside captured grid')
