#!/usr/bin/env python3
"""Freeze the free BTC screen's spot-day list before any paid acquisition."""

from argparse import ArgumentParser
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json, sha256


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = ROOT / 'artifacts/e001_historical_screen_calibration.json'
PROTOCOL = ROOT / 'experiments/e001_liquidity_observational_protocol.yaml'
CATALOG_START = date(2023, 7, 1)
CATALOG_END = date(2026, 8, 31)
PREVIOUS_DAY_SUPPORT_SECONDS = 7500


def _months():
    year, month = 2023, 7
    while (year, month) <= (2026, 8):
        yield f'{year:04d}-{month:02d}'
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def _digest_days(days):
    return hashlib.sha256(('\n'.join(days) + '\n').encode()).hexdigest()


def _hash64(value):
    return (isinstance(value, str) and len(value) == 64 and
            all(char in '0123456789abcdef' for char in value))


def build_manifest(report_path):
    report_path = Path(report_path)
    report = json.loads(report_path.read_text())
    calibration = json.loads(CALIBRATION.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    if (report.get('schema') != 'E001-historical-candidate-screen-1' or
            report.get('purpose') != 'paid_data_acquisition_only' or
            report.get('model_fitted') is not False or
            report.get('primary_eligible') is not False):
        raise ValueError('not an ineligible E001 historical acquisition screen')
    if (calibration.get('schema') != 'E001-historical-screen-calibration-1' or
            protocol.get('schema') != 'E001-LIQ-OBS-protocol-1'):
        raise ValueError('frozen calibration or protocol mismatch')
    frozen = calibration['frozen_candidate_day_rule']
    declared = protocol['historical_extension']['candidate_day_rule']
    if (frozen.get('return_window_seconds') != 300 or
            '-0.0060' not in frozen.get('primary_condition', '') or
            '-0.0050' not in frozen.get('missing_reference_fallback', '') or
            frozen.get('screening_lockout') != 'none' or
            declared.get('return_window_seconds') != 300 or
            '-0.0060' not in declared.get('primary_condition', '') or
            '-0.0050' not in declared.get('missing_reference_fallback', '') or
            not declared.get('screening_lockout', '').startswith('none')):
        raise ValueError('calibration and protocol do not declare the frozen rule')
    rule = report.get('rule', {})
    if (rule.get('return_window_seconds') != 300 or
            Decimal(str(rule.get('free_threshold'))) != Decimal('-0.0060') or
            Decimal(str(rule.get('fallback_threshold'))) != Decimal('-0.0050') or
            rule.get('bybit_max_trade_age_ms') != 5000 or
            rule.get('screening_lockout_seconds', 'missing') is not None):
        raise ValueError('screen report uses a different acquisition rule')

    coverage = report.get('coverage', {})
    if (coverage.get('binance_seconds') != 100051200 or
            coverage.get('binance_gaps') != 0 or
            type(coverage.get('free_reference_valid_seconds')) is not int or
            not 0 <= coverage['free_reference_valid_seconds'] <= 100051200):
        raise ValueError('incomplete or gapped July 2023–August 2026 screen')
    sources = report.get('sources', [])
    if [row.get('month') for row in sources] != list(_months()) or any(
            not _hash64(row.get('binance_sha256')) or
            not _hash64(row.get('bybit_sha256')) for row in sources):
        raise ValueError('missing, unordered, or unhashed free-source month')

    rows = report.get('candidate_days', [])
    days = [row.get('date') for row in rows]
    if (days != sorted(set(days)) or
            report.get('candidate_day_count') != len(days)):
        raise ValueError('candidate days are not ordered, unique, and counted')
    expected_spot_days = set(days)
    for row in rows:
        day = date.fromisoformat(row['date'])
        first = row.get('first_signal_s')
        if (not CATALOG_START <= day <= CATALOG_END or
                type(first) is not int or
                datetime.fromtimestamp(first, timezone.utc).date() != day or
                row.get('primary_signals', 0) + row.get('fallback_signals', 0) < 1):
            raise ValueError('invalid candidate-day signal')
        if first % 86400 < PREVIOUS_DAY_SUPPORT_SECONDS:
            expected_spot_days.add((day - timedelta(days=1)).isoformat())
    spot_days = report.get('paid_spot_seed_days', [])
    if (spot_days != sorted(expected_spot_days) or
            report.get('paid_spot_seed_day_count') != len(spot_days)):
        raise ValueError('spot boundary-support days do not match screen signals')

    return {
        'schema': 'E001-historical-spot-acquisition-manifest-1',
        'purpose': 'freeze_paid_spot_candidate_days_before_purchase',
        'asset': 'BTC',
        'screened_period': '2023-07 through 2026-08',
        'screen_report_sha256': sha256(report_path),
        'calibration_sha256': sha256(CALIBRATION),
        'protocol_sha256': sha256(PROTOCOL),
        'scanner_code_sha256': sha256(ROOT / 'scripts/scan_e001_historical_candidates.py'),
        'free_sources': [
            {'month': row['month'], 'binance_sha256': row['binance_sha256'],
             'bybit_sha256': row['bybit_sha256']} for row in sources],
        'screen_rule': {
            'free_reference_return_lte': '-0.0060',
            'missing_reference_binance_return_lte': '-0.0050',
            'return_window_seconds': 300,
            'bybit_trade_max_age_ms': 5000,
            'screening_lockout': None,
            'role': 'acquisition_only_not_final_trigger',
        },
        'candidate_days': days,
        'candidate_day_count': len(days),
        'candidate_days_sha256': _digest_days(days),
        'paid_spot_seed_days': spot_days,
        'paid_spot_seed_day_count': len(spot_days),
        'paid_spot_seed_days_sha256': _digest_days(spot_days),
        'spot_catalog_coverage_exceptions': [
            item for item in spot_days if not
            CATALOG_START <= date.fromisoformat(item) <= CATALOG_END],
        'spot_instruments': {'binance': 67838, 'bybit': 2000},
        'spot_availability_verified': False,
        'paid_l2_acquired': False,
        'final_receipt_time_trigger_built': False,
        'model_fitted': False,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise FileExistsError(f'acquisition manifest already exists: {args.output}')
        manifest = build_manifest(args.report)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(args.output, manifest)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'historical acquisition freeze error: {exc}\n')
    print(json.dumps({
        'candidate_day_count': manifest['candidate_day_count'],
        'paid_spot_seed_day_count': manifest['paid_spot_seed_day_count'],
        'spot_catalog_coverage_exceptions': manifest['spot_catalog_coverage_exceptions'],
        'manifest_sha256': sha256(args.output),
    }, sort_keys=True))


if __name__ == '__main__':
    main()
