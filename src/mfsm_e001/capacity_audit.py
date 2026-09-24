"""Audit whether the E001 visible-capacity proxy tracks realized BTC absorption."""

from collections import Counter
import csv
from decimal import Decimal, InvalidOperation
import gzip
from statistics import median

from .capture_features import book_window
from .liquidity_state import top_level_book
from .replay import NS


ZERO = Decimal(0)
BP = Decimal(10_000)
DEFAULT_BAND_BPS = Decimal(25)
MAX_BOOK_AGE_US = 5_000_000


def _book_view(bids, asks, *, epoch, last_us, boundary_us, band):
    bid = max(bids, default=None)
    ask = min(asks, default=None)
    if (bid is None or ask is None or bid >= ask or last_us is None or
            boundary_us < last_us or boundary_us-last_us > MAX_BOOK_AGE_US):
        return {'valid': False, 'top_valid': False, 'book_epoch': epoch}
    mid = (bid+ask)/2
    lower, upper = mid*(1-band), mid*(1+band)
    bid_covered = min(bids) <= lower
    ask_covered = max(asks) >= upper
    bid_coverage_bps = (mid-min(bids))/mid*BP
    ask_coverage_bps = (max(asks)-mid)/mid*BP
    depth = sum((price*size for price, size in bids.items() if price >= lower), ZERO)
    return {'valid': bid_covered and ask_covered, 'top_valid': True,
            'book_epoch': epoch,
            'depth_bid': depth if bid_covered else None, 'midpoint': mid,
            'spread_bps': (ask-bid)/mid*BP,
            'bid_covered': bid_covered, 'ask_covered': ask_covered,
            'bid_coverage_bps': bid_coverage_bps,
            'ask_coverage_bps': ask_coverage_bps}


