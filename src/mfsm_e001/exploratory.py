"""Fixed, exploratory BTC receipt-time study on Tardis free sample days.

This is a different observational question from the shock-triggered E001
experiment. It never certifies exchange-to-collector source age or profit.
"""

from bisect import bisect_left, bisect_right
from collections import Counter
import csv
from datetime import date, datetime, timezone
import gzip
import json
import math
from pathlib import Path

from .capture_store import sha256
from .models import TUNING_GRID, fit_calibrated, probabilities
from .spot_quotes import iter_quote_grid
from .validation import prepare_rows


class InsufficientDataError(ValueError):
    """A frozen study could not meet its predeclared sample gate."""


def validate_protocol(protocol):
    """Reject edits that the version-one feature builder would not honor."""
    pinned = {
        'schema': 'E001-OBS-exploratory-protocol-1',
        'status': 'predeclared_before_model_scoring',
        'data_kind': 'exploratory_tardis_btc',
        'dates': [f'{year}-{month:02d}-01'
                  for year, months in ((2025, range(3, 13)), (2026, range(1, 10)))
                  for month in months],
        'asset': 'BTC',
        'spot_venues': ['binance', 'bybit-spot'],
        'spot_reference': 'equal_weight_midquote_at_local_receipt_cutoff',
        'spot_max_receipt_age_seconds': 5,
        'decision_hours_utc_inclusive': [2, 22],
        'decision_spacing_seconds': 3600,
        'label_horizon_seconds': 1800,
        'label_lower_barrier': -0.005,
        'label_upper_barrier': 0.00375,
        'label_none_by_horizon_value': 0,
        'predecision_spot_history_seconds': 300,
        'trade_flow_window_seconds': 30,
        'minimum_observed_trades_in_window': 1,
        'ticker_max_receipt_age_seconds': 30,
        'shared_features': [
            'spot_return_300s', 'spot_realized_vol_300s', 'spot_spread_bps',
            'cross_venue_mid_disagreement_bps', 'oi_change_300s',
            'mark_index_bps', 'sell_notional_rel_oi_30s'],
        'mfsm_combinations': ['sell_pressure_x_spread'],
        'tuning_grid': list(TUNING_GRID),
        'outer_folds_by_date_index_inclusive': [
            {'fit': [0, 6], 'calibration': [7, 9], 'validation': [10, 11], 'test': [12, 14]},
            {'fit': [0, 9], 'calibration': [10, 12], 'validation': [13, 14], 'test': [15, 18]},
        ],
        'minimum_fit_rows': 50,
        'minimum_calibration_rows': 20,
        'minimum_validation_rows': 20,
        'minimum_test_rows': 20,
        'classes_required_in_fit_and_calibration': [0, 1],
        'primary_metric': 'paired_mean_Brier_improvement_MFSM_over_B4',
        'eth_access': 'sealed',
    }
    for key, expected in pinned.items():
        if protocol.get(key) != expected:
            raise ValueError(f'unsupported exploratory protocol field: {key}')
    if any(date.fromisoformat(day).day != 1 for day in protocol['dates']):
        raise ValueError('invalid first-of-month sample date')


def hourly_label(prices, decision_offset, horizon_s, lower_return, upper_return):
    """First passage strictly after an hourly decision; no gap interpolation."""
    if decision_offset < 0 or decision_offset >= len(prices) or prices[decision_offset] is None:
        return {'valid': False, 'value': None, 'state': None,
                'reason': 'missing_decision_price', 'first_hit_offset': None}
    reference = prices[decision_offset]
    lower, upper = reference*(1+lower_return), reference*(1+upper_return)
    for offset in range(decision_offset+1, decision_offset+horizon_s+1):
        if offset >= len(prices) or prices[offset] is None:
            return {'valid': False, 'value': None, 'state': None,
                    'reason': 'missing_price_before_hit', 'first_hit_offset': None}
        if prices[offset] <= lower:
            return {'valid': True, 'value': 1, 'state': 'downside-first',
                    'reason': None, 'first_hit_offset': offset}
        if prices[offset] >= upper:
            return {'valid': True, 'value': 0, 'state': 'recovery-first',
                    'reason': None, 'first_hit_offset': offset}
    return {'valid': True, 'value': 0, 'state': 'neither-by-horizon',
            'reason': None, 'first_hit_offset': None}


