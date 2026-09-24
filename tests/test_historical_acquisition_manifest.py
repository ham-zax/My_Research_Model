"""The paid-spot day list must freeze the exact free-screen inputs and rule."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/freeze_e001_historical_acquisition.py'


def _report():
    months = [f'{year:04d}-{month:02d}'
              for year in range(2023, 2027) for month in range(1, 13)
              if (year, month) >= (2023, 7) and (year, month) <= (2026, 8)]
    early = int(datetime(2024, 1, 1, 0, 5, tzinfo=timezone.utc).timestamp())
    midday = int(datetime(2024, 2, 1, 12, tzinfo=timezone.utc).timestamp())
    return {
        'schema': 'E001-historical-candidate-screen-1',
        'purpose': 'paid_data_acquisition_only',
        'model_fitted': False,
        'primary_eligible': False,
        'rule': {
            'return_window_seconds': 300,
            'free_threshold': -0.006,
            'fallback_threshold': -0.005,
            'bybit_max_trade_age_ms': 5000,
            'screening_lockout_seconds': None,
        },
        'sources': [{'month': month, 'binance_sha256': 'a' * 64,
                     'bybit_sha256': 'b' * 64} for month in months],
        'coverage': {'binance_seconds': 100051200, 'binance_gaps': 0,
                     'free_reference_valid_seconds': 80000000},
        'candidate_days': [
            {'date': '2024-01-01', 'first_signal_s': early,
             'last_signal_s': early, 'primary_signals': 1, 'fallback_signals': 0},
            {'date': '2024-02-01', 'first_signal_s': midday,
             'last_signal_s': midday, 'primary_signals': 0, 'fallback_signals': 1},
        ],
        'candidate_day_count': 2,
        'paid_spot_seed_days': ['2023-12-31', '2024-01-01', '2024-02-01'],
        'paid_spot_seed_day_count': 3,
    }


def test_manifest_freezes_screen_days_and_source_provenance(tmp_path):
    report = tmp_path / 'screen.json'
    report.write_text(json.dumps(_report()))
    output = tmp_path / 'manifest.json'

    run = subprocess.run(
        [sys.executable, str(SCRIPT), '--report', str(report), '--output', str(output)],
        cwd=ROOT, capture_output=True, text=True)

    assert run.returncode == 0, run.stderr
    manifest = json.loads(output.read_text())
    assert manifest['candidate_days'] == ['2024-01-01', '2024-02-01']
    assert manifest['paid_spot_seed_days'] == [
        '2023-12-31', '2024-01-01', '2024-02-01']
    assert manifest['candidate_days_sha256'] == hashlib.sha256(
        b'2024-01-01\n2024-02-01\n').hexdigest()
    assert manifest['screen_report_sha256'] == hashlib.sha256(report.read_bytes()).hexdigest()
    assert len(manifest['free_sources']) == 38
    assert manifest['paid_l2_acquired'] is False
    assert manifest['model_fitted'] is False


def test_manifest_rejects_changed_screen_rule(tmp_path):
    broken = _report()
    broken['rule']['free_threshold'] = -0.0065
    report = tmp_path / 'screen.json'
    report.write_text(json.dumps(broken))
    output = tmp_path / 'manifest.json'

    run = subprocess.run(
        [sys.executable, str(SCRIPT), '--report', str(report), '--output', str(output)],
        cwd=ROOT, capture_output=True, text=True)

    assert run.returncode != 0
    assert not output.exists()