def reconstruct_book_inputs(path, *, target_seconds, observation_ranges,
                            band_bps=DEFAULT_BAND_BPS, top_levels=None):
    """Stream one Tardis L2 day into only the event seconds and cohorts requested."""
    targets = sorted(set(target_seconds))
    band = Decimal(str(band_bps))/BP
    if band <= 0:
        raise ValueError('capacity band must be positive')
    if not targets:
        return {}, [], {'snapshot_cohorts': 0, 'delta_cohorts': 0,
                        'invalid_cohorts': 0}
    stop_us = max(targets[-1]*1_000_000,
                  max((right*1_000_000 for _, right in observation_ranges), default=0))
    target_index = 0
    states = {}
    observations = []
    diagnostics = Counter(snapshot_cohorts=0, delta_cohorts=0, invalid_cohorts=0)
    bids, asks = {}, {}
    initialized = False
    epoch = 0
    last_us = None

    def view(boundary_us, *, include_top_levels):
        result = _book_view(bids, asks, epoch=epoch, last_us=last_us,
                            boundary_us=boundary_us, band=band)
        if include_top_levels and top_levels is not None:
            result.update(top_level_book(
                bids, asks, levels=top_levels, epoch=epoch,
                last_us=last_us, boundary_us=boundary_us))
        return result

    def save_targets_before(stamp_us, *, inclusive=False):
        nonlocal target_index
        while target_index < len(targets):
            boundary_us = targets[target_index]*1_000_000
            if boundary_us > stamp_us or (boundary_us == stamp_us and not inclusive):
                break
            states[targets[target_index]] = view(
                boundary_us, include_top_levels=True)
            states[targets[target_index]]['second'] = targets[target_index]
            target_index += 1

    def in_observation_range(stamp_us):
        return any(left*1_000_000 <= stamp_us <= right*1_000_000
                   for left, right in observation_ranges)

    def apply_cohort(stamp_us, rows):
        nonlocal initialized, epoch, last_us, bids, asks
        snapshot = any(row['is_snapshot'].lower() == 'true' for row in rows)
        if snapshot and not all(row['is_snapshot'].lower() == 'true' for row in rows):
            diagnostics['invalid_cohorts'] += 1
            return
        previous = (dict(bids), dict(asks))
        if snapshot:
            bids, asks = {}, {}
            initialized = True
            epoch += 1
            diagnostics['snapshot_cohorts'] += 1
        else:
            diagnostics['delta_cohorts'] += 1
            if not initialized:
                return
        changes = []
        valid = True
        for row in rows:
            if row['exchange'] != 'bybit' or row['symbol'] != 'BTCUSDT' or row['side'] not in ('bid', 'ask'):
                valid = False
                break
            try:
                price, amount = Decimal(row['price']), Decimal(row['amount'])
            except InvalidOperation:
                valid = False
                break
            if not price.is_finite() or price <= 0 or not amount.is_finite() or amount < 0:
                valid = False
                break
            side = bids if row['side'] == 'bid' else asks
            old = side.get(price, ZERO)
            if amount:
                side[price] = amount
            else:
                side.pop(price, None)
            if not snapshot and amount != old:
                changes.append((row['side'], price, amount-old))
        if not valid:
            diagnostics['invalid_cohorts'] += 1
            initialized = False
            bids, asks = {}, {}
            return
        last_us = stamp_us
        observe = in_observation_range(stamp_us)
        cohort_view = view(stamp_us, include_top_levels=observe)
        known = {'bid': True, 'ask': True}
        if not snapshot and cohort_view.get('midpoint') is not None and previous[0] and previous[1]:
            mid = cohort_view['midpoint']
            for side_name, price, size in changes:
                if size <= 0:
                    continue
                prior = previous[0] if side_name == 'bid' else previous[1]
                outside = price < min(prior) if side_name == 'bid' else price > max(prior)
                inside = (mid*(1-band) <= price <= mid if side_name == 'bid'
                          else mid <= price <= mid*(1+band))
                if outside and inside:
                    known[side_name] = False
        if observe:
            observation = {
                'event_ns': stamp_us*1000, 'available_ns': stamp_us*1000,
                'reset': snapshot, 'valid': cohort_view['top_valid'],
                'mid': cohort_view.get('midpoint'),
                'bid_covered': cohort_view.get('bid_covered', False),
                'ask_covered': cohort_view.get('ask_covered', False),
                'bid_changes_known': known['bid'], 'ask_changes_known': known['ask'],
                'changes': changes, 'book_epoch': epoch}
            if top_levels is not None:
                observation.update(
                    top_level_valid=cohort_view['top_level_valid'],
                    top_bid_prices=cohort_view['top_bid_prices'],
                    top_ask_prices=cohort_view['top_ask_prices'])
            observations.append(observation)

    with gzip.open(path, 'rt', newline='') as stream:
        reader = csv.DictReader(stream)
        required = {'exchange', 'symbol', 'local_timestamp', 'is_snapshot',
                    'side', 'price', 'amount'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('invalid Tardis L2 columns')
        cohort_stamp = None
        cohort = []
        for row in reader:
            stamp = int(row['local_timestamp'])
            if cohort_stamp is not None and stamp < cohort_stamp:
                raise ValueError('L2 receipt timestamp regressed')
            if cohort_stamp is None:
                cohort_stamp = stamp
            if stamp != cohort_stamp:
                save_targets_before(cohort_stamp)
                apply_cohort(cohort_stamp, cohort)
                save_targets_before(cohort_stamp, inclusive=True)
                if stamp > stop_us and target_index == len(targets):
                    cohort_stamp, cohort = None, []
                    break
                cohort_stamp, cohort = stamp, []
            cohort.append(row)
        if cohort_stamp is not None:
            save_targets_before(cohort_stamp)
            apply_cohort(cohort_stamp, cohort)
            save_targets_before(cohort_stamp, inclusive=True)
    while target_index < len(targets):
        second = targets[target_index]
        states[second] = view(second*1_000_000, include_top_levels=True)
        states[second]['second'] = second
        target_index += 1
    return states, observations, dict(diagnostics)


def read_capacity_trades(path, *, windows):
    """Read Bybit trades whose receipt timestamps fall in requested windows."""
    if not windows:
        return [], {'rows_read': 0, 'selected_trades': 0, 'invalid_rows': 0}
    bounds = [(left*1_000_000, right*1_000_000) for left, right in windows]
    stop_us = max(right for _, right in bounds)
    trades = []
    diagnostics = Counter(rows_read=0, selected_trades=0, invalid_rows=0)
    previous_us = None
    with gzip.open(path, 'rt', newline='') as stream:
        reader = csv.DictReader(stream)
        required = {'exchange', 'symbol', 'local_timestamp', 'side', 'price', 'amount'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('invalid Tardis trade columns')
        for row in reader:
            try:
                received_us = int(row['local_timestamp'])
            except ValueError as exc:
                raise ValueError('invalid trade receipt timestamp') from exc
            if previous_us is not None and received_us < previous_us:
                raise ValueError('trade receipt timestamp regressed')
            previous_us = received_us
            if received_us > stop_us:
                break
            diagnostics['rows_read'] += 1
            if (row['exchange'] != 'bybit' or row['symbol'] != 'BTCUSDT' or
                    row['side'] not in ('buy', 'sell')):
                diagnostics['invalid_rows'] += 1
                raise ValueError('invalid Bybit BTC trade row')
            try:
                price, amount = Decimal(row['price']), Decimal(row['amount'])
            except InvalidOperation as exc:
                diagnostics['invalid_rows'] += 1
                raise ValueError('invalid trade price or amount') from exc
            if (not price.is_finite() or price <= 0 or not amount.is_finite() or
                    amount <= 0):
                diagnostics['invalid_rows'] += 1
                raise ValueError('invalid trade price or amount')
            if any(left < received_us <= right for left, right in bounds):
                trades.append({'received_us': received_us, 'side': row['side'],
                               'notional': price*amount})
                diagnostics['selected_trades'] += 1
    return trades, dict(diagnostics)


def _sell_notional(trades, left_us, right_us):
    return sum((row['notional'] for row in trades
                if row['side'] == 'sell' and left_us < row['received_us'] <= right_us), ZERO)


def _ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0]*len(values)
    start = 0
    while start < len(order):
        end = start+1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start+end-1)/2+1
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def _spearman(left, right):
    if len(left) < 2:
        return None
    x, y = _ranks(left), _ranks(right)
    xbar, ybar = sum(x)/len(x), sum(y)/len(y)
    numerator = sum((a-xbar)*(b-ybar) for a, b in zip(x, y))
    xscale = sum((a-xbar)**2 for a in x)
    yscale = sum((b-ybar)**2 for b in y)
    return numerator/(xscale*yscale)**0.5 if xscale and yscale else None


