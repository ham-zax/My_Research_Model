"""Causal timing evidence and diagnostic event/receipt interpretations for E001.

An HTTP server-time bound applies only to that HTTP timestamp domain. Callers
must supply independent evidence before applying it to a WebSocket timestamp.
"""

from dataclasses import dataclass
import json
import time
import urllib.request


NS = 1_000_000_000
MAX_LOCAL_STEP_NS = 100_000_000
PROBE_URLS = {
    'binance': 'https://data-api.binance.vision/api/v3/time',
    'bybit': 'https://api.bybit.com/v5/market/time',
}


def offset_interval(start_ns, end_ns, elapsed_ns, server_ns, resolution_ns=1):
    """Bound source-minus-local offset if server time was made in the request interval."""
    if (end_ns < start_ns or elapsed_ns < 0 or resolution_ns < 1 or
            abs(end_ns-start_ns-elapsed_ns) > MAX_LOCAL_STEP_NS):
        raise ValueError('local clock moved during probe')
    return {'offset_lower_ns': server_ns-end_ns-resolution_ns,
            'offset_upper_ns': server_ns-start_ns+resolution_ns}


@dataclass(frozen=True)
class ClockEvidence:
    source: str
    domain: str
    role: str
    epoch: int
    request_start_ns: int
    request_start_monotonic_ns: int
    received_ns: int
    received_monotonic_ns: int
    available_ns: int
    server_ns: int
    resolution_ns: int
    offset_lower_ns: int
    offset_upper_ns: int
    provenance: str = 'public_http_server_time_request_interval_v1'

    @classmethod
    def from_probe(cls, row):
        if row.get('status') != 'ok' or row.get('domain') != 'http_server_time':
            raise ValueError('not a successful HTTP clock probe')
        if row.get('source') not in PROBE_URLS or row.get('role') != 'server_time':
            raise ValueError('unsupported HTTP clock domain')
        if row.get('available_ns', row['received_ns']) < row['received_ns']:
            raise ValueError('clock evidence precedes response receipt')
        bounds = offset_interval(row['request_start_ns'], row['received_ns'],
                                 row['received_monotonic_ns']-row['request_start_monotonic_ns'],
                                 row['server_ns'], row['resolution_ns'])
        if any(row.get(key) != value for key, value in bounds.items()):
            raise ValueError('inconsistent clock probe bounds')
        return cls(row['source'], row['domain'], row['role'], row['epoch'],
                   row['request_start_ns'], row['request_start_monotonic_ns'],
                   row['received_ns'], row['received_monotonic_ns'],
                   row.get('available_ns', row['received_ns']),
                   row['server_ns'], row['resolution_ns'],
                   bounds['offset_lower_ns'], bounds['offset_upper_ns'])


class EvidenceTimeline:
    """Select only same-domain evidence available at the decision in one epoch."""

    def __init__(self):
        self.rows = []

    def add(self, evidence):
        for previous in reversed(self.rows):
            if previous.epoch == evidence.epoch:
                if evidence.available_ns < previous.available_ns:
                    raise ValueError('clock evidence must be available in epoch order')
                break
        self.rows.append(evidence)

    def select(self, source, domain, role, decision_ns, epoch, *, max_age_ns):
        if max_age_ns is None or max_age_ns < 0:
            raise ValueError('explicit nonnegative evidence expiry required')
        for row in reversed(self.rows):
            if row.available_ns > decision_ns:
                continue
            if (row.source, row.domain, row.role, row.epoch) != (source, domain, role, epoch):
                continue
            return row if decision_ns-row.available_ns <= max_age_ns else None
        return None


def event_interval(source_ns, evidence):
    """Map source time to local wall-time interval; never change receipt order."""
    if evidence is None:
        return None
    return (source_ns-evidence.offset_upper_ns, source_ns-evidence.offset_lower_ns)


