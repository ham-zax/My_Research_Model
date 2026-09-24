from decimal import Decimal

from mfsm_e001.capacity_audit import (
    audit_capacity_event,
    read_capacity_trades,
    reconstruct_book_inputs,
    summarize_capacity_audit,
)


D = Decimal
NS = 1_000_000_000


def state(second, *, depth='1000', mid='100', spread='1', epoch=1):
    return {'second': second, 'depth_bid': D(depth), 'midpoint': D(mid),
            'spread_bps': D(spread), 'book_epoch': epoch, 'valid': True,
            'top_valid': True, 'bid_covered': True, 'ask_covered': True}


def observation(second, *, changes=(), reset=False, epoch=1):
    return {'event_ns': second*NS, 'available_ns': second*NS,
            'reset': reset, 'valid': True, 'mid': D('100'),
            'bid_covered': True, 'ask_covered': True,
            'bid_changes_known': True, 'ask_changes_known': True,
            'changes': [('bid', D(str(price)), D(str(size)))
                        for price, size in changes], 'book_epoch': epoch}


def complete_inputs(trigger=1800):
    decision = trigger+15
    states = {second: state(second) for second in range(trigger-1800, decision+31)}
    observations = [observation(decision-16), observation(decision-15),
                    observation(decision-10, changes=((100, 2),)),
                    observation(decision-9), observation(decision-5), observation(decision)]
    return decision, states, observations


def test_capacity_audit_uses_only_predecision_book_for_capacity():
    decision, states, observations = complete_inputs()
    trades = [{'received_us': (decision-10)*1_000_000, 'side': 'sell',
               'notional': D('50')},
              {'received_us': (decision+10)*1_000_000, 'side': 'sell',
               'notional': D('400')}]
    result = audit_capacity_event(states, observations, trades, trigger_s=1800)
    assert result['valid'] is True
    assert result['pre_depth_median'] == D('1000')
    assert result['replenishment_rate_15s'] == D('200')/15
    assert result['capacity_proxy'] == D('1400')
    assert result['predecision_sell_notional_30s'] == D('50')
    assert result['future_sell_notional_30s'] == D('400')
    future = observation(decision+5, changes=((100, -2),))
    assert audit_capacity_event(states, observations+[future], trades,
                                trigger_s=1800)['capacity_proxy'] == D('1400')


def test_capacity_audit_measures_sell_flow_before_first_25bps_breach():
    decision, states, observations = complete_inputs()
    states[decision+5] = state(decision+5, mid='99.8', depth='800')
    states[decision+10] = state(decision+10, mid='99.7', depth='600')
    for second in range(decision+11, decision+31):
        states[second] = state(second, mid='99.7', depth='600')
    trades = [
        {'received_us': (decision+4)*1_000_000, 'side': 'sell', 'notional': D('100')},
        {'received_us': (decision+10)*1_000_000, 'side': 'sell', 'notional': D('200')},
        {'received_us': (decision+12)*1_000_000, 'side': 'buy', 'notional': D('900')},
    ]
    result = audit_capacity_event(states, observations, trades, trigger_s=1800)
    assert result['first_25bps_breach_seconds'] == 10
    assert result['sell_notional_before_25bps_breach'] == D('300')
    assert result['future_sell_notional_30s'] == D('300')
    assert result['depth_ratio_30s'] == D('0.6')
    assert result['mid_return_bps_30s'] == D('-30')


def test_capacity_audit_rejects_missing_history_and_epoch_reset():
    decision, states, observations = complete_inputs()
    del states[100]
    result = audit_capacity_event(states, observations, [], trigger_s=1800)
    assert result == {'valid': False, 'reason': 'missing_pretrigger_book_state'}
    _, states, observations = complete_inputs()
    states[100]['book_epoch'] = 2
    result = audit_capacity_event(states, observations, [], trigger_s=1800)
    assert result == {'valid': False, 'reason': 'book_reset_inside_required_window'}


def test_capacity_audit_requires_bid_band_but_not_full_ask_band():
    _, states, observations = complete_inputs()
    states[100].update(valid=False, ask_covered=False)
    assert audit_capacity_event(states, observations, [], trigger_s=1800)['valid'] is True
    states[100].update(bid_covered=False)
    assert audit_capacity_event(states, observations, [], trigger_s=1800) == {
        'valid': False, 'reason': 'incomplete_pretrigger_bid_band'}


def test_tardis_l2_reconstruction_groups_snapshot_and_tracks_resets(tmp_path):
    import gzip

    path = tmp_path/'bybit_incremental_book_L2_2025-03-01_BTCUSDT.csv.gz'
    header = 'exchange,symbol,timestamp,local_timestamp,is_snapshot,side,price,amount\n'
    rows = [
        'bybit,BTCUSDT,100000,100000,true,bid,100,1\n',
        'bybit,BTCUSDT,100000,100000,true,bid,99.7,1\n',
        'bybit,BTCUSDT,100000,100000,true,ask,100.1,1\n',
        'bybit,BTCUSDT,100000,100000,true,ask,100.4,1\n',
        'bybit,BTCUSDT,500000,500000,false,bid,100,2\n',
        'bybit,BTCUSDT,1500000,1500000,true,bid,100,3\n',
        'bybit,BTCUSDT,1500000,1500000,true,bid,99.7,1\n',
        'bybit,BTCUSDT,1500000,1500000,true,ask,100.1,1\n',
        'bybit,BTCUSDT,1500000,1500000,true,ask,100.4,1\n',
    ]
    with gzip.open(path, 'wt') as stream:
        stream.write(header+''.join(rows))
    states, observations, diagnostics = reconstruct_book_inputs(
        path, target_seconds={1, 2}, observation_ranges=[(0, 2)])
    assert states[1]['valid'] is True
    assert states[1]['depth_bid'] == D('200')
    assert states[1]['book_epoch'] == 1
    assert states[2]['depth_bid'] == D('300')
    assert states[2]['book_epoch'] == 2
    assert [row['reset'] for row in observations] == [True, False, True]
    assert observations[1]['changes'] == [('bid', D('100'), D('1'))]
    assert diagnostics == {'snapshot_cohorts': 2, 'delta_cohorts': 1,
                           'invalid_cohorts': 0}


