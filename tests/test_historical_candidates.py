"""Behavioral check for the frozen, acquisition-only BTC day screen."""

from datetime import datetime, timezone
import gzip
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from zipfile import ZipFile


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/scan_e001_historical_candidates.py'
SPEC = spec_from_file_location('e001_historical_candidates', SCRIPT)
screen = module_from_spec(SPEC)
SPEC.loader.exec_module(screen)


def test_free_screen_uses_fallback_only_when_reference_missing(tmp_path, monkeypatch):
    start = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())
    binance = tmp_path / 'BTCUSDT-1s-2024-01.zip'
    rows = []
    for offset in range(601):
        price = ('100' if offset < 300 else '99.4' if offset == 300
                 else '99.39' if offset < 600 else '98.8')
        rows.append(f'{(start + offset) * 1000},0,0,0,{price}\n')
    with ZipFile(binance, 'w') as archive:
        archive.writestr('BTCUSDT-1s-2024-01.csv', ''.join(rows))

    bybit = tmp_path / 'BTCUSDT-2024-01.csv.gz'
    with gzip.open(bybit, 'wt') as stream:
        stream.write('id,timestamp,price,volume,side,rpi\n')
        for trade_id, offset, price in ((1, 0, '100'), (2, 300, '100'),
                                        (3, 301, '99.39')):
            stream.write(f'{trade_id},{(start + offset) * 1000},{price},1,Buy,0\n')

    monkeypatch.setattr(screen, 'verify_binance_month',
                        lambda month, directory: (binance, 'a' * 64))
    monkeypatch.setattr(screen, 'fetch_bybit_month',
                        lambda month, directory: (bybit, 'b' * 64, 'local-fixture'))
    result = screen.scan_months(['2024-01'], binance_dir=Path(tmp_path),
                                bybit_dir=Path(tmp_path))

    day = result['candidate_days'][0]
    assert day['date'] == '2024-01-01'
    assert day['first_signal_s'] == start + 301  # Valid free quote blocks fallback at t=300.
    assert day['primary_signals'] > 1  # No screening lockout.
    assert day['fallback_signals'] > 0  # Bybit is stale by t=600.
    assert result['paid_spot_seed_days'] == ['2023-12-31', '2024-01-01']
    assert result['coverage']['binance_gaps'] == 0
    assert result['model_fitted'] is False
