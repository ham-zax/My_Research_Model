#!/usr/bin/env python3
"""Count E001-style BTC shock crossings from official Binance 1-second archives.

This is an acquisition-planning tool only. It uses Binance spot 1-second close
prices to estimate event incidence and must not be substituted for the frozen
two-venue midpoint trigger in E001-LIQ-OBS-1.
"""

from argparse import ArgumentParser
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.request import urlopen
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1s'


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


def fetch_month(month, cache_dir):
    cache_dir.mkdir(parents=True, exist_ok=True)
    name = f'BTCUSDT-1s-{month}.zip'
    target = cache_dir / name
    checksum_url = f'{BASE}/{name}.CHECKSUM'
    with urlopen(checksum_url, timeout=60) as response:
        expected = response.read().decode().strip().split()[0]
    if target.exists() and sha256(target) == expected:
        return target, expected
    with tempfile.NamedTemporaryFile(dir=cache_dir, prefix='.btc-1s-', delete=False) as tmp:
        pending = Path(tmp.name)
        try:
            with urlopen(f'{BASE}/{name}', timeout=60) as response:
                for block in iter(lambda: response.read(1 << 20), b''):
                    tmp.write(block)
        except BaseException:
            pending.unlink(missing_ok=True)
            raise
    actual = sha256(pending)
    if actual != expected:
        pending.unlink(missing_ok=True)
        raise RuntimeError(f'checksum mismatch for {month}: {actual} != {expected}')
    pending.replace(target)
    return target, expected


def timestamp_second(raw):
    value = int(raw)
    if value >= 10**15:
        return value // 1_000_000
    if value >= 10**12:
        return value // 1_000
    raise ValueError(f'unexpected Binance timestamp scale: {value}')


def scan(paths):
    history = deque(maxlen=301)
    previous_falling = None
    previous_second = None
    last_accepted = None
    crossing_rows = []
    month_rows = []

    for month, path, source_hash in paths:
        rows = gaps = crossings = accepted = 0
        with ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != 1:
                raise RuntimeError(f'{path}: expected one CSV member')
            with archive.open(names[0]) as stream:
                for raw_line in stream:
                    row = raw_line.decode().rstrip().split(',')
                    if len(row) < 5:
                        raise RuntimeError(f'{path}: short kline row')
                    second = timestamp_second(row[0])
                    price = float(row[4])
                    rows += 1
                    if previous_second is not None and second != previous_second + 1:
                        gaps += 1
                        history.clear()
                        previous_falling = None
                    history.append((second, price))
                    falling = None
                    if len(history) == 301 and history[0][0] == second - 300:
                        falling = price / history[0][1] - 1 <= -0.01
                    if falling is True and previous_falling is False:
                        crossings += 1
                        is_accepted = (
                            last_accepted is None or second >= last_accepted + 7200)
                        if is_accepted:
                            accepted += 1
                            last_accepted = second
                        crossing_rows.append({
                            'month': month,
                            'trigger_s': second,
                            'trigger_utc': datetime.fromtimestamp(
                                second, timezone.utc).isoformat(),
                            'accepted_2h_lockout': is_accepted,
                        })
                    previous_falling = falling
                    previous_second = second
        month_rows.append({
            'month': month,
            'source': str(path),
            'sha256': source_hash,
            'rows': rows,
            'gaps': gaps,
            'crossings': crossings,
            'accepted_2h_lockout': accepted,
        })

    return {
        'schema': 'E001-binance-1s-event-yield-1',
        'purpose': 'acquisition_planning_only',
        'trigger_proxy': 'Binance BTCUSDT 1-second close, -1% over exactly 300 seconds',
        'final_trigger_warning': (
            'not the E001-LIQ-OBS two-venue receipt-time midpoint trigger'),
        'episode_lockout_seconds': 7200,
        'months': month_rows,
        'crossings': crossing_rows,
        'summary': {
            'months': len(month_rows),
            'rows': sum(row['rows'] for row in month_rows),
            'gaps': sum(row['gaps'] for row in month_rows),
            'crossings': sum(row['crossings'] for row in month_rows),
            'accepted_2h_lockout': sum(
                row['accepted_2h_lockout'] for row in month_rows),
        },
        'model_fitted': False,
    }


def main():
    parser = ArgumentParser()
    parser.add_argument('--start', required=True, help='YYYY-MM')
    parser.add_argument('--end', required=True, help='YYYY-MM')
    parser.add_argument(
        '--cache-dir', type=Path,
        default=ROOT / 'data/raw/binance_1s')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()

    sources = []
    for month in month_range(args.start, args.end):
        path, source_hash = fetch_month(month, args.cache_dir)
        sources.append((month, path, source_hash))
        print(f'{month}: verified {source_hash}', flush=True)

    report = scan(sources)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
