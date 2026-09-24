"""Receipt-time top-level BTC liquidity measurements for a separate study.

Displayed depth, additions and observed trade flow describe market state. They
are not an estimate of maximum sell flow the market can absorb.
"""

from bisect import bisect_right
from collections import defaultdict
from decimal import Decimal
from statistics import median


ZERO = Decimal(0)
BP = Decimal(10_000)
NS = 1_000_000_000
MAX_BOOK_AGE_US = 5_000_000
MAX_BOOK_AGE_NS = 5*NS
PRETRIGGER_SECONDS = 1800
MIN_VALID_PRETRIGGER_SECONDS = 1710
MAX_PRETRIGGER_GAP_SECONDS = 5


def top_level_book(bids, asks, *, levels, epoch, last_us, boundary_us):
    """Value exactly the best ``levels`` on each side of a reconstructed book."""
    if type(levels) is not int or levels < 1:
        raise ValueError('top-level count must be a positive integer')
    result = {'top_level_valid': False, 'book_epoch': epoch,
              'top_bid_notional': None, 'top_ask_notional': None,
              'top_bid_prices': (), 'top_ask_prices': ()}
    if (last_us is None or boundary_us < last_us or
            boundary_us-last_us > MAX_BOOK_AGE_US):
        return {**result, 'reason': 'book_missing_or_stale'}
    if not bids or not asks:
        return {**result, 'reason': 'book_side_empty'}
    top_bid = sorted(bids, reverse=True)[:levels]
    top_ask = sorted(asks)[:levels]
    if top_bid[0] >= top_ask[0]:
        return {**result, 'reason': 'crossed_or_locked_book'}
    if len(top_bid) < levels or len(top_ask) < levels:
        return {**result, 'reason': 'insufficient_book_levels',
                'available_bid_levels': len(top_bid),
                'available_ask_levels': len(top_ask)}
    mid = (top_bid[0]+top_ask[0])/2
    bid_value = sum((price*bids[price] for price in top_bid), ZERO)
    ask_value = sum((price*asks[price] for price in top_ask), ZERO)
    if bid_value <= 0 or ask_value <= 0:
        return {**result, 'reason': 'nonpositive_top_level_depth'}
    return {**result, 'top_level_valid': True, 'reason': None,
            'top_bid_notional': bid_value, 'top_ask_notional': ask_value,
            'top_bid_prices': tuple(top_bid), 'top_ask_prices': tuple(top_ask),
            'midpoint': mid, 'spread_bps': (top_ask[0]-top_bid[0])/mid*BP,
            'imbalance': (bid_value-ask_value)/(bid_value+ask_value)}


def persistent_top_bid_add_rate(observations, *, boundary_ns, window_seconds=15):
    """Credit additions that remain in the top levels one second later.

    The input is a receipt-ordered sequence of reconstructed book cohorts.
    Decreases at the same price during dwell reduce an addition's credit.
    """
    if type(window_seconds) is not int or window_seconds < 2:
        raise ValueError('invalid replenishment window')
    left = boundary_ns-window_seconds*NS
    available = [row for row in observations if row['available_ns'] <= boundary_ns]
    times = [row['event_ns'] for row in available]
    if times != sorted(times):
        raise ValueError('book observations are not receipt ordered')
    anchor_index = bisect_right(times, left)-1
    if anchor_index < 0:
        return {'valid': False, 'reason': 'no_replenishment_anchor'}
    relevant = available[anchor_index:]
    if boundary_ns-relevant[-1]['event_ns'] > MAX_BOOK_AGE_NS:
        return {'valid': False, 'reason': 'stale_replenishment_endpoint'}
    if any(row.get('reset') and row['event_ns'] > left for row in relevant):
        return {'valid': False, 'reason': 'book_reset_in_window'}
    if len({row.get('book_epoch') for row in relevant}) != 1:
        return {'valid': False, 'reason': 'book_epoch_changed_in_window'}
    if any(not row.get('top_level_valid') for row in relevant):
        return {'valid': False, 'reason': 'incomplete_top_levels_in_window'}
    if any(not row.get('bid_changes_known', False)
           for row in relevant if row['event_ns'] >= left):
        return {'valid': False, 'reason': 'unknown_bid_change'}
    if any(later['event_ns']-earlier['event_ns'] > MAX_BOOK_AGE_NS
           for earlier, later in zip(relevant, relevant[1:])):
        return {'valid': False, 'reason': 'book_update_gap_in_window'}

    # Collapse changes within each same-timestamp cohort before calculating
    # additions and decreases. Internal row order cannot create a real dwell.
    events = []
    decreases = defaultdict(list)
    for row in relevant:
        if row['event_ns'] <= left:
            continue
        net = defaultdict(lambda: ZERO)
        for side, price, amount in row['changes']:
            if side == 'bid':
                net[price] += amount
        for price, amount in net.items():
            if amount:
                events.append((row, price, amount))
                if amount < 0:
                    decreases[price].append((row['event_ns'], -amount))
    prefixes = {}
    for price, changes in decreases.items():
        stamps = []
        cumulative = [ZERO]
        for stamp, amount in changes:
            stamps.append(stamp)
            cumulative.append(cumulative[-1]+amount)
        prefixes[price] = (stamps, cumulative)

    gross = persistent = ZERO
    for row, price, amount in events:
        if amount <= 0 or price not in row['top_bid_prices']:
            continue
        gross += price*amount
        endpoint = row['event_ns']+NS
        if endpoint > boundary_ns:
            continue
        endpoint_index = bisect_right(times, endpoint)-1
        end_state = available[endpoint_index]
        if price not in end_state['top_bid_prices']:
            continue
        reduction = ZERO
        if price in prefixes:
            stamps, cumulative = prefixes[price]
            reduction = (cumulative[bisect_right(stamps, endpoint)]-
                         cumulative[bisect_right(stamps, row['event_ns'])])
        persistent += price*max(amount-reduction, ZERO)
    return {'valid': True, 'reason': None,
            'gross_bid_add_rate': gross/window_seconds,
            'persistent_bid_add_rate': persistent/window_seconds}


