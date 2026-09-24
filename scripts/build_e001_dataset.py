"""Build an E001 episode dataset from an explicitly synthetic receipt grid."""

import argparse
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.dataset import build_synthetic_fixture


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = run(args.fixture, args.output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'E001 dataset error: {exc}\n')
    print(json.dumps({'data_kind': result['data_kind'],
                      'episodes': len(result['episodes']),
                      'crossings': len(result['crossings'])}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
