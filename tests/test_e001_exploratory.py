"""Exploratory hourly labels and calendar folds remain causal and disjoint."""

import pytest

from mfsm_e001.exploratory import (
    _ticker_at, _trade_windows, evaluate_exploratory, fixed_calendar_splits,
    hourly_label, validate_protocol,
)


def test_hourly_label_starts_after_decision_and_respects_gap_before_hit():
    prices = [100.0]*1901
    prices[1] = 98.0
    label = hourly_label(prices, 0, 1800, -0.005, 0.00375)
    assert label['valid'] and label['value'] == 1 and label['first_hit_offset'] == 1
    prices[1] = None
    assert hourly_label(prices, 0, 1800, -0.005, 0.00375)['reason'] == 'missing_price_before_hit'
    prices[1] = 100.0
    prices[2] = 101.0
    label = hourly_label(prices, 0, 1800, -0.005, 0.00375)
    assert label['valid'] and label['value'] == 0 and label['state'] == 'recovery-first'


def test_fixed_calendar_folds_have_past_matured_labels_only():
    rows = []
    for day in range(19):
        for hour in range(2, 23):
            second = day*86400+hour*3600
            rows.append({'episode_id': f'{day}-{hour}', 'date_index': day,
                         'decision_s': second, 'maturity_ms': (second+1800)*1000,
                         'y': hour % 2})
    folds = fixed_calendar_splits(rows, [
        {'fit': [0, 6], 'calibration': [7, 9], 'validation': [10, 11], 'test': [12, 14]},
        {'fit': [0, 9], 'calibration': [10, 12], 'validation': [13, 14], 'test': [15, 18]}],
        minimums={'fit': 50, 'calibration': 20, 'validation': 20, 'test': 20})
    assert len(folds) == 2
    assert len(folds[0]['test']) == 63 and len(folds[1]['test']) == 84
    assert not set(folds[0]['test']) & set(folds[1]['test'])
    bad = [dict(row) for row in rows]
    bad[0]['maturity_ms'] = 10**15
    with pytest.raises(ValueError, match='immature'):
        fixed_calendar_splits(bad, [
            {'fit': [0, 6], 'calibration': [7, 9], 'validation': [10, 11], 'test': [12, 14]}],
            minimums={'fit': 50, 'calibration': 20, 'validation': 20, 'test': 20})


def test_exploratory_model_scores_only_predeclared_disjoint_test_days():
    import json
    from pathlib import Path

    protocol = json.loads((Path(__file__).parents[1]/'experiments'/
                           'e001_observational_exploratory_protocol.yaml').read_text())
    episodes = []
    for day in range(19):
        for hour in range(2, 23):
            decision = day*86400+hour*3600
            shared = {name: (day % 3 + hour % 4)/10 for name in protocol['shared_features']}
            episodes.append({'episode_id': f'fixture-{day:02d}-{hour:02d}',
                             'date_index': day, 'decision_s': decision,
                             'primary_eligible': True,
                             'primary_label': {'valid': True, 'value': hour % 2,
                                               'training_maturity_ms': (decision+1800)*1000},
                             'shared': shared,
                             'mfsm': {**shared, 'sell_pressure_x_spread': (day+hour)/100}})
    result = evaluate_exploratory(episodes, protocol)
    assert result['data_kind'] == 'exploratory_tardis_btc'
    assert len(result['paired_predictions']) == 147
    assert {p['episode_id'] for p in result['paired_predictions']} == {
        e['episode_id'] for e in episodes if e['date_index'] >= 12}
    assert result['b4_brier'] >= 0 and result['mfsm_brier'] >= 0
    for fold in result['folds']:
        assert not set(fold['test_episode_ids']) & set(fold['fit_episode_ids'])
        assert not set(fold['test_episode_ids']) & set(fold['validation_episode_ids'])
    episodes[0]['mfsm']['spot_return_300s'] = 9
    with pytest.raises(ValueError, match='shared feature mismatch'):
        evaluate_exploratory(episodes, protocol)


def test_receipt_trade_window_excludes_future_and_rejects_unknown_side(tmp_path):
    import gzip

    path = tmp_path/'bybit_trades_2025-03-01_BTCUSDT.csv.gz'
    header = 'exchange,symbol,local_timestamp,side,price,amount\n'
    body = ''.join(f'bybit,BTCUSDT,{stamp},{side},100,1\n' for stamp, side in [
        (500_000, 'sell'), (600_000, 'sell'), (1_000_000, 'buy'),
        (1_500_000, 'sell'), (1_600_000, 'sell'), (2_100_000, 'sell')])
    with gzip.open(path, 'wt') as stream:
        stream.write(header+body)
    counts, sells = _trade_windows(path, [1_000_000, 2_000_000], 500_000)
    assert counts == [2, 1]
    assert sells == [100, 100]
    assert _ticker_at([800_000, 1_100_000], [(1., 2., 2.), (2., 2., 2.)],
                      1_000_000, 300_000) == (1., 2., 2.)
    assert _ticker_at([800_000, 1_100_000], [(1., 2., 2.), (2., 2., 2.)],
                      1_000_000, 100_000) is None
    with gzip.open(path, 'wt') as stream:
        stream.write(header+body.replace(',buy,', ',unknown,'))
    with pytest.raises(ValueError, match='invalid trade side'):
        _trade_windows(path, [1_000_000, 2_000_000], 500_000)


def test_unimplemented_protocol_change_is_rejected():
    import json
    from pathlib import Path

    protocol = json.loads((Path(__file__).parents[1]/'experiments'/
                           'e001_observational_exploratory_protocol.yaml').read_text())
    protocol['label_lower_barrier'] = -0.01
    with pytest.raises(ValueError, match='label_lower_barrier'):
        validate_protocol(protocol)
