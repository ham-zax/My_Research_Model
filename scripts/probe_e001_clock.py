"""Bracket public exchange clock offsets; never modify clocks or captured timestamps."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
import urllib.request

from mfsm_e001.capture_store import atomic_json

URLS = {'binance': 'https://data-api.binance.vision/api/v3/time',
        'bybit': 'https://api.bybit.com/v5/market/time'}


def offset_interval(start_ns, end_ns, elapsed_ns, server_ns, resolution_ns=1):
    if end_ns < start_ns or abs(end_ns - start_ns - elapsed_ns) > 100_000_000:
        raise ValueError('local clock moved during probe')
    return {'offset_lower_ns': server_ns-end_ns-resolution_ns,
            'offset_upper_ns': server_ns-start_ns+resolution_ns}


def probe(source, samples):
    rows = []
    for _ in range(samples):
        start, mono = time.time_ns(), time.monotonic_ns()
        try:
            request = urllib.request.Request(URLS[source], headers={
                'User-Agent': 'MFSM-E001-clock-audit/1', 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(request, timeout=10) as response:
                raw = response.read(100001)
            end, elapsed = time.time_ns(), time.monotonic_ns()-mono
            if len(raw) > 100000:
                raise ValueError('oversized response')
            payload = json.loads(raw)
            if source == 'binance':
                server, resolution = int(payload['serverTime'])*1_000_000, 1_000_000
            else:
                if payload['retCode'] != 0:
                    raise ValueError('Bybit time request failed')
                server, resolution = int(payload['result']['timeNano']), 1
            rows.append({'request_start_ns': start, 'received_ns': end, 'round_trip_ns': elapsed,
                         'server_ns': server, 'raw': payload,
                         **offset_interval(start, end, elapsed, server, resolution)})
        except Exception as exc:
            rows.append({'request_start_ns': start, 'error': f'{type(exc).__name__}: {exc}'})
    return source, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=int, default=3, choices=range(1, 11))
    parser.add_argument('--output', default='data/derived/e001_clock_probe.json')
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=2) as pool:
        probes = dict(pool.map(lambda source: probe(source, args.samples), URLS))
    report = {'provenance': 'public_server_time_offset_bounds_no_correction', 'sources': URLS,
              'assumption': 'Fresh server timestamp generated between request start and response receipt; '
                            'bounds include timestamp quantization, not server clock error.',
              'probes': probes}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(target, report)
    print(json.dumps({source: [({k: row[k] for k in ('offset_lower_ns', 'offset_upper_ns')}
                               if 'server_ns' in row else row) for row in rows]
                      for source, rows in probes.items()}, indent=2))
    return int(any(not any('server_ns' in row for row in rows) for rows in probes.values()))


if __name__ == '__main__':
    raise SystemExit(main())
