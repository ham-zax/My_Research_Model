"""Replay a closed BTC capture, or an explicitly frozen prefix of sealed segments."""

import argparse
from collections import Counter
import gzip
import io
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256
from mfsm_e001.replay import CaptureInput, Replay, replay_grid


def run(manifest, output, *, sealed_prefix=False, segment_limit=None):
    capture = CaptureInput(manifest, sealed_prefix=sealed_prefix, segment_limit=segment_limit)
    output = Path(output)
    if 'eth' in str(output.resolve()).lower():
        raise ValueError('ETH holdout is sealed')
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'grid.jsonl.gz'
    temporary = output / 'grid.jsonl.gz.tmp'
    replay = Replay()
    counts = Counter({'grid_seconds': 0, 'valid_composite_seconds': 0,
                      'complete_30m_windows': 0, 'ticker_required_fields_known_seconds': 0})
    invalid, covered, initialized = Counter(), Counter(), Counter()
    first = last = None
    valid_run = 0
    ticker_required = ('openInterest', 'fundingRate', 'markPrice', 'indexPrice', 'nextFundingTime')
    try:
        with temporary.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped, \
                io.TextIOWrapper(zipped, encoding='utf-8') as stream:
            for row in replay_grid(capture.records(), replay):
                stream.write(json.dumps(row, default=str, separators=(',', ':')) + '\n')
                counts['grid_seconds'] += 1
                first = row['second'] if first is None else first
                last = row['second']
                if row['composite_price'] is not None:
                    counts['valid_composite_seconds'] += 1
                    valid_run += 1
                    counts['complete_30m_windows'] += valid_run >= 1801
                else:
                    valid_run = 0
                for venue, quote in row['quotes'].items():
                    if not quote['valid']:
                        invalid[f"{venue}:{quote['reason']}"] += 1
                if not row['clock_valid']:
                    invalid['clock_review_required'] += 1
                for key, book in row['books'].items():
                    if book['ready']:
                        initialized[key] += 1
                        covered[key + ':bid'] += book['bid_band_covered']
                        covered[key + ':ask'] += book['ask_band_covered']
                ticker = row['bybit_linear_ticker']
                if ticker['ready'] and all(ticker['fields'].get(key, {}).get('value') not in (None, '')
                                           for key in ticker_required):
                    counts['ticker_required_fields_known_seconds'] += 1
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    root = Path(__file__).resolve().parents[1]
    report = {
        'schema': 'E001-replay-v1', 'provenance': 'btc_receipt_ordered_state_replay_no_model_fit',
        'scope': 'sealed_prefix_only' if sealed_prefix else 'completed_capture',
        'run_id': capture.manifest['run_id'], 'capture_status_at_selection': capture.manifest['status'],
        'manifest_path': str(capture.path), 'manifest_sha256_at_selection': capture.manifest_sha256,
        'segment_sha256': capture.hashes, 'grid_path': str(target), 'grid_sha256': sha256(target),
        'sealed_segment_count': len(capture.segments),
        'code_sha256': {name: sha256(root / name) for name in
                       ('src/mfsm_e001/replay.py', 'scripts/replay_e001_capture.py',
                        'src/mfsm_e001/capture_health.py', 'src/mfsm_e001/collect.py')},
        'first_grid_second': first, 'last_grid_second': last,
        'counts': dict(counts), 'invalid_quote_seconds': dict(invalid),
        'book_initialized_seconds': dict(initialized), 'band_coverage_seconds': dict(covered),
        'diagnostics': dict(replay.diagnostics),
        'receipt_minus_source_ms_histogram': {source: dict(sorted(values.items()))
                                              for source, values in replay.clock_lag_ms.items()},
        'quote_policy': 'BBO_price_or_size_changes_only; equal_venue_midpoints; max_source_age_5s',
        'book_policy': 'Bybit_top_N_trimmed_separately; Binance_initial_snapshot_known_range_fixed',
        'feed_completeness_verified': False, 'full_common_feature_panel_complete': False,
        'model_fitted': False,
    }
    atomic_json(output / 'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', required=True, help='Directory for grid.jsonl.gz and report.json')
    parser.add_argument('--sealed-prefix', action='store_true', help='Freeze currently sealed segments; exclude the open tail')
    parser.add_argument('--max-segments', type=int, help='Reproduce a prefix using its first N sealed segments')
    args = parser.parse_args()
    result = run(args.manifest, args.output, sealed_prefix=args.sealed_prefix, segment_limit=args.max_segments)
    print(json.dumps({key: result[key] for key in ('scope', 'counts', 'band_coverage_seconds', 'diagnostics')}, indent=2))


if __name__ == '__main__':
    main()
