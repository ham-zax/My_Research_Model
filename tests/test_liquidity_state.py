"""Behavioral checks for the separate observable top-level liquidity feature."""

from decimal import Decimal

from mfsm_e001.liquidity_state import (
    decision_liquidity_state,
    persistent_top_bid_add_rate,
    top_level_book,
)
from mfsm_e001.capacity_audit import reconstruct_book_inputs


D = Decimal
NS = 1_000_000_000


def book(second, *, epoch=1, bid='1000', ask='1000', valid=True):
    return {'second': second, 'book_epoch': epoch, 'top_valid': valid,
            'top_level_valid': valid, 'top_bid_notional': D(bid),
            'top_ask_notional': D(ask), 'spread_bps': D('2'),
            'midpoint': D('100')}


def observation(second, *, bid_prices=('99.99',), changes=(),
                reset=False, known=True, valid=True):
    return {'event_ns': second*NS, 'available_ns': second*NS,
            'book_epoch': 1, 'reset': reset, 'top_level_valid': valid,
            'bid_changes_known': known,
            'top_bid_prices': tuple(D(price) for price in bid_prices),
            'changes': [('bid', D(price), D(amount)) for price, amount in changes]}


def complete_inputs(trigger=1800):
    decision = trigger+15
    states = {second: book(second) for second in range(trigger-1800, decision+1)}
    observations = [observation(decision-16), observation(decision-15),
                    observation(decision-10, changes=(('99.99', '2'),)),
                    observation(decision-9), observation(decision-5),
                    observation(decision)]
    trades = [
        {'received_us': (decision-5)*1_000_000, 'side': 'sell', 'notional': D('400')},
        {'received_us': (decision-2)*1_000_000, 'side': 'buy', 'notional': D('100')},
        {'received_us': (decision+1)*1_000_000, 'side': 'sell', 'notional': D('900')},
    ]
    return decision, states, observations, trades


def test_top_level_depth_remains_defined_when_midpoint_band_is_empty():
    bids = {D('99.90'): D('2'), D('99.80'): D('3')}
    asks = {D('100.10'): D('4'), D('100.20'): D('5')}
    view = top_level_book(bids, asks, levels=2, epoch=1,
                          last_us=500_000, boundary_us=1_000_000)
    assert view['top_level_valid'] is True
    assert view['top_bid_notional'] == D('499.20')
    assert view['top_ask_notional'] == D('901.40')
    assert view['spread_bps'] == D('20')
    assert top_level_book(bids, asks, levels=3, epoch=1,
                          last_us=500_000, boundary_us=1_000_000)['reason'] == (
                              'insufficient_book_levels')


def test_persistent_top_bid_additions_require_dwell_and_endpoint_membership():
    observations = [observation(0), observation(1, changes=(('99.99', '3'),)),
                    observation(2, changes=(('99.99', '-1'),)),
                    observation(4, changes=(('99.99', '4'),)),
                    observation(5, bid_prices=())]
    result = persistent_top_bid_add_rate(observations, boundary_ns=5*NS,
                                         window_seconds=5)
    assert result['valid'] is True
    assert result['persistent_bid_add_rate'] == D('99.99')*2/5
    assert result['gross_bid_add_rate'] == D('99.99')*7/5


def test_persistent_top_bid_additions_reject_reset_and_unknown_changes():
    rows = [observation(0), observation(1, changes=(('99.99', '2'),)),
            observation(2, reset=True), observation(5)]
    assert persistent_top_bid_add_rate(rows, boundary_ns=5*NS,
                                       window_seconds=5)['reason'] == 'book_reset_in_window'
    rows[2] = observation(2, known=False)
    assert persistent_top_bid_add_rate(rows, boundary_ns=5*NS,
                                       window_seconds=5)['reason'] == 'unknown_bid_change'


def test_decision_feature_uses_only_past_book_and_trade_flow():
    decision, states, observations, trades = complete_inputs()
    result = decision_liquidity_state(states, observations, trades, trigger_s=1800,
                                      levels=50)
    assert result['valid'] is True
    assert result['top_bid_relative'] == D('1')
    assert result['top_ask_relative'] == D('1')
    assert result['imbalance'] == D('0')
    assert result['persistent_bid_add_rate_15s'] == D('199.98')/15
    assert result['sell_notional_30s'] == D('400')
    assert result['buy_notional_30s'] == D('100')
    assert result['net_buy_notional_30s'] == D('-300')
    assert result['gross_trade_notional_30s'] == D('500')
    later = observation(decision+1, changes=(('99.99', '-2'),))
    assert decision_liquidity_state(states, observations+[later], trades,
                                    trigger_s=1800, levels=50) == result


def test_decision_feature_rejects_long_history_gap_and_epoch_change():
    decision, states, observations, trades = complete_inputs()
    for second in range(100, 107):
        states[second]['top_level_valid'] = False
    assert decision_liquidity_state(states, observations, trades,
                                    trigger_s=1800, levels=50)['reason'] == (
                                        'pretrigger_book_gap_exceeds_5s')
    decision, states, observations, trades = complete_inputs()
    states[100]['book_epoch'] = 2
    assert decision_liquidity_state(states, observations, trades,
                                    trigger_s=1800, levels=50)['reason'] == (
                                        'book_epoch_changed_in_history')


def test_reconstruction_exposes_top_levels_when_25bps_band_is_missing(tmp_path):
    import gzip

    path = tmp_path/'bybit_incremental_book_L2_2025-03-01_BTCUSDT.csv.gz'
    rows = [
        'bybit,BTCUSDT,100000,100000,true,bid,100,1\n',
        'bybit,BTCUSDT,100000,100000,true,bid,99.99,2\n',
        'bybit,BTCUSDT,100000,100000,true,ask,100.01,3\n',
        'bybit,BTCUSDT,100000,100000,true,ask,100.02,4\n',
        'bybit,BTCUSDT,500000,500000,false,bid,100,2\n',
    ]
    with gzip.open(path, 'wt') as stream:
        stream.write('exchange,symbol,timestamp,local_timestamp,is_snapshot,side,price,amount\n')
        stream.writelines(rows)
    states, observations, _ = reconstruct_book_inputs(
        path, target_seconds={1}, observation_ranges=[(0, 1)],
        band_bps=D('25'), top_levels=2)
    assert states[1]['bid_covered'] is False
    assert states[1]['top_level_valid'] is True
    assert states[1]['top_bid_notional'] == D('399.98')
    assert observations[-1]['top_bid_prices'] == (D('100'), D('99.99'))
    assert observations[-1]['changes'] == [('bid', D('100'), D('1'))]
