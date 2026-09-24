"""Fail-closed E001 execution readiness over hash-verified BTC capture selections."""

from collections import Counter
import hashlib
import json
from pathlib import Path

from .capture_features import CaptureFeatureReplay, feature_rows
from .capture_store import sha256
from .dataset import build_synthetic_fixture
from .qualification import REQUIRED_WS_ROLES
from .replay import CaptureInput


SCHEMA = 'E001-execution-candidate-1'
FEATURE_SCHEMA = 'E001-live-features-receipt-candidate-1'
POLICY = 'E001-receipt-time-candidate-1'
CODE_FILES = (
    'src/mfsm_e001/readiness.py', 'src/mfsm_e001/capture_features.py',
    'src/mfsm_e001/replay.py', 'src/mfsm_e001/timing.py',
    'src/mfsm_e001/data.py', 'src/mfsm_e001/capture_health.py',
    'src/mfsm_e001/collect.py', 'src/mfsm_e001/qualification.py',
    'src/mfsm_e001/dataset.py', 'scripts/build_e001_dataset.py',
    'src/mfsm_e001/validation.py', 'src/mfsm_e001/models.py',
    'src/mfsm_e001/evaluation.py', 'scripts/run_e001_experiment.py',
)


def _path(root, name):
    if not isinstance(name, str) or not name:
        raise ValueError('nonempty input path required')
    path = (root / name).resolve()
    if 'eth' in str(path).lower():
        raise ValueError('ETH holdout is sealed')
    return path


def load_config(path, root):
    """JSON syntax is a YAML 1.2 subset, so this config needs no YAML parser."""
    path = Path(path).resolve()
    config = json.loads(path.read_text())
    if not isinstance(config, dict) or config.get('schema') != SCHEMA:
        raise ValueError('unsupported execution config schema')
    if (config.get('data_kind') != 'real_btc' or
            config.get('timing_candidate') != 'receipt_v1' or
            config.get('timing_policy') != POLICY or
            config.get('feature_schema') != FEATURE_SCHEMA or
            config.get('label_schema') != 'E001-label-v4-candidate' or
            config.get('experiment_version') != 'e001-v1.3-candidate'):
        raise ValueError('execution policy/version mismatch')
    run_config = _path(root, config.get('run_config'))
    if not run_config.is_file():
        raise ValueError('missing scientific run config')
    protocol = _path(root, config.get('evaluation_protocol'))
    if not protocol.is_file() or json.loads(protocol.read_text()).get('schema') != 'E001-btc-evaluation-protocol-candidate-1':
        raise ValueError('missing or unsupported evaluation protocol')
    inputs = config.get('real_inputs')
    if not isinstance(inputs, list) or not inputs:
        raise ValueError('nonempty real_inputs required')
    names = set()
    for item in inputs:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str):
            raise ValueError('named real input required')
        if item['name'] in names:
            raise ValueError('duplicate real input name')
        names.add(item['name'])
        _path(root, item.get('manifest'))
        selected = item.get('decision_seconds')
        if (not isinstance(selected, list) or not selected or
                any(type(s) is not int or s < 0 for s in selected) or
                len(set(selected)) != len(selected)):
            raise ValueError('distinct nonnegative decision seconds required')
        if item.get('sealed_prefix', False) is not True and 'segment_limit' in item:
            raise ValueError('segment limit requires sealed_prefix')
        if 'segment_limit' in item and (type(item['segment_limit']) is not int or item['segment_limit'] < 1):
            raise ValueError('positive integer segment limit required')
    return config, sha256(path), sha256(run_config)


def _block(code, evidence, next_action, *, owner_decision=False):
    return {'code': code, 'evidence': evidence, 'next_action': next_action,
            'owner_decision_required': owner_decision}


def _stage(status, blockers=(), **extra):
    return {'status': status, 'blockers': list(blockers), **extra}