def decision_liquidity_state(states, observations, trades, *, trigger_s,
                             levels=50):
    """Build one causal top-level feature row at the existing t0+15s decision."""
    decision = trigger_s+15
    current = states.get(decision)
    if current is None or not current.get('top_level_valid'):
        return {'valid': False, 'reason': 'decision_book_unavailable'}
    history = [states.get(second) for second in range(
        trigger_s-PRETRIGGER_SECONDS, trigger_s)]
    if any(row is None for row in history):
        return {'valid': False, 'reason': 'pretrigger_history_incomplete'}
    if any(row.get('book_epoch') != current.get('book_epoch') for row in history):
        return {'valid': False, 'reason': 'book_epoch_changed_in_history'}
    valid = [row for row in history if row.get('top_level_valid') and
             row.get('top_bid_notional', ZERO) > 0 and
             row.get('top_ask_notional', ZERO) > 0]
    gap = longest_gap = 0
    for row in history:
        gap = 0 if row in valid else gap+1
        longest_gap = max(longest_gap, gap)
    if longest_gap > MAX_PRETRIGGER_GAP_SECONDS:
        return {'valid': False, 'reason': 'pretrigger_book_gap_exceeds_5s'}
    if len(valid) < MIN_VALID_PRETRIGGER_SECONDS:
        return {'valid': False, 'reason': 'pretrigger_book_coverage_below_95pct'}
    replenish = persistent_top_bid_add_rate(
        observations, boundary_ns=decision*NS, window_seconds=15)
    if not replenish['valid']:
        return {'valid': False, 'reason': replenish['reason']}
    bid_scale = median(row['top_bid_notional'] for row in valid)
    ask_scale = median(row['top_ask_notional'] for row in valid)
    total_scale = bid_scale+ask_scale
    start_us, decision_us = (decision-30)*1_000_000, decision*1_000_000
    past = [row for row in trades
            if start_us < row['received_us'] <= decision_us]
    buy = sum((row['notional'] for row in past if row['side'] == 'buy'), ZERO)
    sell = sum((row['notional'] for row in past if row['side'] == 'sell'), ZERO)
    bid, ask = current['top_bid_notional'], current['top_ask_notional']
    return {
        'valid': True, 'reason': None, 'schema': 'E001-top-level-liquidity-state-1',
        'trigger_s': trigger_s, 'decision_s': decision, 'levels_per_side': levels,
        'valid_pretrigger_seconds': len(valid),
        'pretrigger_bid_median': bid_scale, 'pretrigger_ask_median': ask_scale,
        'top_bid_notional': bid, 'top_ask_notional': ask,
        'top_bid_relative': bid/bid_scale, 'top_ask_relative': ask/ask_scale,
        'imbalance': (bid-ask)/(bid+ask), 'spread_bps': current['spread_bps'],
        'gross_bid_add_rate_15s': replenish['gross_bid_add_rate'],
        'persistent_bid_add_rate_15s': replenish['persistent_bid_add_rate'],
        'persistent_bid_add_relative_15s': (
            replenish['persistent_bid_add_rate']*15/bid_scale),
        'observed_trades_30s': len(past),
        'buy_notional_30s': buy, 'sell_notional_30s': sell,
        'net_buy_notional_30s': buy-sell,
        'gross_trade_notional_30s': buy+sell,
        'buy_relative_total_depth_30s': buy/total_scale,
        'sell_relative_total_depth_30s': sell/total_scale,
        'net_buy_relative_total_depth_30s': (buy-sell)/total_scale,
        'gross_trade_relative_total_depth_30s': (buy+sell)/total_scale,
        'source_freshness_certified': False,
        'model_ready': False,
    }


def liquidity_model_features(state):
    """Return the frozen matched B4/MFSM inputs for E001-LIQ-OBS-1."""
    if not isinstance(state, dict) or state.get('valid') is not True:
        return {'shared': {}, 'mfsm': {}, 'ready': False}
    shared_names = (
        'top_bid_relative', 'top_ask_relative', 'imbalance', 'spread_bps',
        'buy_relative_total_depth_30s', 'sell_relative_total_depth_30s',
        'gross_trade_relative_total_depth_30s',
        'persistent_bid_add_relative_15s',
    )
    shared = {name: state.get(name) for name in shared_names}
    if any(value is None for value in shared.values()):
        return {'shared': {}, 'mfsm': {}, 'ready': False}
    bid_relative = shared['top_bid_relative']
    replenish = shared['persistent_bid_add_relative_15s']
    sell_pressure = shared['sell_relative_total_depth_30s']
    if bid_relative <= 0 or replenish < 0 or sell_pressure < 0:
        return {'shared': {}, 'mfsm': {}, 'ready': False}
    mfsm = dict(shared)
    mfsm['sell_pressure_x_inverse_bid_depth'] = sell_pressure/bid_relative
    mfsm['sell_pressure_x_inverse_replenishment'] = sell_pressure/(1+replenish)
    return {'shared': shared, 'mfsm': mfsm, 'ready': True}
