"""One receipt grid supplies event selection, features and labels."""

from decimal import Decimal

import pytest

from mfsm_e001.dataset import build_episode_dataset


POLICY = 'E001-receipt-time-candidate-1'


def fixture_rows():
    rows = []
    changes = {7500: '98.9', 7510: '100', 7520: '98.9', 8000: '100',
               15000: '98.9', 15016: '100', 31000: '98.9', 43000: '98.9'}
    price = Decimal('100')
    for start, end, epoch in ((0, 17000, 0), (23000, 33000, 1),
                              (35000, 45000, 2)):
        price = Decimal('100')
        for second in range(start, end + 1):
            price = Decimal(changes.get(second, price))
            rows.append({'second': second, 'composite_price': None if second == 32000 else price,
                         'timing_policy': POLICY, 'clock_epoch': epoch,
                         'latest_received_ns': second * 1_000_000_000})
    return rows


def features():
    return [{'decision_second': second, 'timing_policy': POLICY,
             'timing_quality': {'clock_epoch': epoch, 'state': 'qualified'},
             'primary_eligible': True, 'shared': {'depth_relative': Decimal('1')},
             'mfsm': {'depth_relative': Decimal('1'), 'interaction': Decimal('0.2')}}
            for second, epoch in ((7515, 0), (15015, 0), (31015, 1), (43015, 2))]


def build(rows=None, feature_rows=None, as_of=40_000_000):
    return build_episode_dataset(
        rows or fixture_rows(), features() if feature_rows is None else feature_rows,
        asset='BTC', experiment_version='e001-v1.3-candidate', timing_policy=POLICY,
        label_schema='E001-label-v4-candidate', source_sha256='a'*64,
        training_as_of_ms=as_of, synthetic_fixture=True)


def test_fixture_has_two_barrier_directions_lockout_and_gap():
    dataset = build()
    assert dataset['data_kind'] == 'synthetic_fixture'
    assert [(x['trigger_s'], x['status']) for x in dataset['crossings']] == [
        (7500, 'accepted_with_observed_lockout'), (7520, 'locked_out'),
        (7810, 'locked_out'),
        (15000, 'accepted_with_observed_lockout'),
        (31000, 'accepted_with_observed_lockout'),
        (43000, 'accepted_with_observed_lockout')]
    episodes = dataset['episodes']
    assert len(episodes) == 4 and len({e['episode_id'] for e in episodes}) == 4
    assert [e['primary_label']['state'] for e in episodes] == [
        'downside-first', 'recovery-first', None, 'neither-by-horizon']
    assert episodes[2]['primary_label']['reason'] == 'missing_price_before_hit'
    assert episodes[0]['primary_label']['first_hit_s'] == 7520
    assert episodes[0]['primary_label']['training_maturity_ms'] == 9315_000
    assert episodes[0]['shared'] == {'depth_relative': '1'}
    assert episodes[0]['mfsm']['depth_relative'] == episodes[0]['shared']['depth_relative']


def test_early_hit_cannot_train_before_full_horizon_and_future_is_causal():
    rows = fixture_rows()
    early = build(rows, as_of=7520_000)
    assert early['episodes'][0]['primary_label']['valid'] is True
    assert early['episodes'][0]['primary_label']['training_ready'] is False
    rows[-1]['composite_price'] = Decimal('200')
    changed = build(rows, as_of=7520_000)
    assert changed['episodes'][0] == early['episodes'][0]


def test_policy_or_epoch_mismatch_rejected_before_join():
    feature_rows = features()
    feature_rows[0]['timing_policy'] = 'legacy_source_time'
    with pytest.raises(ValueError, match='policy mismatch'):
        build(feature_rows=feature_rows)
    feature_rows = features()
    feature_rows[0]['timing_quality']['clock_epoch'] = 1
    with pytest.raises(ValueError, match='epoch mismatch'):
        build(feature_rows=feature_rows)


def test_decision_feature_must_be_available_and_timing_qualified():
    future = features()
    future[0]['latest_input_available_ns'] = (7515*1_000_000_000)+1
    with pytest.raises(ValueError, match='feature arrived after decision'):
        build(feature_rows=future)
    unqualified = features()
    unqualified[0]['timing_quality']['state'] = 'unknown'
    result = build(feature_rows=unqualified)
    assert result['episodes'][0]['primary_eligible'] is False
    assert any('decision_timing_unqualified' in item['reason']
               for item in result['exclusions'])