def _capture(root, spec):
    capture = CaptureInput(_path(root, spec['manifest']),
                           sealed_prefix=spec.get('sealed_prefix', False),
                           segment_limit=spec.get('segment_limit'))
    replay = CaptureFeatureReplay(timing_candidate='receipt_v1')
    rows = list(feature_rows(capture.records(), spec['decision_seconds'], replay))
    if any(row['schema'] != FEATURE_SCHEMA for row in rows):
        raise ValueError('feature schema differs from execution config')
    reasons = Counter(reason for row in rows for reason in row['timing_quality']['reasons'])
    state_counts = Counter(row['timing_quality']['state'] for row in rows)
    missing = Counter(field for row in rows for field, value in row['raw'].items()
                      if value is None)
    availability = Counter(field for row in rows for field, value in row['raw'].items()
                           if value is not None)
    return ({'name': spec['name'], 'run_id': capture.manifest['run_id'],
             'manifest': spec['manifest'], 'manifest_sha256': capture.manifest_sha256,
             'capture_status_at_selection': capture.manifest['status'],
             'scope': 'sealed_prefix_only' if capture.partial else 'completed_capture',
             'sealed_segment_count': len(capture.segments),
             'segment_sha256': dict(capture.hashes),
             'decision_seconds': spec['decision_seconds'],
             'decision_rows': len(rows),
             'timing_states': dict(sorted(state_counts.items())),
             'timing_reasons': dict(sorted(reasons.items())),
             'http_probe_count': len(replay.clock_evidence.rows),
             'maximum_source_lead_ns': replay.max_source_lead_ns,
             'primary_eligible_rows': sum(row['primary_eligible'] is True for row in rows),
             'full_panel_rows': sum(row['full_common_feature_panel_complete'] is True for row in rows),
             'depth_scale_rows': sum(row['pretrigger_scales']['depth'] is not None for row in rows),
             'oi_scale_rows': sum(row['pretrigger_scales']['oi'] is not None for row in rows),
             'liquidation_pressure_rows': sum(row['mfsm']['liquidation_pressure_ratio'] is not None for row in rows),
             'raw_missing_rows': dict(sorted(missing.items())),
             'raw_available_rows': dict(sorted(availability.items()))}, rows)


