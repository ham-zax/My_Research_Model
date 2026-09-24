"""Run E001 readiness or explicit synthetic fixture checks; fail closed before fitting."""

import argparse
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.readiness import CODE_FILES, inspect_fixture, inspect_real, load_config, render_report


ROOT = Path(__file__).resolve().parents[1]


def _write_result(output, result, config_hash, run_config_hash):
    atomic_json(output/'result.json', result)
    (output/'report.md').write_text(render_report(result), encoding='utf-8')
    atomic_json(output/'manifest.json', {
        'schema': 'E001-execution-manifest-1', 'status': result['status'],
        'config_sha256': config_hash, 'run_config_sha256': run_config_hash,
        'evaluation_protocol_sha256': result.get('evaluation_protocol_sha256'),
        'code_sha256': result['code_sha256'],
        'result_sha256': sha256(output/'result.json'),
        'report_sha256': sha256(output/'report.md'),
    })


def _error_result(mode, exc, *, config_hash, run_config_hash=None,
                  timing_policy='unresolved', protocol_hash=None):
    return {'schema': 'E001-execution-result-1', 'status': 'ERROR',
            'mode': mode, 'data_kind': 'synthetic_fixture' if mode == 'fixture' else 'real_btc',
            'timing_policy': timing_policy, 'config_sha256': config_hash,
            'run_config_sha256': run_config_hash,
            'evaluation_protocol_sha256': protocol_hash,
            'code_sha256': {p: sha256(ROOT/p) for p in CODE_FILES},
            'stages': {}, 'primary_eligible_rows': 0,
            'model_fitted': False, 'primary_score': None, 'eth_accessed': False,
            'error_type': type(exc).__name__, 'error_message': str(exc)[:500]}


def run(config_path, mode, output):
    if mode not in ('readiness', 'evaluate', 'fixture'):
        raise ValueError('unknown execution mode')
    output = Path(output).resolve()
    if 'eth' in str(output).lower():
        raise ValueError('ETH holdout is sealed')
    output.mkdir(parents=True, exist_ok=False)
    config_path = Path(config_path).resolve()
    config_hash = sha256(config_path) if config_path.is_file() else None
    try:
        config, config_hash, run_config_hash = load_config(config_path, ROOT)
    except Exception as exc:
        _write_result(output, _error_result(mode, exc, config_hash=config_hash),
                      config_hash, None)
        raise
    try:
        if mode == 'fixture':
            result = inspect_fixture(config, ROOT, config_sha256=config_hash,
                                     run_config_sha256=run_config_hash)
        else:
            result = inspect_real(config, ROOT, mode=mode, config_sha256=config_hash,
                                  run_config_sha256=run_config_hash)
    except Exception as exc:
        error = _error_result(
            mode, exc, config_hash=config_hash, run_config_hash=run_config_hash,
            timing_policy=config['timing_policy'],
            protocol_hash=sha256(ROOT/config['evaluation_protocol']))
        _write_result(output, error, config_hash, run_config_hash)
        raise
    _write_result(output, result, config_hash, run_config_hash)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--mode', required=True, choices=('readiness', 'evaluate', 'fixture'))
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = run(args.config, args.mode, args.output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'E001 execution error: {exc}\n')
    print(json.dumps({'status': result['status'], 'mode': result['mode'],
                      'primary_eligible_rows': result['primary_eligible_rows'],
                      'model_fitted': result['model_fitted'],
                      'result_path': str(Path(args.output).resolve()/'result.json')},
                     sort_keys=True))
    return 0 if result['status'] in ('READINESS_PASSED', 'PIPELINE_VERIFIED_SYNTHETIC',
                                      'BTC_DEVELOPMENT_FAILED', 'BTC_DEVELOPMENT_PASSED') else 2


if __name__ == '__main__':
    raise SystemExit(main())
