"""Bracket public exchange clock offsets; never modify clocks or captured timestamps."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from mfsm_e001.capture_store import atomic_json
from mfsm_e001.timing import PROBE_URLS, offset_interval, probe_server_clock

URLS = PROBE_URLS


def probe(source, samples):
    return source, [probe_server_clock(source) for _ in range(samples)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=int, default=3, choices=range(1, 11))
    parser.add_argument('--output', default='data/derived/e001_clock_probe.json')
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=2) as pool:
        probes = dict(pool.map(lambda source: probe(source, args.samples), URLS))
    report = {'provenance': 'public_server_time_offset_bounds_no_correction', 'sources': URLS,
              'assumption': 'Fresh server timestamp generated between request start and response receipt; '
                            'bounds include timestamp quantization, not server clock error. '
                            'HTTP bounds do not certify WebSocket timestamp domains.',
              'probes': probes}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(target, report)
    print(json.dumps({source: [({k: row[k] for k in ('offset_lower_ns', 'offset_upper_ns')}
                               if row['status'] == 'ok' else {'status': row['status'],
                                                              'error': row['error']}) for row in rows]
                      for source, rows in probes.items()}, indent=2))
    return int(any(not any(row['status'] == 'ok' for row in rows) for rows in probes.values()))


if __name__ == '__main__':
    raise SystemExit(main())