def summarize_capacity_audit(rows, *, minimum_independent):
    """Summarize crossings without treating locked-out rows as independent."""
    valid = [row for row in rows if row['valid']]
    independent = [row for row in valid
                   if row.get('history_qualified', row['accepted'])]
    censored = [row for row in valid if row['first_25bps_breach_seconds'] is None]
    summary = {
        'crossings': len(rows),
        'valid_crossings': len(valid),
        'valid_independent_episodes': len(independent),
        'right_censored_crossings': len(censored),
        'breached_crossings': len(valid)-len(censored),
        'capacity_under_observed_no_breach_crossings': sum(
            row['future_sell_notional_30s'] > row['capacity_proxy'] for row in censored),
        'exclusion_counts': dict(sorted(Counter(
            row['reason'] for row in rows if not row['valid']).items())),
    }
    coverage = [row['pretrigger_bid_coverage_bps_min'] for row in rows
                if row.get('pretrigger_bid_coverage_bps_min') is not None]
    if coverage:
        summary['excluded_pretrigger_minimum_bid_coverage_bps'] = {
            'minimum': min(coverage), 'median': median(coverage),
            'maximum': max(coverage),
        }
    if len(independent) < minimum_independent:
        summary['rank_correlations'] = {
            'status': 'not_computed',
            'reason': (f'{len(independent)} valid independent episodes; minimum is '
                       f'{minimum_independent}'),
        }
        return summary
    metrics = {}
    for name in ('future_sell_notional_30s', 'depth_ratio_30s', 'mid_return_bps_30s'):
        metrics[f'capacity_vs_{name}'] = _spearman(
            [row['capacity_proxy'] for row in independent],
            [row[name] for row in independent])
    uncensored = [row for row in independent
                  if row['first_25bps_breach_seconds'] is not None]
    metrics['capacity_vs_uncensored_sell_before_breach'] = (
        _spearman([row['capacity_proxy'] for row in uncensored],
                  [row['sell_notional_before_25bps_breach'] for row in uncensored])
        if len(uncensored) >= minimum_independent else None)
    summary['rank_correlations'] = {
        'status': 'computed_descriptive', 'independent_episodes': len(independent),
        'metrics': metrics,
    }
    return summary