def fixed_calendar_splits(rows, fold_specs, *, minimums):
    """Expand predeclared day ranges to episode indices and enforce maturity."""
    if not rows or any(rows[i]['decision_s'] >= rows[i+1]['decision_s']
                       for i in range(len(rows)-1)):
        raise ValueError('unordered exploratory episodes')
    folds = []
    for spec in fold_specs:
        fold = {}
        for role in ('fit', 'calibration', 'validation', 'test'):
            first, last = spec[role]
            if type(first) is not int or type(last) is not int or first > last:
                raise ValueError('invalid calendar fold')
            fold[role] = [i for i, row in enumerate(rows)
                          if first <= row['date_index'] <= last]
            if len(fold[role]) < minimums[role]:
                raise InsufficientDataError(f'insufficient {role} episodes in fixed calendar fold')
        for earlier, later in (('fit', 'calibration'), ('calibration', 'validation'),
                               ('validation', 'test')):
            if max(fold[earlier]) >= min(fold[later]):
                raise ValueError('overlapping or unordered calendar blocks')
            cutoff = rows[fold[later][0]]['decision_s']*1000
            if any(rows[i]['maturity_ms'] > cutoff for i in fold[earlier]):
                raise ValueError('immature label crosses calendar cutoff')
        for role in ('fit', 'calibration'):
            if {rows[i]['y'] for i in fold[role]} != {0, 1}:
                raise InsufficientDataError(f'both classes required in {role}')
        folds.append(fold)
    tests = [i for fold in folds for i in fold['test']]
    if len(set(tests)) != len(tests):
        raise ValueError('outer test episodes overlap')
    return folds


def _verified_files(root, day):
    folder = Path(root)/'data/raw/tardis'/day
    manifest = json.loads((folder/'manifest.json').read_text())
    names = {
        'binance_quotes': f'binance_quotes_{day}_BTCUSDT.csv.gz',
        'bybit_spot_quotes': f'bybit-spot_quotes_{day}_BTCUSDT.csv.gz',
        'bybit_trades': f'bybit_trades_{day}_BTCUSDT.csv.gz',
        'bybit_ticker': f'bybit_derivative_ticker_{day}_BTCUSDT.csv.gz',
    }
    paths = {}
    hashes = {}
    for role, name in names.items():
        path = folder/name
        actual = sha256(path)
        if manifest.get(name, {}).get('sha256') != actual:
            raise ValueError(f'Tardis source integrity mismatch: {name}')
        paths[role], hashes[role] = path, actual
    return paths, hashes