def inspect_real(config, root, *, mode, config_sha256, run_config_sha256):
    """Independent readiness checks continue when the primary timing gate fails."""
    captures = []
    selected_rows = []
    for spec in config['real_inputs']:
        capture, rows = _capture(root, spec)
        captures.append(capture)
        selected_rows.extend(rows)
    count = len(selected_rows)
    eligible = sum(row['primary_eligible'] is True for row in selected_rows)
    reason_counts = Counter()
    for capture in captures:
        reason_counts.update(capture['timing_reasons'])
    timing_blockers = []
    if eligible != count:
        timing_blockers.append(_block(
            'receipt_candidate_unqualified',
            {'ineligible_decision_rows': count-eligible,
             'reasons': dict(sorted(reason_counts.items())),
             'source': 'causal receipt_v1 rows in selected sealed captures'},
            'Implement independent UTC and WebSocket-role delay evidence; rerun qualification on a new capture.'))
    if reason_counts['independent_utc_clock_evidence_missing']:
        timing_blockers.append(_block(
            'independent_utc_evidence_unavailable',
            {'missing_decision_rows': reason_counts['independent_utc_clock_evidence_missing'],
             'source': 'selected raw capture records contain no independent UTC attestation'},
            'Add a validated independent UTC monitor and preserve its causal evidence records in a new capture.'))
    if reason_counts['websocket_role_delay_bound_missing']:
        timing_blockers.append(_block(
            'source_delay_evidence_unavailable',
            {'missing_decision_rows': reason_counts['websocket_role_delay_bound_missing'],
             'unsupported_roles': list(REQUIRED_WS_ROLES),
             'source_review': 'docs/e001_websocket_evidence_review.md'},
            'Resolve the source-age contract with an independently audited provider, or version a narrower observational receipt-time experiment before real fitting.',
            owner_decision=True))
    feature_missing = {
        'pretrigger_depth_scale': count-sum(c['depth_scale_rows'] for c in captures),
        'pretrigger_oi_scale': count-sum(c['oi_scale_rows'] for c in captures),
        'liquidation_pressure_ratio': count-sum(c['liquidation_pressure_rows'] for c in captures),
        'full_common_panel': count-sum(c['full_panel_rows'] for c in captures),
    }
    feature_blockers = []
    if any(feature_missing.values()):
        feature_blockers.append(_block(
            'required_feature_coverage_or_semantics_missing',
            {'missing_decision_rows_by_field': feature_missing,
             'source': 'computed candidate features in selected sealed captures'},
            'Audit complete depth/OI histories and independently support liquidation valuation; resolve the feature contract before fitting.',
            owner_decision=True))
    stages = {
        'capture_integrity': _stage('passed', selected_captures=len(captures),
                                    selected_segments=sum(c['sealed_segment_count'] for c in captures)),
        'timing_qualification': _stage('blocked' if timing_blockers else 'passed', timing_blockers,
                                       eligible_decisions=eligible, selected_decisions=count),
        'feature_feasibility': _stage('blocked' if feature_blockers else 'passed', feature_blockers,
                                      missing_decision_rows_by_field=feature_missing),
        'episode_dataset': _stage('not_run', reason='primary timing/feature contract unresolved'
                                  if timing_blockers or feature_blockers else 'dataset builder not implemented'),
        'btc_evaluation': _stage('not_run', reason='episode dataset unavailable'),
    }
    status = ('BLOCKED_TIMING' if timing_blockers else
              'BLOCKED_FEATURES' if feature_blockers else 'PIPELINE_NOT_IMPLEMENTED')
    return {'schema': 'E001-execution-result-1', 'status': status, 'mode': mode,
            'data_kind': 'real_btc', 'timing_policy': config['timing_policy'],
            'experiment_version': config['experiment_version'],
            'feature_schema': config['feature_schema'], 'label_schema': config['label_schema'],
            'config_sha256': config_sha256, 'run_config_sha256': run_config_sha256,
            'evaluation_protocol_sha256': sha256(_path(root, config['evaluation_protocol'])),
            'code_sha256': {p: sha256(root/p) for p in CODE_FILES},
            'captures': captures, 'stages': stages, 'primary_eligible_rows': eligible,
            'selected_diagnostic_decisions': count, 'model_fitted': False,
            'primary_score': None, 'eth_accessed': False}