def arrival_class(event_bounds, receipt_ns):
    if event_bounds is None:
        return 'unknown'
    earliest, latest = event_bounds
    if earliest > receipt_ns:
        return 'impossible'
    if latest > receipt_ns:
        return 'ambiguous'
    return 'possible'


def quote_freshness(event_bounds, receipt_ns, boundary_ns, *, max_age_ns=5*NS):
    """A quote qualifies only if every possible event time is already available and fresh."""
    if event_bounds is None:
        return 'unknown'
    if boundary_ns < receipt_ns:
        return 'unavailable'
    arrival = arrival_class(event_bounds, receipt_ns)
    if arrival != 'possible':
        return arrival
    earliest, latest = event_bounds
    if earliest > boundary_ns:
        return 'impossible'
    if boundary_ns-earliest > max_age_ns:
        return 'stale_or_ambiguous'
    return 'fresh'


def window_membership(event_bounds, left_ns, right_ns, *, left_inclusive=False):
    """Flow window (left, right] by default; uncertainty stays explicit."""
    if event_bounds is None:
        return 'unknown'
    earliest, latest = event_bounds
    if (latest < left_ns if left_inclusive else latest <= left_ns) or earliest > right_ns:
        return 'out'
    if (earliest >= left_ns if left_inclusive else earliest > left_ns) and latest <= right_ns:
        return 'in'
    return 'ambiguous'


def receipt_membership(received_ns, left_ns, right_ns, *, same_epoch=True,
                       left_inclusive=False):
    if not same_epoch:
        return 'unknown'
    inside = (received_ns >= left_ns if left_inclusive else received_ns > left_ns)
    return 'in' if inside and received_ns <= right_ns else 'out'


def dwell_complete(start_bounds, boundary_ns, *, dwell_ns=NS):
    """A dwell may count only when its latest possible start plus dwell has passed."""
    if start_bounds is None:
        return 'unknown'
    earliest, latest = start_bounds
    if earliest+dwell_ns > boundary_ns:
        return 'out'
    if latest+dwell_ns <= boundary_ns:
        return 'in'
    return 'ambiguous'


def probe_server_clock(source, *, epoch=0, timeout=5):
    """Make one bounded public HTTP request; return a capture-safe diagnostic row."""
    if source not in PROBE_URLS:
        raise ValueError('unapproved clock source')
    start_ns, start_mono = time.time_ns(), time.monotonic_ns()
    row = {'source': source, 'domain': 'http_server_time', 'role': 'server_time',
           'epoch': epoch, 'request_start_ns': start_ns,
           'request_start_monotonic_ns': start_mono,
           'provenance': 'public_http_server_time_request_interval_v1',
           'assumption': 'fresh_server_timestamp_generated_within_request_interval',
           'websocket_domain_qualified': False}
    try:
        request = urllib.request.Request(PROBE_URLS[source], headers={
            'User-Agent': 'MFSM-E001-clock-audit/1', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(100_001)
        row['received_ns'], row['received_monotonic_ns'] = time.time_ns(), time.monotonic_ns()
        if len(raw) > 100_000:
            raise ValueError('oversized response')
        payload = json.loads(raw)
        row['raw'] = payload
        row['round_trip_ns'] = row['received_monotonic_ns']-start_mono
        if source == 'binance':
            server_ns, resolution_ns = int(payload['serverTime'])*1_000_000, 1_000_000
        else:
            if payload['retCode'] != 0:
                raise ValueError('Bybit time request failed')
            server_ns, resolution_ns = int(payload['result']['timeNano']), 1
        row.update(server_ns=server_ns, resolution_ns=resolution_ns)
        row.update(offset_interval(start_ns, row['received_ns'],
                                   row['received_monotonic_ns']-start_mono,
                                   server_ns, resolution_ns))
        row['status'] = 'ok'
    except Exception as exc:
        row.setdefault('received_ns', time.time_ns())
        row.setdefault('received_monotonic_ns', time.monotonic_ns())
        row.update(status='error', error_type=type(exc).__name__, error=str(exc)[:200])
    row['available_ns'] = time.time_ns()
    return row
