"""Real capture inputs cannot become model results by changing execution mode."""

import importlib
import json
from pathlib import Path

import pytest

from mfsm_e001.capture_store import CaptureStore, atomic_json, sha256
from mfsm_e001.replay import NS


def execution_config(tmp_path, *, manifest):
    config = {'schema': 'E001-execution-candidate-1', 'data_kind': 'real_btc',
              'timing_candidate': 'receipt_v1',
              'timing_policy': 'E001-receipt-time-candidate-1',
              'experiment_version': 'e001-v1.3-candidate',
              'feature_schema': 'E001-live-features-receipt-candidate-1',
              'label_schema': 'E001-label-v4-candidate',
              'run_config': str(Path(__file__).resolve().parents[1]/'experiments/e001_run_config.yaml'),
              'evaluation_protocol': str(Path(__file__).resolve().parents[1]/'experiments/e001_btc_evaluation_protocol.yaml'),
              'real_inputs': [{'name': 'bounded', 'manifest': str(manifest),
                               'sealed_prefix': True, 'segment_limit': 1,
                               'decision_seconds': [1]}],
              'fixture_inputs': [{'name': 'synthetic', 'path': str(tmp_path/'fixture.json')}]}
    path = tmp_path/'execution.yaml'
    path.write_text(json.dumps(config))
    return path


def tiny_capture(tmp_path):
    root = tmp_path/'capture'
    store = CaptureStore(root, max_bytes=1_000_000)
    for index, (kind, received) in enumerate((('connected', 0), ('noop', 2*NS))):
        store.append({'schema': 'E001-capture-v1', 'record_id': index,
                      'kind': kind, 'source': 'bybit_linear', 'connection_id': 'c',
                      'received_ns': received})
    store.close()
    manifest = root/(store.run_id+'.manifest.json')
    atomic_json(manifest, {'schema': 'E001-capture-v1', 'asset': 'BTC',
                           'symbol': 'BTCUSDT', 'run_id': store.run_id,
                           'status': 'running'})
    return manifest


def runner(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    return importlib.import_module('run_e001_experiment')


def test_readiness_and_evaluate_fail_closed_on_same_sealed_capture(tmp_path, monkeypatch):
    manifest = tiny_capture(tmp_path)
    config = execution_config(tmp_path, manifest=manifest)
    module = runner(monkeypatch)
    first = module.run(config, 'readiness', tmp_path/'first')
    second = module.run(config, 'evaluate', tmp_path/'second')
    assert first['status'] == second['status'] == 'BLOCKED_TIMING'
    assert first['stages']['capture_integrity']['status'] == 'passed'
    assert first['stages']['feature_feasibility']['status'] == 'blocked'
    assert first['stages']['btc_evaluation']['status'] == 'not_run'
    assert first['primary_eligible_rows'] == 0 and first['primary_score'] is None
    assert second['model_fitted'] is False and second['eth_accessed'] is False
    for name in ('first', 'second'):
        output = tmp_path/name
        receipt = json.loads((output/'manifest.json').read_text())
        assert receipt['result_sha256'] == sha256(output/'result.json')
        assert receipt['report_sha256'] == sha256(output/'report.md')
    with pytest.raises(FileExistsError):
        module.run(config, 'readiness', tmp_path/'first')


def test_fixture_mode_requires_synthetic_provenance_and_does_not_claim_a_score(tmp_path, monkeypatch):
    config = execution_config(tmp_path, manifest=tiny_capture(tmp_path))
    fixture = tmp_path/'fixture.json'
    fixture.write_text(json.dumps({'provenance': 'real_market', 'events': []}))
    module = runner(monkeypatch)
    with pytest.raises(ValueError, match='synthetic provenance'):
        module.run(config, 'fixture', tmp_path/'invalid')
    fixture.write_text(json.dumps({'provenance': 'synthetic_fixture', 'events': [],
                                   'primary_label': {'valid': False}}))
    result = module.run(config, 'fixture', tmp_path/'valid')
    assert result['status'] == 'PIPELINE_NOT_IMPLEMENTED'
    assert result['data_kind'] == 'synthetic_fixture'
    assert result['stages']['fixture_input']['status'] == 'passed'
    assert result['model_fitted'] is False and result['primary_score'] is None


def test_corrupt_segment_fails_instead_of_reporting_readiness(tmp_path, monkeypatch):
    manifest = tiny_capture(tmp_path)
    config = execution_config(tmp_path, manifest=manifest)
    segment = next(manifest.parent.glob('*.jsonl'))
    segment.write_bytes(segment.read_bytes()+b'corrupt')
    with pytest.raises(ValueError, match='integrity mismatch'):
        runner(monkeypatch).run(config, 'readiness', tmp_path/'corrupt')
    output = tmp_path/'corrupt'
    result = json.loads((output/'result.json').read_text())
    assert result['status'] == 'ERROR'
    assert result['error_type'] == 'ReplayError'
    assert 'integrity mismatch' in result['error_message']
    receipt = json.loads((output/'manifest.json').read_text())
    assert receipt['result_sha256'] == sha256(output/'result.json')


def test_repository_synthetic_grid_runs_dataset_stage_only(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    result = runner(monkeypatch).run(root/'experiments/e001_execution_config.yaml',
                                    'fixture', tmp_path/'fixture_grid')
    assert result['status'] == 'PIPELINE_VERIFIED_SYNTHETIC'
    assert result['stages']['episode_dataset']['status'] == 'passed'
    assert result['stages']['synthetic_model_evaluation']['status'] == 'passed'
    assert result['stages']['btc_evaluation']['status'] == 'not_run'
    assert result['synthetic_datasets'][0]['episodes'] == 4
    assert result['synthetic_datasets'][0]['primary_label_states'] == [
        'downside-first', 'recovery-first', None, 'neither-by-horizon']
    assert result['model_fitted'] is True and result['primary_score'] is None
    assert len(result['synthetic_model_evaluations'][0]['paired_predictions']) == 40


def test_invalid_config_preserves_error_receipt(tmp_path, monkeypatch):
    bad = tmp_path/'bad.yaml'
    bad.write_text('{"schema": "unexpected"}')
    output = tmp_path/'invalid_config'
    with pytest.raises(ValueError, match='unsupported execution config schema'):
        runner(monkeypatch).run(bad, 'readiness', output)
    result = json.loads((output/'result.json').read_text())
    assert result['status'] == 'ERROR'
    assert result['config_sha256'] == sha256(bad)
    assert json.loads((output/'manifest.json').read_text())['result_sha256'] == sha256(output/'result.json')