def _ticker_states(path):
    times, values = [], []
    with gzip.open(path, 'rt', newline='') as stream:
        reader = csv.DictReader(stream)
        required = {'exchange', 'symbol', 'local_timestamp', 'open_interest',
                    'mark_price', 'index_price'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('invalid derivative ticker columns')
        for row in reader:
            if row['exchange'] != 'bybit' or row['symbol'] != 'BTCUSDT':
                raise ValueError('out-of-scope derivative ticker')
            stamp = int(row['local_timestamp'])
            if times and stamp < times[-1]:
                raise ValueError('ticker receipt order regressed')
            def positive(name):
                try:
                    value = float(row[name])
                except (TypeError, ValueError):
                    return None
                return value if math.isfinite(value) and value > 0 else None
            times.append(stamp)
            values.append((positive('open_interest'), positive('mark_price'),
                           positive('index_price')))
    return times, values


def _ticker_at(times, values, cutoff_us, max_age_us):
    pos = bisect_right(times, cutoff_us)-1
    if pos < 0 or cutoff_us-times[pos] > max_age_us:
        return None
    return values[pos] if all(value is not None for value in values[pos]) else None


def _trade_windows(path, decisions_us, window_us):
    counts = [0]*len(decisions_us)
    sells = [0.0]*len(decisions_us)
    previous = -1
    with gzip.open(path, 'rt', newline='') as stream:
        reader = csv.DictReader(stream)
        required = {'exchange', 'symbol', 'local_timestamp', 'side', 'price', 'amount'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('invalid perpetual trade columns')
        for row in reader:
            if row['exchange'] != 'bybit' or row['symbol'] != 'BTCUSDT':
                raise ValueError('out-of-scope perpetual trade')
            stamp = int(row['local_timestamp'])
            if stamp < previous:
                raise ValueError('trade receipt order regressed')
            previous = stamp
            side = row['side'].lower()
            if side not in ('buy', 'sell'):
                raise ValueError('invalid trade side')
            price, amount = float(row['price']), float(row['amount'])
            if not all(math.isfinite(v) and v > 0 for v in (price, amount)):
                raise ValueError('invalid trade value')
            index = bisect_left(decisions_us, stamp)
            if index >= len(decisions_us) or stamp <= decisions_us[index]-window_us:
                continue
            counts[index] += 1
            if side == 'sell':
                sells[index] += price*amount
    return counts, sells


def build_exploratory_day(root, day, date_index, protocol):
    """One source-verified day with fixed hourly decisions and explicit exclusions."""
    validate_protocol(protocol)
    if protocol['dates'][date_index] != day:
        raise ValueError('day is not at its frozen protocol index')
    paths, hashes = _verified_files(root, day)
    midnight = int(datetime.combine(date.fromisoformat(day), datetime.min.time(),
                                    tzinfo=timezone.utc).timestamp())
    hours = range(protocol['decision_hours_utc_inclusive'][0],
                  protocol['decision_hours_utc_inclusive'][1]+1)
    offsets = [hour*3600 for hour in hours]
    decisions_us = [(midnight+offset)*1_000_000 for offset in offsets]
    prices = [None]*86400
    quote_metrics = {}
    decision_set = set(offsets)
    for grid in iter_quote_grid(paths['binance_quotes'], paths['bybit_spot_quotes'],
                                start_s=midnight, end_s=midnight+86399):
        offset = grid.second-midnight
        q = (grid.binance, grid.bybit)
        cutoff = grid.second*1_000_000
        if not all(x is not None and x.midpoint is not None and x.invalid_reason is None and
                   0 <= cutoff-x.received_us <= protocol['spot_max_receipt_age_seconds']*1_000_000
                   for x in q):
            continue
        mid = (float(q[0].midpoint)+float(q[1].midpoint))/2
        prices[offset] = mid
        if offset in decision_set:
            quote_metrics[offset] = {
                'spot_spread_bps': (float(q[0].spread_bps)+float(q[1].spread_bps))/2,
                'cross_venue_mid_disagreement_bps':
                    abs(float(q[0].midpoint)-float(q[1].midpoint))/mid*10_000}
    ticker_times, ticker_values = _ticker_states(paths['bybit_ticker'])
    trade_counts, sell_notionals = _trade_windows(
        paths['bybit_trades'], decisions_us,
        protocol['trade_flow_window_seconds']*1_000_000)
    episodes = []
    exclusions = Counter()
    for index, offset in enumerate(offsets):
        decision = midnight+offset
        label = hourly_label(prices, offset, protocol['label_horizon_seconds'],
                             protocol['label_lower_barrier'], protocol['label_upper_barrier'])
        label['training_maturity_ms'] = (decision+protocol['label_horizon_seconds'])*1000 if label['valid'] else None
        reasons = []
        history_s = protocol['predecision_spot_history_seconds']
        path = prices[offset-history_s:offset+1]
        if len(path) != history_s+1 or any(value is None or value <= 0 for value in path):
            reasons.append('missing_spot_feature_history')
        if offset not in quote_metrics:
            reasons.append('missing_decision_quote')
        ticker = _ticker_at(ticker_times, ticker_values, decision*1_000_000,
                            protocol['ticker_max_receipt_age_seconds']*1_000_000)
        earlier = _ticker_at(ticker_times, ticker_values, (decision-history_s)*1_000_000,
                             protocol['ticker_max_receipt_age_seconds']*1_000_000)
        if ticker is None or earlier is None:
            reasons.append('missing_fresh_ticker_or_oi_history')
        if trade_counts[index] < protocol['minimum_observed_trades_in_window']:
            reasons.append('unobserved_trade_window')
        if not label['valid']:
            reasons.append('label_'+label['reason'])
        shared = mfsm = None
        if not reasons:
            changes = [math.log(b/a) for a, b in zip(path, path[1:])]
            sell_rel_oi = sell_notionals[index]/(ticker[0]*prices[offset])
            shared = {
                'spot_return_300s': prices[offset]/path[0]-1,
                'spot_realized_vol_300s': math.sqrt(sum(v*v for v in changes)),
                **quote_metrics[offset],
                'oi_change_300s': ticker[0]/earlier[0]-1,
                'mark_index_bps': (ticker[1]/ticker[2]-1)*10_000,
                'sell_notional_rel_oi_30s': sell_rel_oi}
            mfsm = {**shared,
                    'sell_pressure_x_spread': sell_rel_oi*shared['spot_spread_bps']}
        for reason in reasons:
            exclusions[reason] += 1
        episodes.append({'episode_id': f'E001-OBS-{day}-{offset//3600:02d}',
                         'date': day, 'date_index': date_index, 'decision_s': decision,
                         'primary_eligible': not reasons,
                         'primary_label': label,
                         'shared': shared, 'mfsm': mfsm,
                         'exclusion_reasons': reasons,
                         'source_sha256': hashes})
    return {'date': day, 'source_sha256': hashes, 'scheduled_decisions': len(offsets),
            'eligible_decisions': sum(e['primary_eligible'] for e in episodes),
            'exclusions': dict(sorted(exclusions.items())), 'episodes': episodes}


def _brier(rows, indices, predicted):
    return sum((probability-rows[index]['y'])**2
               for index, probability in zip(indices, predicted))/len(indices)


def evaluate_exploratory(episodes, protocol):
    """Matched, frozen-calendar out-of-sample score for the observational study."""
    validate_protocol(protocol)
    eligible = [episode for episode in episodes if episode['primary_eligible']]
    rows = prepare_rows(eligible, protocol['shared_features'], protocol['mfsm_combinations'])
    if not rows:
        raise InsufficientDataError('no eligible exploratory episodes')
    for row, episode in zip(rows, eligible):
        row['date_index'] = episode['date_index']
    minimums = {role: protocol[f'minimum_{role}_rows']
                for role in ('fit', 'calibration', 'validation', 'test')}
    folds = fixed_calendar_splits(rows, protocol['outer_folds_by_date_index_inclusive'],
                                  minimums=minimums)
    paired = []
    receipts = []
    for fold_id, fold in enumerate(folds, start=1):
        selected = {}
        validation_scores = {}
        for name, feature_key in (('b4', 'x_b4'), ('mfsm', 'x_mfsm')):
            scores = []
            for grid_id, params in enumerate(TUNING_GRID):
                model = fit_calibrated(rows, fold['fit'], fold['calibration'],
                                       feature_key=feature_key, params=params)
                predicted = probabilities(model, rows, fold['validation'],
                                          feature_key=feature_key)
                scores.append((_brier(rows, fold['validation'], predicted), grid_id))
            best_score, best_id = min(scores)
            selected[name] = best_id
            validation_scores[name] = best_score
            model = fit_calibrated(rows, fold['fit'], fold['calibration'],
                                   feature_key=feature_key, params=TUNING_GRID[best_id])
            selected[name+'_probabilities'] = probabilities(
                model, rows, fold['test'], feature_key=feature_key)
        for index, b4, mfsm in zip(fold['test'], selected['b4_probabilities'],
                                   selected['mfsm_probabilities']):
            paired.append({'episode_id': rows[index]['episode_id'],
                           'fold': fold_id, 'decision_s': rows[index]['decision_s'],
                           'y': rows[index]['y'], 'b4_probability': b4,
                           'mfsm_probability': mfsm, 'b4_grid_id': selected['b4'],
                           'mfsm_grid_id': selected['mfsm']})
        receipts.append({'fold': fold_id,
                         **{role+'_episode_ids': [rows[i]['episode_id'] for i in fold[role]]
                            for role in ('fit', 'calibration', 'validation', 'test')},
                         'selected_b4_grid_id': selected['b4'],
                         'selected_mfsm_grid_id': selected['mfsm'],
                         'b4_validation_brier': validation_scores['b4'],
                         'mfsm_validation_brier': validation_scores['mfsm']})
    b4_score = sum((p['b4_probability']-p['y'])**2 for p in paired)/len(paired)
    mfsm_score = sum((p['mfsm_probability']-p['y'])**2 for p in paired)/len(paired)
    return {'schema': 'E001-OBS-paired-evaluation-1',
            'data_kind': protocol['data_kind'],
            'shared_features': protocol['shared_features'],
            'mfsm_combinations': protocol['mfsm_combinations'],
            'search_budget': {'b4_candidates': len(TUNING_GRID),
                              'mfsm_candidates': len(TUNING_GRID)},
            'folds': receipts, 'paired_predictions': paired,
            'b4_brier': b4_score, 'mfsm_brier': mfsm_score,
            'paired_brier_improvement': b4_score-mfsm_score,
            'eligible_episodes': len(rows), 'test_episodes': len(paired)}
