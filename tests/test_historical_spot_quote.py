"""A purchase quote must cover the frozen, purchasable spot-day basket."""

from datetime import date, timedelta
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/quote_e001_historical_spot.py'


def test_quote_batches_exact_spot_basket_and_records_missing_file():
    assert SCRIPT.is_file()
    spec = importlib.util.spec_from_file_location('historical_spot_quote', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    first = date(2023, 7, 17)
    days = [(first + timedelta(days=offset)).isoformat() for offset in range(367)]
    manifest = {
        'schema': 'E001-historical-spot-acquisition-manifest-1',
        'purpose': 'freeze_paid_spot_candidate_days_before_purchase',
        'spot_instruments': {'binance': 67838, 'bybit': 2000},
        'paid_spot_seed_days': days,
        'paid_spot_seed_day_count': len(days),
        'spot_catalog_coverage_exceptions': ['2023-07-17'],
        'paid_l2_acquired': False,
        'model_fitted': False,
    }
    batches = []

    def quote(items):
        batches.append(items)
        missing = [item for item in items if item == {
            'instrument_id': 2000, 'date': '2023-07-18', 'kind': 'tick'}]
        return {
            'items_requested': len(items),
            'items_available': len(items) - len(missing),
            'total_eur': len(items) - len(missing),
            'missing': [dict(item, reason='no file for this day') for item in missing],
        }

    receipt = module.build_quote_receipt(manifest, quote)

    assert [len(batch) for batch in batches] == [365, 365, 2]
    assert sum(len(batch) for batch in batches) == 732
    assert all(item['date'] != '2023-07-17' for batch in batches for item in batch)
    assert receipt['excluded_spot_days'] == ['2023-07-17']
    assert receipt['items_requested'] == 732
    assert receipt['items_available'] == 731
    assert receipt['total_eur'] == '731'
    assert receipt['missing'] == [{
        'instrument_id': 2000, 'date': '2023-07-18',
        'kind': 'tick', 'reason': 'no file for this day'}]
    assert receipt['checkout_created'] is False
