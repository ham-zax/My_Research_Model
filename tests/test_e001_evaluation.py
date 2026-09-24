"""Matched B4/MFSM software checks on invented episodes only."""

import pytest

from mfsm_e001.evaluation import evaluate_walk_forward
from mfsm_e001.validation import prepare_rows, walk_forward_splits


def invented_episodes(n=130):
    rows = []
    for index in range(n):
        decision = index * 7200
        shared = {'depth_relative': str(1 + (index % 7)/10)}
        rows.append({'episode_id': f'synthetic-{index:03}',
                     'decision_s': decision, 'primary_eligible': True,
                     'shared': shared,
                     'mfsm': {**shared, 'interaction': str((index % 11)/10)},
                     'primary_label': {'valid': True, 'value': index % 2,
                                       'training_maturity_ms': (decision+1800)*1000}})
    return rows


def test_walk_forward_obeys_maturity_and_disjoint_periods():
    rows = prepare_rows(invented_episodes(), ['depth_relative'], ['interaction'])
    folds = walk_forward_splits(rows)
    assert len(folds) == 2
    for fold in folds:
        assert set(fold['fit']).isdisjoint(
            fold['calibration']+fold['validation']+fold['test'])
        assert max(fold['fit']) < min(fold['calibration']) < min(fold['validation']) < min(fold['test'])
        test_start = rows[fold['test'][0]]['decision_s']*1000
        assert all(rows[index]['maturity_ms'] <= test_start for index in
                   fold['fit']+fold['calibration']+fold['validation'])
    bad = invented_episodes()
    bad[0]['primary_label']['training_maturity_ms'] = 10**12
    with pytest.raises(ValueError, match='immature'):
        walk_forward_splits(prepare_rows(bad, ['depth_relative'], ['interaction']))


def test_matched_models_are_deterministic_and_same_episode_rows():
    rows = invented_episodes()
    first = evaluate_walk_forward(rows, shared_features=['depth_relative'],
                                  mfsm_combinations=['interaction'], data_kind='synthetic_fixture')
    second = evaluate_walk_forward(rows, shared_features=['depth_relative'],
                                   mfsm_combinations=['interaction'], data_kind='synthetic_fixture')
    assert first == second
    assert len(first['paired_predictions']) == 40
    assert len({p['episode_id'] for p in first['paired_predictions']}) == 40
    assert all(0 <= p['b4_probability'] <= 1 and 0 <= p['mfsm_probability'] <= 1
               for p in first['paired_predictions'])
    assert first['data_kind'] == 'synthetic_fixture'
    assert first['search_budget'] == {'b4_candidates': 2, 'mfsm_candidates': 2}


def test_pair_matrix_rejects_missing_or_mismatched_shared_inputs():
    bad = invented_episodes()
    bad[2]['mfsm']['depth_relative'] = '9'
    with pytest.raises(ValueError, match='shared feature mismatch'):
        prepare_rows(bad, ['depth_relative'], ['interaction'])
    bad = invented_episodes()
    bad[2]['mfsm']['interaction'] = None
    with pytest.raises(ValueError, match='missing required feature'):
        prepare_rows(bad, ['depth_relative'], ['interaction'])


def test_real_fit_is_disabled_until_feature_and_measurement_contract_freeze():
    with pytest.raises(ValueError, match='real BTC fitting disabled'):
        evaluate_walk_forward(invented_episodes(),
                              shared_features=['depth_relative'],
                              mfsm_combinations=['interaction'], data_kind='real_btc')
