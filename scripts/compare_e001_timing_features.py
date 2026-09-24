"""Compare strict and receipt-time feature diagnostics on identical sealed BTC inputs."""

import argparse
import gzip
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256


def load_report(path):
    path = Path(path)
    if 'eth' in str(path.resolve()).lower():
        raise ValueError('ETH holdout is sealed')
    report = json.loads(path.read_text())
    features = Path(report['features_path'])
    if sha256(features) != report['features_sha256']:
        raise ValueError('feature output hash mismatch')
    with gzip.open(features, 'rt') as stream:
        rows = [json.loads(line) for line in stream]
    if len(rows) != report['rows']:
        raise ValueError('feature output row count mismatch')
    return path, report, rows


def compare_pair(strict_path, receipt_path):
    strict_file, strict, strict_rows = load_report(strict_path)
    receipt_file, receipt, receipt_rows = load_report(receipt_path)
    for field in ('run_id', 'manifest_sha256_at_selection', 'segment_sha256',
                  'decision_seconds', 'code_sha256'):
        if strict[field] != receipt[field]:
            raise ValueError(f'unmatched {field}')
    if (strict['schema'] != 'E001-live-features-candidate-1' or
            receipt['schema'] != 'E001-live-features-receipt-diagnostic-1'):
        raise ValueError('unexpected feature schema pair')
    if any(row['model_ready'] for row in strict_rows+receipt_rows):
        raise ValueError('diagnostic output cannot be model ready')
    comparisons = []
    for before, after in zip(strict_rows, receipt_rows, strict=True):
        if (before['decision_second'] != after['decision_second'] or
                before['raw'].keys() != after['raw'].keys()):
            raise ValueError('unmatched decision or feature names')
        if after.get('primary_eligible') is not False or after.get('source_freshness_certified') is not False:
            raise ValueError('receipt candidate is not explicitly diagnostic')
        b, a = before['raw'], after['raw']
        comparisons.append({
            'decision_second': before['decision_second'],
            'strict_clock_valid': before['clock_valid'],
            'receipt_local_clock_valid': after['clock_valid'],
            'strict_raw_available': sum(value is not None for value in b.values()),
            'receipt_raw_available': sum(value is not None for value in a.values()),
            'changed_available_fields': [key for key in b if b[key] is not None and
                                         a[key] is not None and b[key] != a[key]],
            'became_available_fields': [key for key in b if b[key] is None and a[key] is not None],
            'became_missing_fields': [key for key in b if b[key] is not None and a[key] is None],
            'strict_pretrigger_scales': before['pretrigger_scales'],
            'receipt_pretrigger_scales': after['pretrigger_scales'],
            'receipt_primary_eligible': after['primary_eligible'],
        })
    return {'run_id': strict['run_id'], 'manifest_sha256': strict['manifest_sha256_at_selection'],
            'segment_sha256': strict['segment_sha256'],
            'strict_report': str(strict_file), 'strict_report_sha256': sha256(strict_file),
            'receipt_report': str(receipt_file), 'receipt_report_sha256': sha256(receipt_file),
            'strict_features_sha256': strict['features_sha256'],
            'receipt_features_sha256': receipt['features_sha256'],
            'feature_code_sha256': strict['code_sha256'],
            'decisions': comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pair', nargs=3, metavar=('NAME', 'STRICT_REPORT', 'RECEIPT_REPORT'),
                        action='append', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    target = Path(args.output)
    if 'eth' in str(target.resolve()).lower():
        parser.error('ETH holdout is sealed')
    pairs = {name: compare_pair(strict, receipt) for name, strict, receipt in args.pair}
    if len(pairs) != len(args.pair):
        parser.error('duplicate pair name')
    root = Path(__file__).resolve().parents[1]
    report = {'schema': 'E001-receipt-feature-comparison-v1',
              'pairs': pairs, 'measurement_changed': True,
              'source_freshness_certified': False, 'primary_eligible_rows': 0,
              'model_fitted': False, 'eth_read': False,
              'comparison_code_sha256': sha256(root/'scripts/compare_e001_timing_features.py')}
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(target, report)
    print(json.dumps({name: [{key: row[key] for key in
                              ('decision_second', 'strict_raw_available', 'receipt_raw_available')}
                             for row in pair['decisions']]
                      for name, pair in pairs.items()}, indent=2))


if __name__ == '__main__':
    main()