def audit_capacity_event(states, observations, trades, *, trigger_s,
                         capacity_band_bps=DEFAULT_BAND_BPS,
                         breach_bps=DEFAULT_BAND_BPS):
    """Compare a causal decision-time capacity proxy with the next 30 seconds."""
    decision = trigger_s+15
    pre = [states.get(second) for second in range(trigger_s-1800, trigger_s)]
    if len(pre) != 1800 or any(row is None for row in pre):
        return {'valid': False, 'reason': 'missing_pretrigger_book_state'}
    if any(row.get('top_valid', row.get('valid')) is not True for row in pre):
        return {'valid': False, 'reason': 'invalid_or_stale_pretrigger_book_state'}
    if any(row.get('bid_covered', row.get('valid')) is not True for row in pre):
        coverage = [row.get('bid_coverage_bps') for row in pre
                    if row.get('bid_coverage_bps') is not None]
        result = {'valid': False, 'reason': 'incomplete_pretrigger_bid_band'}
        if coverage:
            result.update(pretrigger_bid_coverage_bps_min=min(coverage),
                          pretrigger_bid_coverage_bps_median=median(coverage),
                          pretrigger_bid_coverage_bps_max=max(coverage))
        return result
    if any(row.get('depth_bid') is None or row['depth_bid'] <= 0 for row in pre):
        return {'valid': False, 'reason': 'invalid_pretrigger_bid_depth'}
    future = [states.get(second) for second in range(decision, decision+31)]
    if any(row is None for row in future):
        return {'valid': False, 'reason': 'missing_decision_or_outcome_book_state'}
    if any(row.get('top_valid', row.get('valid')) is not True for row in future):
        return {'valid': False, 'reason': 'invalid_or_stale_decision_or_outcome_book_state'}
    if any(row.get('bid_covered', row.get('valid')) is not True for row in future):
        return {'valid': False, 'reason': 'incomplete_decision_or_outcome_bid_band'}
    if any(row.get('depth_bid') is None or row.get('midpoint') is None or
           row.get('spread_bps') is None for row in future):
        return {'valid': False, 'reason': 'invalid_decision_or_outcome_book_metrics'}
    epochs = {row['book_epoch'] for row in pre+future}
    if len(epochs) != 1:
        return {'valid': False, 'reason': 'book_reset_inside_required_window'}
    available = [row for row in observations if row['available_ns'] <= decision*NS]
    window = book_window(available, decision*NS, 15,
                         band=Decimal(str(capacity_band_bps))/BP)
    rate = window['persistent_bid_add_rate_15s']
    if rate is None:
        return {'valid': False, 'reason': 'incomplete_replenishment_history'}
    pre_depth = median(row['depth_bid'] for row in pre)
    decision_state = future[0]
    raw_capacity = decision_state['depth_bid']+Decimal(30)*rate
    floor = pre_depth*Decimal('0.01')
    capacity = max(raw_capacity, floor)
    decision_us = decision*1_000_000
    future_sell = _sell_notional(trades, decision_us, (decision+30)*1_000_000)
    breach = next((offset for offset, row in enumerate(future[1:], start=1)
                   if row['midpoint']/decision_state['midpoint']-1 <=
                   -Decimal(str(breach_bps))/BP), None)
    breach_end = decision+breach if breach is not None else decision+30
    result = {
        'valid': True, 'reason': None, 'trigger_s': trigger_s, 'decision_s': decision,
        'pre_depth_median': pre_depth,
        'decision_bid_depth': decision_state['depth_bid'],
        'replenishment_rate_15s': rate,
        'raw_capacity_proxy': raw_capacity, 'capacity_floor': floor,
        'capacity_proxy': capacity,
        'predecision_sell_notional_30s': _sell_notional(
            trades, (decision-30)*1_000_000, decision_us),
        'future_sell_notional_30s': future_sell,
        'sell_notional_before_25bps_breach': _sell_notional(
            trades, decision_us, breach_end*1_000_000),
        'first_25bps_breach_seconds': breach,
    }
    for offset in (5, 15, 30):
        row = future[offset]
        result[f'depth_ratio_{offset}s'] = row['depth_bid']/decision_state['depth_bid']
        result[f'mid_return_bps_{offset}s'] = (
            row['midpoint']/decision_state['midpoint']-1)*BP
        result[f'spread_change_bps_{offset}s'] = (
            row['spread_bps']-decision_state['spread_bps'])
    return result
