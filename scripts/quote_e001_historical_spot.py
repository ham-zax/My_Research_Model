#!/usr/bin/env python3
"""Quote the frozen E001 spot-day basket without creating a checkout."""

from argparse import ArgumentParser
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

from mfsm_e001.capture_store import atomic_json, sha256


ENDPOINT = 'https://cryptostruct.com/mcp'
BATCH_SIZE = 365
SPOT_IDS = {'binance': 67838, 'bybit': 2000}


def build_quote_receipt(manifest, quote):
    if (manifest.get('schema') != 'E001-historical-spot-acquisition-manifest-1' or
            manifest.get('purpose') != 'freeze_paid_spot_candidate_days_before_purchase' or
            manifest.get('spot_instruments') != SPOT_IDS or
            manifest.get('paid_l2_acquired') is not False or
            manifest.get('model_fitted') is not False):
        raise ValueError('not a frozen E001 spot acquisition manifest')
    days = manifest.get('paid_spot_seed_days', [])
    excluded = manifest.get('spot_catalog_coverage_exceptions', [])
    if (not days or days != sorted(set(days)) or
            manifest.get('paid_spot_seed_day_count') != len(days) or
            excluded != sorted(set(excluded)) or
            not set(excluded).issubset(days)):
        raise ValueError('invalid spot day or coverage-exception list')
    quoted_days = [day for day in days if day not in set(excluded)]
    items = [
        {'instrument_id': instrument_id, 'date': day, 'kind': 'tick'}
        for day in quoted_days
        for instrument_id in (SPOT_IDS['binance'], SPOT_IDS['bybit'])
    ]
    if not items:
        raise ValueError('no purchasable spot days to quote')

    missing = []
    batch_receipts = []
    available_count = 0
    total_eur = Decimal(0)
    for offset in range(0, len(items), BATCH_SIZE):
        batch = items[offset:offset + BATCH_SIZE]
        result = quote(batch)
        unavailable = result.get('missing', [])
        missing_keys = [(row.get('instrument_id'), row.get('date'), row.get('kind'))
                        for row in unavailable]
        batch_keys = {(row['instrument_id'], row['date'], row['kind']) for row in batch}
        if (result.get('items_requested') != len(batch) or
                result.get('items_available') != len(batch) - len(unavailable) or
                len(missing_keys) != len(set(missing_keys)) or
                not set(missing_keys).issubset(batch_keys)):
            raise ValueError('price quote did not account for the requested spot items')
        price = Decimal(str(result['total_eur']))
        if price < 0:
            raise ValueError('negative spot price quote')
        available_count += result['items_available']
        total_eur += price
        missing.extend(unavailable)
        batch_receipts.append({
            'items_requested': len(batch),
            'items_available': result['items_available'],
            'total_eur': str(price),
            'missing': unavailable,
        })

    return {
        'schema': 'E001-historical-spot-price-quote-1',
        'purpose': 'read_only_availability_and_cost_before_purchase',
        'source': ENDPOINT,
        'source_tool': 'get_price_quote',
        'spot_instruments': SPOT_IDS,
        'excluded_spot_days': excluded,
        'quoted_spot_day_count': len(quoted_days),
        'items_requested': len(items),
        'items_sha256': hashlib.sha256(
            (json.dumps(items, sort_keys=True, separators=(',', ':')) + '\n').encode()
        ).hexdigest(),
        'items_available': available_count,
        'missing': missing,
        'total_eur': str(total_eur),
        'batch_receipts': batch_receipts,
        'checkout_created': False,
        'paid_l2_acquired': False,
        'model_fitted': False,
    }


def get_price_quote(items):
    request = {
        'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
        'params': {'name': 'get_price_quote', 'arguments': {'items': items}},
    }
    response = subprocess.run(
        ['curl', '-fsSL', ENDPOINT, '-H', 'Content-Type: application/json',
         '-H', 'Accept: application/json, text/event-stream',
         '-d', json.dumps(request)],
        check=True, capture_output=True, text=True, timeout=60,
    )
    rpc = json.loads(response.stdout)
    if 'error' in rpc or rpc.get('result', {}).get('isError'):
        raise ValueError(f'CryptoStruct quote error: {rpc.get("error", rpc.get("result"))}')
    return json.loads(rpc['result']['content'][0]['text'])


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.exit(1, f'spot quote receipt already exists: {args.output}\n')
    try:
        manifest = json.loads(args.manifest.read_text())
        receipt = build_quote_receipt(manifest, get_price_quote)
        receipt['acquisition_manifest_sha256'] = sha256(args.manifest)
        receipt['captured_utc'] = datetime.now(timezone.utc).isoformat()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(args.output, receipt)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'historical spot quote error: {exc}\n')
    print(json.dumps({
        'items_requested': receipt['items_requested'],
        'items_available': receipt['items_available'],
        'missing_count': len(receipt['missing']),
        'total_eur': receipt['total_eur'],
        'receipt_sha256': sha256(args.output),
    }, sort_keys=True))


if __name__ == '__main__':
    main()