def test_tardis_reconstruction_supports_separate_shallow_band(tmp_path):
    import gzip

    path = tmp_path/'bybit_incremental_book_L2_2025-03-01_BTCUSDT.csv.gz'
    header = 'exchange,symbol,timestamp,local_timestamp,is_snapshot,side,price,amount\n'
    rows = [
        'bybit,BTCUSDT,100000,100000,true,bid,100,1\n',
        'bybit,BTCUSDT,100000,100000,true,bid,99.99,1\n',
        'bybit,BTCUSDT,100000,100000,true,ask,100.01,1\n',
        'bybit,BTCUSDT,100000,100000,true,ask,100.02,1\n',
    ]
    with gzip.open(path, 'wt') as stream:
        stream.write(header+''.join(rows))
    deep, _, _ = reconstruct_book_inputs(
        path, target_seconds={1}, observation_ranges=[], band_bps=D('25'))
    shallow, _, _ = reconstruct_book_inputs(
        path, target_seconds={1}, observation_ranges=[], band_bps=D('0.5'))
    assert deep[1]['bid_covered'] is False
    assert shallow[1]['bid_covered'] is True
    assert shallow[1]['depth_bid'] == D('100')


def test_tardis_trade_reader_uses_receipt_time_and_requested_windows(tmp_path):
    import gzip

    path = tmp_path/'bybit_trades_2025-03-01_BTCUSDT.csv.gz'
    header = 'exchange,symbol,timestamp,local_timestamp,id,side,price,amount\n'
    rows = [
        'bybit,BTCUSDT,10000,900000,a,sell,100,2\n',
        'bybit,BTCUSDT,20000,1000000,b,sell,101,3\n',
        'bybit,BTCUSDT,30000,1500000,c,buy,102,4\n',
        'bybit,BTCUSDT,40000,2000000,d,sell,103,5\n',
        'bybit,BTCUSDT,50000,2100000,e,sell,104,6\n',
    ]
    with gzip.open(path, 'wt') as stream:
        stream.write(header+''.join(rows))
    trades, diagnostics = read_capacity_trades(path, windows=[(1, 2)])
    assert trades == [
        {'received_us': 1_500_000, 'side': 'buy', 'notional': D('408')},
        {'received_us': 2_000_000, 'side': 'sell', 'notional': D('515')},
    ]
    assert diagnostics == {'rows_read': 4, 'selected_trades': 2,
                           'invalid_rows': 0}


def test_capacity_summary_separates_independent_events_and_censoring():
    rows = [
        {'valid': True, 'accepted': True, 'capacity_proxy': D('100'),
         'future_sell_notional_30s': D('120'),
         'sell_notional_before_25bps_breach': D('120'),
         'first_25bps_breach_seconds': None, 'depth_ratio_30s': D('1.1'),
         'mid_return_bps_30s': D('2')},
        {'valid': True, 'accepted': False, 'capacity_proxy': D('200'),
         'future_sell_notional_30s': D('100'),
         'sell_notional_before_25bps_breach': D('80'),
         'first_25bps_breach_seconds': 20, 'depth_ratio_30s': D('0.7'),
         'mid_return_bps_30s': D('-30')},
        {'valid': False, 'accepted': True, 'reason': 'missing'},
    ]
    summary = summarize_capacity_audit(rows, minimum_independent=5)
    assert summary['crossings'] == 3
    assert summary['valid_crossings'] == 2
    assert summary['valid_independent_episodes'] == 1
    assert summary['right_censored_crossings'] == 1
    assert summary['capacity_under_observed_no_breach_crossings'] == 1
    assert summary['exclusion_counts'] == {'missing': 1}
    assert summary['rank_correlations'] == {
        'status': 'not_computed',
        'reason': '1 valid independent episodes; minimum is 5',
    }


def test_capacity_summary_uses_history_qualification_when_present():
    common = {'valid': True, 'capacity_proxy': D('100'),
              'future_sell_notional_30s': D('80'),
              'sell_notional_before_25bps_breach': D('80'),
              'first_25bps_breach_seconds': None,
              'depth_ratio_30s': D('1'), 'mid_return_bps_30s': D('0')}
    rows = [
        {**common, 'accepted': True, 'history_qualified': True},
        {**common, 'accepted': True, 'history_qualified': False},
    ]
    summary = summarize_capacity_audit(rows, minimum_independent=5)
    assert summary['valid_crossings'] == 2
    assert summary['valid_independent_episodes'] == 1
