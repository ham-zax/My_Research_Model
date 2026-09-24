#!/usr/bin/env python3
"""Build the frozen E001 historical paid-data candidate-day screen.

This scanner is acquisition planning only. It combines official Binance
BTCUSDT one-second close prices with the latest Bybit public BTCUSDT spot trade
available by each second-end. It never becomes the final E001-LIQ-OBS trigger.
"""

from argparse import ArgumentParser
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.request import urlopen
from zipfile import ZipFile

from mfsm_e001.public_archive import read_bybit_spot_gzip


ROOT = Path(__file__).resolve().parents[1]
BINANCE_BASE = 'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1s'
BYBIT_BASE = 'https://public.bybit.com/spot/BTCUSDT'
FREE_THRESHOLD = Decimal('-0.0060')
FALLBACK_THRESHOLD = Decimal('-0.0050')
RETURN_SECONDS = 300
BYBIT_MAX_AGE_MS = 5000
PREVIOUS_DAY_SUPPORT_SECONDS = 2 * 3600 + RETURN_SECONDS


def month_range(start, end):
    year, month = map(int, start.split('-'))
    end_year, end_month = map(int, end.split('-'))
    while (year, month) <= (end_year, end_month):
        yield f'{year:04d}-{month:02d}'
        month += 1
        if month == 13:
            year += 1
            month = 1


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def timestamp_second(raw):
    value = int(raw)
    if value >= 10**15:
        return value // 1_000_000
    if value >= 10**12:
        return value // 1_000
    raise ValueError(f'unexpected Binance timestamp scale: {value}')


def verify_binance_month(month, directory):
    path = directory / f'BTCUSDT-1s-{month}.zip'
    if not path.is_file():
        raise FileNotFoundError(
            f'missing {path}; run scripts/scan_e001_binance_event_yield.py first')
    with urlopen(f'{BINANCE_BASE}/{path.name}.CHECKSUM', timeout=60) as response:
        expected = response.read().decode().strip().split()[0]
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f'Binance checksum mismatch for {month}: {actual} != {expected}')
    return path, actual


def fetch_bybit_month(month, directory):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'BTCUSDT-{month}.csv.gz'
    url = f'{BYBIT_BASE}/{path.name}'
    if not path.exists():
        with tempfile.NamedTemporaryFile(
                dir=directory, prefix='.bybit-btc-', delete=False) as temp:
            pending = Path(temp.name)
            try:
                with urlopen(url, timeout=60) as response:
                    for block in iter(lambda: response.read(1 << 20), b''):
                        temp.write(block)
            except BaseException:
                pending.unlink(missing_ok=True)
                raise
        pending.replace(path)
    # Validate gzip framing before recording a local content hash.
    with gzip.open(path, 'rb') as stream:
        while stream.read(1 << 20):
            pass
    return path, sha256(path), url


def _day_state():
    return {
        'primary_signals': 0,
        'fallback_signals': 0,
        'first_signal_s': None,
        'last_signal_s': None,
        'minimum_free_return': None,
        'minimum_binance_return': None,
    }


def _record_signal(days, second, *, reason, free_return, binance_return):
    day = datetime.fromtimestamp(second, timezone.utc).date().isoformat()
    state = days[day]
    key = 'primary_signals' if reason == 'free_reference' else 'fallback_signals'
    state[key] += 1
    if state['first_signal_s'] is None:
        state['first_signal_s'] = second
    state['last_signal_s'] = second
    if free_return is not None:
        value = float(free_return)
        current = state['minimum_free_return']
        state['minimum_free_return'] = value if current is None else min(current, value)
    value = float(binance_return)
    current = state['minimum_binance_return']
    state['minimum_binance_return'] = value if current is None else min(current, value)


