"""Replay a BTC capture into the observational top-level liquidity inputs."""

import argparse
from collections import Counter
import gzip
import io
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.liquidity_live import (
    OBSERVATION_FEATURE_SCHEMA,
    OBSERVATION_POLICY,
    replay_dataset_inputs,
)
from mfsm_e001.replay import CaptureInput


def _write_jsonl_gz(path, rows):
    temporary = path.with_suffix(path.suffix + '.tmp')
    try:
        with temporary.open('wb') as raw, gzip.GzipFile(
                filename='', mode='wb', fileobj=raw, mtime=0) as zipped, \
                io.TextIOWrapper(zipped, encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row, default=str, separators=(',', ':')) + '\n')
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def run(manifest, output, *, sealed_prefix=False, segment_limit=None):
    capture = CaptureInput(
        manifest, sealed_prefix=sealed_prefix, segment_limit=segment_limit)
    output = Path(output).resolve()
    if 'eth' in str(output).lower():
        raise ValueError('ETH holdout is sealed')
    output.mkdir(parents=True, exist_ok=False)

    grid_rows, feature_rows = replay_dataset_inputs(capture.records())
    grid_path = output/'grid.jsonl.gz'
    feature_path = output/'features.jsonl.gz'
    _write_jsonl_gz(grid_path, grid_rows)
    _write_jsonl_gz(feature_path, feature_rows)

    quote_failures = Counter()
    for row in grid_rows:
        for venue, quote in row['quotes'].items():
            if not quote['valid']:
                quote_failures[f"{venue}:{quote['reason']}"] += 1

    valid_features = sum(
        row['raw'].get('valid') is True for row in feature_rows)
    root = Path(__file__).resolve().parents[1]
    report = {
        'schema': 'E001-forward-liquidity-replay-1',
        'data_kind': 'separate_receipt_time_observational_btc',
        'scope': 'sealed_prefix_only' if sealed_prefix else 'completed_capture',
        'run_id': capture.manifest['run_id'],
        'capture_status_at_selection': capture.manifest['status'],
        'manifest_path': str(capture.path),
        'manifest_sha256_at_selection': capture.manifest_sha256,
        'segment_sha256': capture.hashes,
        'sealed_segment_count': len(capture.segments),
        'timing_policy': OBSERVATION_POLICY,
        'feature_schema': OBSERVATION_FEATURE_SCHEMA,
        'grid_path': str(grid_path),
        'grid_sha256': sha256(grid_path),
        'feature_path': str(feature_path),
        'feature_sha256': sha256(feature_path),
        'grid_seconds': len(grid_rows),
        'valid_spot_seconds': sum(
            row['composite_price'] is not None for row in grid_rows),
        'crossing_decision_feature_rows': len(feature_rows),
        'valid_liquidity_measurement_rows': valid_features,
        'invalid_quote_seconds': dict(sorted(quote_failures.items())),
        'source_freshness_certified': False,
        'primary_eligible': False,
        'model_ready': False,
        'model_fitted': False,
        'code_sha256': {
            name: sha256(root/name) for name in (
                'src/mfsm_e001/liquidity_live.py',
                'src/mfsm_e001/liquidity_state.py',
                'src/mfsm_e001/replay.py',
                'scripts/replay_e001_liquidity.py',
            )
        },
    }
    atomic_json(output/'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', required=True)
    parser.add_argument(
        '--sealed-prefix', action='store_true',
        help='Use only currently sealed segments from a running capture.')
    parser.add_argument(
        '--max-segments', type=int,
        help='Use the first N sealed segments; requires --sealed-prefix.')
    args = parser.parse_args()
    try:
        result = run(
            args.manifest, args.output, sealed_prefix=args.sealed_prefix,
            segment_limit=args.max_segments)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'liquidity replay error: {exc}\n')
    print(json.dumps({
        key: result[key] for key in (
            'scope', 'grid_seconds', 'valid_spot_seconds',
            'crossing_decision_feature_rows',
            'valid_liquidity_measurement_rows',
        )
    }, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