def inspect_fixture(config, root, *, config_sha256, run_config_sha256):
    selected = config.get('fixture_inputs')
    if not isinstance(selected, list) or not selected:
        raise ValueError('explicit fixture_inputs required')
    fixtures = []
    datasets = []
    model_evaluations = []
    for item in selected:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str):
            raise ValueError('named fixture required')
        path = _path(root, item.get('path'))
        value = json.loads(path.read_text())
        if value.get('provenance') != 'synthetic_fixture':
            raise ValueError('fixture input lacks explicit synthetic provenance')
        dataset = (build_synthetic_fixture(path)
                   if value.get('schema') == 'E001-synthetic-receipt-grid-1' else None)
        if dataset is not None:
            datasets.append({'name': item['name'], 'episodes': len(dataset['episodes']),
                             'crossings': len(dataset['crossings']),
                             'eligible_fixture_episodes': sum(
                                 e['primary_eligible'] for e in dataset['episodes']),
                             'primary_label_states': [e['primary_label']['state']
                                                      for e in dataset['episodes']]})
        if value.get('schema') == 'E001-synthetic-model-episodes-1':
            from .evaluation import evaluate_synthetic_model_fixture
            model_evaluations.append(evaluate_synthetic_model_fixture(path))
        fixtures.append({'name': item['name'], 'path': item['path'], 'sha256': sha256(path),
                         'events': len(value.get('events', [])),
                         'primary_label_valid': value.get('primary_label', {}).get('valid') is True})
    verified = bool(datasets and model_evaluations)
    return {'schema': 'E001-execution-result-1',
            'status': 'PIPELINE_VERIFIED_SYNTHETIC' if verified else 'PIPELINE_NOT_IMPLEMENTED',
            'mode': 'fixture', 'data_kind': 'synthetic_fixture',
            'timing_policy': config['timing_policy'], 'experiment_version': config['experiment_version'],
            'feature_schema': config['feature_schema'], 'label_schema': config['label_schema'],
            'config_sha256': config_sha256, 'run_config_sha256': run_config_sha256,
            'evaluation_protocol_sha256': sha256(_path(root, config['evaluation_protocol'])),
            'code_sha256': {p: sha256(root/p) for p in CODE_FILES},
            'fixtures': fixtures, 'synthetic_datasets': datasets,
            'synthetic_model_evaluations': model_evaluations,
            'stages': {'fixture_input': _stage('passed'),
                       'episode_dataset': _stage('passed' if datasets else 'not_run',
                                                 **({'synthetic_episode_count': sum(d['episodes'] for d in datasets)}
                                                    if datasets else {'reason': 'no synthetic grid fixture selected'})),
                       'synthetic_model_evaluation': _stage(
                           'passed' if model_evaluations else 'not_run',
                           **({} if model_evaluations else {'reason': 'no synthetic model fixture selected'})),
                       'btc_evaluation': _stage('not_run', reason='real BTC timing/feature/data gates unresolved')},
            'primary_eligible_rows': 0, 'model_fitted': bool(model_evaluations),
            'primary_score': None, 'eth_accessed': False}


def render_report(result):
    lines = ['# Experiment 001 execution result', '',
             f"Status: **{result['status']}**. Mode: `{result['mode']}`. Data: `{result['data_kind']}`.", '',
             f"Policy: `{result['timing_policy']}`. Model fitted: `{str(result['model_fitted']).lower()}`."
             ]
    if result['status'] == 'ERROR':
        lines.extend(['', f"Execution error: `{result['error_type']}`: {result['error_message']}"])
    if result.get('captures'):
        lines.extend(['', '## Selected BTC captures', ''])
        for capture in result['captures']:
            lines.append(f"- `{capture['name']}`: {capture['decision_rows']} diagnostic decisions, "
                         f"{capture['primary_eligible_rows']} eligible; {capture['sealed_segment_count']} sealed segments; "
                         f"timing states {capture['timing_states']}.")
    if result.get('synthetic_datasets'):
        lines.extend(['', '## Synthetic dataset checks', ''])
        for dataset in result['synthetic_datasets']:
            lines.append(f"- `{dataset['name']}`: {dataset['crossings']} crossings, "
                         f"{dataset['episodes']} episodes, {dataset['eligible_fixture_episodes']} "
                         f"software-eligible rows; labels {dataset['primary_label_states']}.")
    if result.get('synthetic_model_evaluations'):
        lines.extend(['', '## Synthetic model checks', ''])
        for evaluation in result['synthetic_model_evaluations']:
            lines.append(f"- {len(evaluation['paired_predictions'])} invented out-of-sample pairs; "
                         f"paired Brier difference {evaluation['paired_brier_improvement']:.6g}. "
                         'This is a software check, not a BTC research score.')
    lines.extend(['', '## Stage outcomes', ''])
    for name, stage in result['stages'].items():
        lines.append(f"- **{name}**: {stage['status']}"
                     + (f" — {stage['reason']}" if 'reason' in stage else ''))
        for blocker in stage['blockers']:
            lines.append(f"  - `{blocker['code']}`: {blocker['next_action']} Evidence: {blocker['evidence']}.")
    lines.extend(['', 'See `result.json` for exact manifest, segment, config and code hashes.', ''])
    return '\n'.join(lines)
