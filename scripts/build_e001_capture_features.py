"""Build BTC feature diagnostics at explicit decision seconds from sealed captures."""

import argparse
from collections import Counter
import gzip
import io
import json
from pathlib import Path

from mfsm_e001.capture_features import CaptureFeatureReplay, feature_rows
from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.replay import CaptureInput, ReplayError


def run(manifest, output, decision_seconds, *, sealed_prefix=False, segment_limit=None):
    output = Path(output)
    if 'eth' in str(output.resolve()).lower():
        raise ReplayError('ETH holdout is sealed')
    capture = CaptureInput(manifest, sealed_prefix=sealed_prefix, segment_limit=segment_limit)
    output.mkdir(parents=True, exist_ok=True)
    target, temporary = output/'features.jsonl.gz', output/'features.jsonl.gz.tmp'
    replay = CaptureFeatureReplay()
    missing, available = Counter(), Counter()
    count = clocks = scaled = 0
    decisions = sorted(set(decision_seconds))
    try:
        with temporary.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped, \
                io.TextIOWrapper(zipped, encoding='utf-8') as stream:
            for row in feature_rows(capture.records(), decisions, replay):
                stream.write(json.dumps(row, default=str, sort_keys=True, separators=(',', ':'))+'\n')
                count += 1
                clocks += row['clock_valid']
                scaled += row['pretrigger_scales']['depth'] is not None
                missing.update(row['missing_reasons'].values())
                available.update(k for k, value in row['raw'].items() if value is not None)
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    root = Path(__file__).resolve().parents[1]
    report = {'schema': 'E001-live-features-candidate-1',
        'provenance': 'explicit_decision_feature_diagnostics_not_event_selection_or_model_evaluation',
        'scope': 'sealed_prefix_only' if sealed_prefix else 'completed_capture',
        'run_id': capture.manifest['run_id'], 'capture_status_at_selection': capture.manifest['status'],
        'manifest_path': str(capture.path), 'manifest_sha256_at_selection': capture.manifest_sha256,
        'sealed_segment_count': len(capture.segments), 'segment_sha256': capture.hashes,
        'decision_seconds': decisions, 'features_path': str(target), 'features_sha256': sha256(target),
        'code_sha256': {name: sha256(root/name) for name in (
            'src/mfsm_e001/capture_features.py', 'src/mfsm_e001/replay.py', 'src/mfsm_e001/data.py',
            'src/mfsm_e001/capture_health.py', 'src/mfsm_e001/collect.py',
            'scripts/build_e001_capture_features.py')},
        'rows': count, 'clock_valid_rows': clocks, 'valid_pretrigger_depth_scale_rows': scaled,
        'raw_feature_available_rows': dict(available), 'missing_reason_counts': dict(missing),
        'replay_diagnostics': dict(replay.diagnostics),
        'full_common_feature_panel_complete': False, 'feed_completeness_verified': False,
        'model_fitted': False, 'eth_accessed': False}
    atomic_json(output/'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', required=True)
    parser.add_argument('--decision-second', type=int, action='append', required=True,
                        help='Explicit UTC epoch second; repeat for multiple diagnostic decisions')
    parser.add_argument('--sealed-prefix', action='store_true')
    parser.add_argument('--max-segments', type=int)
    args = parser.parse_args()
    report = run(args.manifest, args.output, args.decision_second,
                 sealed_prefix=args.sealed_prefix, segment_limit=args.max_segments)
    print(json.dumps({k: report[k] for k in ('scope', 'rows', 'clock_valid_rows',
        'valid_pretrigger_depth_scale_rows', 'missing_reason_counts', 'replay_diagnostics')}, indent=2))


if __name__ == '__main__':
    main()
