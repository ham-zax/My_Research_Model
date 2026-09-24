"""Candidate matched walk-forward B4/MFSM software evaluation."""

import json
from pathlib import Path

from .capture_store import sha256
from .models import TUNING_GRID, fit_calibrated, probabilities
from .validation import prepare_rows, walk_forward_splits


def _brier(rows, indices, predicted):
    return sum((p-rows[i]['y'])**2 for i, p in zip(indices, predicted))/len(indices)


def evaluate_walk_forward(episodes, *, shared_features, mfsm_combinations, data_kind):
    """Evaluate identical eligible episodes; caller controls real-data gates."""
    if data_kind not in ('synthetic_fixture', 'real_btc'):
        raise ValueError('unknown data provenance')
    if data_kind == 'real_btc':
        raise ValueError('real BTC fitting disabled until measurement and feature contracts freeze')
    rows = prepare_rows(episodes, shared_features, mfsm_combinations)
    folds = walk_forward_splits(rows)
    paired = []
    fit_receipts = []
    for fold_id, fold in enumerate(folds, start=1):
        selected = {}
        for name, key in (('b4', 'x_b4'), ('mfsm', 'x_mfsm')):
            scored = []
            for grid_id, params in enumerate(TUNING_GRID):
                model = fit_calibrated(rows, fold['fit'], fold['calibration'],
                                       feature_key=key, params=params)
                predicted = probabilities(model, rows, fold['validation'], feature_key=key)
                scored.append((_brier(rows, fold['validation'], predicted), grid_id))
            _, best_id = min(scored)  # Grid order is the deterministic tie break.
            selected[name] = best_id
            model = fit_calibrated(rows, fold['fit'], fold['calibration'],
                                   feature_key=key, params=TUNING_GRID[best_id])
            selected[name+'_probabilities'] = probabilities(model, rows, fold['test'],
                                                              feature_key=key)
        for index, b4, mfsm in zip(fold['test'], selected['b4_probabilities'],
                                   selected['mfsm_probabilities']):
            paired.append({'episode_id': rows[index]['episode_id'],
                           'fold': fold_id, 'decision_s': rows[index]['decision_s'],
                           'y': rows[index]['y'], 'b4_probability': b4,
                           'mfsm_probability': mfsm,
                           'b4_grid_id': selected['b4'], 'mfsm_grid_id': selected['mfsm']})
        fit_receipts.append({'fold': fold_id,
                             'fit_episode_ids': [rows[i]['episode_id'] for i in fold['fit']],
                             'calibration_episode_ids': [rows[i]['episode_id'] for i in fold['calibration']],
                             'validation_episode_ids': [rows[i]['episode_id'] for i in fold['validation']],
                             'test_episode_ids': [rows[i]['episode_id'] for i in fold['test']],
                             'selected_b4_grid_id': selected['b4'],
                             'selected_mfsm_grid_id': selected['mfsm']})
    b4_score = sum((p['b4_probability']-p['y'])**2 for p in paired)/len(paired)
    mfsm_score = sum((p['mfsm_probability']-p['y'])**2 for p in paired)/len(paired)
    return {'schema': 'E001-paired-evaluation-candidate-1', 'data_kind': data_kind,
            'shared_features': list(shared_features),
            'mfsm_combinations': list(mfsm_combinations),
            'search_budget': {'b4_candidates': len(TUNING_GRID),
                              'mfsm_candidates': len(TUNING_GRID)},
            'folds': fit_receipts, 'paired_predictions': paired,
            'b4_brier': b4_score, 'mfsm_brier': mfsm_score,
            'paired_brier_improvement': b4_score-mfsm_score,
            'unscored_tail_episodes': len(rows)-max(fold['test'][-1] for fold in folds)-1}


def evaluate_synthetic_model_fixture(path):
    """Generate only the declared deterministic invented training fixture."""
    path = Path(path)
    spec = json.loads(path.read_text())
    if (spec.get('schema') != 'E001-synthetic-model-episodes-1' or
            spec.get('provenance') != 'synthetic_fixture' or
            spec.get('label_rule') != 'alternating_binary_by_index' or
            spec.get('feature_rule') != 'modular_numeric_by_index' or
            spec.get('episode_count') != 130 or spec.get('spacing_seconds') != 7200):
        raise ValueError('unsupported synthetic model fixture')
    episodes = []
    for index in range(spec['episode_count']):
        decision = index*spec['spacing_seconds']
        shared = {'depth_relative': str(1+(index % 7)/10)}
        episodes.append({'episode_id': f'invented-{index:03}',
                         'decision_s': decision, 'primary_eligible': True,
                         'shared': shared,
                         'mfsm': {**shared, 'interaction': str((index % 11)/10)},
                         'primary_label': {'valid': True, 'value': index % 2,
                                           'training_maturity_ms': (decision+1800)*1000}})
    result = evaluate_walk_forward(
        episodes, shared_features=spec['shared_features'],
        mfsm_combinations=spec['mfsm_combinations'], data_kind='synthetic_fixture')
    result['source_sha256'] = sha256(path)
    return result