def scan_months(months, *, binance_dir, bybit_dir):
    binance_history = {}
    free_history = {}
    candidate_days = defaultdict(_day_state)
    sources = []
    previous_second = None
    last_bybit_ms = None
    last_bybit_price = None
    rows = gaps = free_valid_seconds = 0

    for month in months:
        binance_path, binance_hash = verify_binance_month(month, binance_dir)
        bybit_path, bybit_hash, bybit_url = fetch_bybit_month(month, bybit_dir)
        sources.append({
            'month': month,
            'binance_path': str(binance_path),
            'binance_sha256': binance_hash,
            'bybit_path': str(bybit_path),
            'bybit_sha256': bybit_hash,
            'bybit_url': bybit_url,
        })

        trades = iter(read_bybit_spot_gzip(bybit_path))
        next_trade = next(trades, None)
        prior_trade_ms = None

        with ZipFile(binance_path) as archive:
            names = archive.namelist()
            if len(names) != 1:
                raise RuntimeError(f'{binance_path}: expected one CSV member')
            with archive.open(names[0]) as stream:
                for raw_line in stream:
                    row = raw_line.decode().rstrip().split(',')
                    if len(row) < 5:
                        raise RuntimeError(f'{binance_path}: short kline row')
                    second = timestamp_second(row[0])
                    price = Decimal(row[4])
                    rows += 1

                    if previous_second is not None and second != previous_second + 1:
                        gaps += 1
                        binance_history.clear()
                        free_history.clear()
                        last_bybit_ms = None
                        last_bybit_price = None

                    boundary_ms = second * 1000 + 999
                    while next_trade is not None and next_trade.event_ms <= boundary_ms:
                        if prior_trade_ms is not None and next_trade.event_ms < prior_trade_ms:
                            raise RuntimeError(
                                f'{bybit_path}: Bybit trade timestamps are not monotonic')
                        prior_trade_ms = next_trade.event_ms
                        last_bybit_ms = next_trade.event_ms
                        last_bybit_price = next_trade.price
                        next_trade = next(trades, None)

                    free_price = None
                    if (last_bybit_ms is not None and
                            0 <= boundary_ms - last_bybit_ms <= BYBIT_MAX_AGE_MS):
                        free_price = (price + last_bybit_price) / 2
                        free_valid_seconds += 1

                    old_binance = binance_history.get(second - RETURN_SECONDS)
                    old_free = free_history.get(second - RETURN_SECONDS)
                    if old_binance is not None:
                        binance_return = price / old_binance - 1
                        free_return = (
                            free_price / old_free - 1
                            if free_price is not None and old_free is not None else None)
                        if free_return is not None and free_return <= FREE_THRESHOLD:
                            _record_signal(
                                candidate_days, second, reason='free_reference',
                                free_return=free_return,
                                binance_return=binance_return)
                        elif free_return is None and binance_return <= FALLBACK_THRESHOLD:
                            _record_signal(
                                candidate_days, second, reason='missing_free_reference',
                                free_return=None,
                                binance_return=binance_return)

                    binance_history[second] = price
                    if free_price is None:
                        free_history.pop(second, None)
                    else:
                        free_history[second] = free_price
                    binance_history.pop(second - RETURN_SECONDS - 1, None)
                    free_history.pop(second - RETURN_SECONDS - 1, None)
                    previous_second = second

        if next_trade is not None:
            raise RuntimeError(
                f'{bybit_path}: trade archive extends beyond matching Binance month')

    retained = []
    paid_spot_seed_days = set()
    by_year = defaultdict(int)
    for day_text, state in sorted(candidate_days.items()):
        day = date.fromisoformat(day_text)
        by_year[str(day.year)] += 1
        paid_spot_seed_days.add(day_text)
        first_signal = datetime.fromtimestamp(
            state['first_signal_s'], timezone.utc)
        if (first_signal.hour * 3600 + first_signal.minute * 60 +
                first_signal.second) < PREVIOUS_DAY_SUPPORT_SECONDS:
            paid_spot_seed_days.add((day - timedelta(days=1)).isoformat())
        retained.append({'date': day_text, **state})

    return {
        'schema': 'E001-historical-candidate-screen-1',
        'purpose': 'paid_data_acquisition_only',
        'model_fitted': False,
        'primary_eligible': False,
        'rule': {
            'return_window_seconds': RETURN_SECONDS,
            'free_threshold': float(FREE_THRESHOLD),
            'fallback_threshold': float(FALLBACK_THRESHOLD),
            'bybit_max_trade_age_ms': BYBIT_MAX_AGE_MS,
            'screening_lockout_seconds': None,
            'free_reference': (
                'equal-weight Binance one-second close and latest Bybit public '
                'spot trade available by second-end'),
            'fallback': (
                'only when the free reference is unavailable at an endpoint, '
                'retain if Binance-only five-minute return <= -0.50%'),
            'final_trigger_warning': (
                'screen is not the E001-LIQ-OBS receipt-time two-venue midpoint trigger'),
        },
        'sources': sources,
        'coverage': {
            'binance_seconds': rows,
            'binance_gaps': gaps,
            'free_reference_valid_seconds': free_valid_seconds,
            'free_reference_valid_percent': (
                100 * free_valid_seconds / rows if rows else None),
        },
        'candidate_days': retained,
        'candidate_day_count': len(retained),
        'candidate_days_by_year': dict(sorted(by_year.items())),
        'paid_spot_seed_days': sorted(paid_spot_seed_days),
        'paid_spot_seed_day_count': len(paid_spot_seed_days),
        'notes': [
            'No two-hour lockout is applied during screening.',
            'Previous-day spot support is added only when a screen signal occurs within the first 2h05m UTC.',
            'Next-day label support is acquired only after the exact paid-spot trigger ledger is rebuilt.',
            'Bybit perpetual L2 is acquired only after exact paid-spot event times are fixed.',
        ],
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--start', required=True, help='YYYY-MM')
    parser.add_argument('--end', required=True, help='YYYY-MM')
    parser.add_argument(
        '--binance-dir', type=Path,
        default=ROOT / 'data/raw/binance_1s')
    parser.add_argument(
        '--bybit-dir', type=Path,
        default=ROOT / 'data/raw/bybit_spot_monthly')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    report = scan_months(
        list(month_range(args.start, args.end)),
        binance_dir=args.binance_dir,
        bybit_dir=args.bybit_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({
        'candidate_day_count': report['candidate_day_count'],
        'paid_spot_seed_day_count': report['paid_spot_seed_day_count'],
        'candidate_days_by_year': report['candidate_days_by_year'],
        'coverage': report['coverage'],
    }, sort_keys=True))


if __name__ == '__main__':
    main()
