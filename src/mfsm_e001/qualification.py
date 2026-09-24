"""Causal evidence check for a proposed receipt-time timing policy.

This evaluates explicit records; it does not create a venue clock guarantee.
Real callers must supply separately reviewed contract IDs and policy limits.
"""

from collections.abc import Mapping

REQUIRED_WS_ROLES = (
    'binance_spot_depth', 'bybit_spot_orderbook', 'bybit_linear_orderbook',
    'bybit_linear_ticker', 'bybit_linear_trade', 'bybit_linear_liquidation',
)


def _integer(record, name, *, nonnegative=False):
    value = record.get(name)
    if type(value) is not int or (nonnegative and value < 0):
        raise ValueError(f'invalid {name}')
    return value


def _base(record, domain):
    if not isinstance(record, Mapping) or record.get('domain') != domain:
        raise ValueError('wrong_evidence_domain')
    epoch = _integer(record, 'clock_epoch', nonnegative=True)
    available = _integer(record, 'available_ns', nonnegative=True)
    expiry = _integer(record, 'expires_ns', nonnegative=True)
    if expiry <= available:
        raise ValueError('invalid_evidence_expiry')
    if not isinstance(record.get('provenance'), str) or not record['provenance']:
        raise ValueError('missing_evidence_provenance')
    return epoch, available, expiry


def _utc(record):
    epoch, available, expiry = _base(record, 'independent_utc')
    if not all(isinstance(record.get(key), str) and record[key] for key in
               ('reference', 'upstream')) or record.get('sync_state') != 'synchronized':
        raise ValueError('unverified_utc_reference')
    start_wall = _integer(record, 'request_wall_ns', nonnegative=True)
    end_wall = _integer(record, 'receipt_wall_ns', nonnegative=True)
    start_mono = _integer(record, 'request_mono_ns', nonnegative=True)
    end_mono = _integer(record, 'receipt_mono_ns', nonnegative=True)
    lower = _integer(record, 'offset_lower_ns')
    upper = _integer(record, 'offset_upper_ns')
    drift = _integer(record, 'max_drift_ns', nonnegative=True)
    if lower > upper:
        raise ValueError('contradictory_utc_interval')
    if end_wall < start_wall or end_mono <= start_mono or available < end_wall:
        raise ValueError('invalid_utc_probe_order')
    return epoch, available, expiry, max(abs(lower), abs(upper)) + drift


def _delay(record):
    epoch, available, expiry = _base(record, 'websocket_role_bound')
    if not isinstance(record.get('role'), str) or not record['role'] or not isinstance(
            record.get('contract_id'), str) or not record['contract_id']:
        raise ValueError('missing_role_or_contract')
    transport = _integer(record, 'max_delivery_delay_ns', nonnegative=True)
    clock = _integer(record, 'max_clock_error_ns', nonnegative=True)
    return epoch, available, expiry, transport + clock


def assess_timing_evidence(*, boundary_ns, clock_epoch, utc_records, delay_records,
                           roles, supported_contracts, max_utc_error_ns,
                           max_total_delay_ns, synthetic_fixture=False):
    """Classify only records available by boundary in the same local clock epoch.

    Expired records do not qualify. A subsequent successful record cannot
    backdate a decision. Synthetic provenance is accepted only in fixture mode.
    """
    if (type(boundary_ns) is not int or boundary_ns < 0 or
            type(clock_epoch) is not int or clock_epoch < 0 or
            type(max_utc_error_ns) is not int or max_utc_error_ns < 0 or
            type(max_total_delay_ns) is not int or max_total_delay_ns < 0 or
            not roles or len(set(roles)) != len(roles)):
        raise ValueError('invalid qualification policy')
    records = [('utc', row) for row in utc_records] + [('delay', row) for row in delay_records]
    malformed = []
    chosen_utc = []
    chosen_delay = {role: [] for role in roles}
    for kind, row in records:
        if not isinstance(row, Mapping) or row.get('domain') != (
                'independent_utc' if kind == 'utc' else 'websocket_role_bound'):
            continue  # REST exchange clocks and PHC-only records are different domains.
        if row.get('clock_epoch') != clock_epoch:
            continue
        available_value = row.get('available_ns')
        if type(available_value) is not int:
            malformed.append('invalid available_ns')
            continue
        if available_value > boundary_ns:
            continue
        if row.get('provenance') == 'synthetic_fixture' and not synthetic_fixture:
            continue
        try:
            epoch, available, expiry, bound = (_utc(row) if kind == 'utc' else _delay(row))
        except ValueError as exc:
            malformed.append(str(exc))
            continue
        if epoch != clock_epoch or available > boundary_ns:
            continue
        if kind == 'utc':
            chosen_utc.append((available, expiry, bound))
        elif (row['role'] in chosen_delay and
              supported_contracts.get(row['role']) == row['contract_id']):
            chosen_delay[row['role']].append((available, expiry, bound))
    if malformed:
        return {'state': 'quarantined', 'reasons': sorted(set(malformed)),
                'source_delay_bound_ns': None}
    reasons = []
    expired = False
    latest_utc = max(chosen_utc, default=None)
    if latest_utc is None:
        reasons.append('independent_utc_clock_evidence_missing')
    elif latest_utc[1] < boundary_ns:
        expired = True
        reasons.append('independent_utc_clock_evidence_expired')
    elif latest_utc[2] > max_utc_error_ns:
        reasons.append('independent_utc_error_exceeds_policy')
    role_bounds = []
    for role in roles:
        latest = max(chosen_delay[role], default=None)
        if latest is None:
            reasons.append(f'websocket_role_delay_bound_missing:{role}')
        elif latest[1] < boundary_ns:
            expired = True
            reasons.append(f'websocket_role_delay_bound_expired:{role}')
        else:
            role_bounds.append(latest[2])
    maximum = max(role_bounds, default=None)
    if maximum is not None and maximum > max_total_delay_ns:
        reasons.append('source_delay_exceeds_policy')
    return {'state': ('expired' if expired else 'unknown') if reasons else 'qualified',
            'reasons': reasons, 'source_delay_bound_ns': maximum if not reasons else None}
