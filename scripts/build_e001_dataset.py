"""Build an E001 episode dataset from a synthetic grid or diagnostic BTC replay."""

import argparse
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.dataset import (
    build_liquidity_observation_dataset,
    build_synthetic_fixture,
)
from mfsm_e001.replay import CaptureInput


def run(fixture, output):
    fixture, output = Path(fixture).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    dataset = build_synthetic_fixture(fixture)
    atomic_json(output/'dataset.json', dataset)
    atomic_json(output/'manifest.json', {
        'schema': 'E001-dataset-manifest-1', 'data_kind': 'synthetic_fixture',
        'source_path': str(fixture), 'source_sha256': sha256(fixture),
        'dataset_sha256': sha256(output/'dataset.json'),
        'code_sha256': sha256(Path(__file__).resolve().parents[1]/'src/mfsm_e001/dataset.py')})
    return dataset


def run_liquidity(manifest, output, *, experiment_version, label_schema,
                  training_as_of_ms, sealed_prefix=False, segment_limit=None):
    output = Path(output).resolve()
    if 'eth' in str(output).lower():
        raise ValueError('ETH holdout is sealed')
    capture = CaptureInput(
        manifest, sealed_prefix=sealed_prefix, segment_limit=segment_limit)
    output.mkdir(parents=True, exist_ok=False)
    dataset = build_liquidity_observation_dataset(
        capture.records(), source_sha256=capture.manifest_sha256,
        training_as_of_ms=training_as_of_ms,
        experiment_version=experiment_version, label_schema=label_schema)
    atomic_json(output/'dataset.json', dataset)
    root = Path(__file__).resolve().parents[1]
    atomic_json(output/'manifest.json', {
        'schema': 'E001-dataset-manifest-1',
        'data_kind': 'real_btc_diagnostic_liquidity',
        'source_path': str(capture.path),
        'source_sha256': capture.manifest_sha256,
        'segment_sha256': capture.hashes,
        'sealed_segment_count': len(capture.segments),
        'scope': 'sealed_prefix_only' if sealed_prefix else 'completed_capture',
        'dataset_sha256': sha256(output/'dataset.json'),
        'model_ready': False,
        'model_fitted': False,
        'code_sha256': {
            name: sha256(root/name) for name in (
                'src/mfsm_e001/dataset.py',
                'src/mfsm_e001/liquidity_live.py',
                'src/mfsm_e001/liquidity_state.py',
                'scripts/build_e001_dataset.py',
            )
        }})
    return dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--fixture')
    source.add_argument('--liquidity-manifest')
    parser.add_argument('--output', required=True)
    parser.add_argument('--experiment-version')
    parser.add_argument('--label-schema')
    parser.add_argument('--training-as-of-ms', type=int)
    parser.add_argument('--sealed-prefix', action='store_true')
    parser.add_argument('--max-segments', type=int)
    args = parser.parse_args()
    try:
        if args.fixture:
            if any(value is not None for value in (
                    args.experiment_version, args.label_schema, args.training_as_of_ms,
                    args.max_segments)) or args.sealed_prefix:
                raise ValueError('liquidity-only options cannot be used with --fixture')
            result = run(args.fixture, args.output)
        else:
            if not args.experiment_version or not args.label_schema or args.training_as_of_ms is None:
                raise ValueError(
                    'liquidity dataset requires --experiment-version, --label-schema and --training-as-of-ms')
            result = run_liquidity(
                args.liquidity_manifest, args.output,
                experiment_version=args.experiment_version,
                label_schema=args.label_schema,
                training_as_of_ms=args.training_as_of_ms,
                sealed_prefix=args.sealed_prefix,
                segment_limit=args.max_segments)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'E001 dataset error: {exc}\n')
    print(json.dumps({'data_kind': result['data_kind'],
                      'episodes': len(result['episodes']),
                      'crossings': len(result['crossings'])}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
