"""Versioned episode/label joins on one receipt-time spot grid.

Real callers must pass already qualified feature rows. This builder never
promotes a diagnostic row merely because its spot reference is valid.
"""

from dataclasses import asdict
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path

from .capture_store import sha256

from .events import CompositePoint, Event
from .labels import label_event
from .sampling import audit_episode_history


PRIMARY_HORIZON_S = 1800
SECONDARY_HORIZON_S = 7200


def _price(value):
    if value is None:
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('invalid grid price') from None
    if not result.is_finite() or result <= 0:
        raise ValueError('invalid grid price')
    return result


def _json_numbers(values):
    return {key: str(value) if isinstance(value, Decimal) else value
            for key, value in values.items()}


def _label(points, event, horizon_s, as_of_ms):
    result = asdict(label_event(points, event, horizon_s=horizon_s))
    # The research split embargo uses the entire prespecified horizon even if
    # the outcome was observed after a few seconds.
    maturity = max(result['available_ms'] or 0, (event.decision_s + horizon_s) * 1000)
    result['training_maturity_ms'] = maturity if result['valid'] else None
    result['training_ready'] = bool(result['valid'] and as_of_ms >= maturity)
    return result


def build_episode_dataset(grid_rows, feature_rows, *, asset, experiment_version,
                          timing_policy, label_schema, source_sha256,
                          training_as_of_ms, synthetic_fixture=False):
    """Audit lockout uncertainty and label accepted crossings within each epoch."""
    if (asset != 'BTC' or not all(isinstance(v, str) and v for v in
                                   (experiment_version, timing_policy, label_schema)) or
            not isinstance(source_sha256, str) or len(source_sha256) != 64 or
            any(c not in '0123456789abcdef' for c in source_sha256) or
            type(training_as_of_ms) is not int or training_as_of_ms < 0):
        raise ValueError('invalid dataset identity or provenance')
    by_epoch = {}
    last_second = -1
    seen_epochs = set()
    current_epoch = None
    for row in grid_rows:
        second, epoch = row.get('second'), row.get('clock_epoch')
        if type(second) is not int or second <= last_second or type(epoch) is not int or epoch < 0:
            raise ValueError('grid seconds and epochs must be ordered and unique')
        if row.get('timing_policy') != timing_policy:
            raise ValueError('grid policy mismatch')
        if epoch != current_epoch:
            if epoch in seen_epochs:
                raise ValueError('epoch cannot resume after a boundary')
            seen_epochs.add(epoch)
            current_epoch = epoch
        available_ns = row.get('latest_received_ns')
        if available_ns is not None and (type(available_ns) is not int or available_ns < 0 or
                                          available_ns > second*1_000_000_000):
            raise ValueError('grid value was not available at cutoff')
        point = CompositePoint(second, _price(row.get('composite_price')),
                               available_ns//1_000_000 if available_ns is not None else None)
        by_epoch.setdefault(epoch, []).append(point)
        last_second = second
    feature_by_decision = {}
    for row in feature_rows:
        second = row.get('decision_second')
        if row.get('timing_policy') != timing_policy:
            raise ValueError('feature policy mismatch')
        if type(second) is not int or second in feature_by_decision:
            raise ValueError('duplicate or invalid feature decision')
        shared, mfsm = row.get('shared'), row.get('mfsm')
        if not isinstance(shared, dict) or not isinstance(mfsm, dict) or any(
                key not in mfsm or mfsm[key] != value for key, value in shared.items()):
            raise ValueError('MFSM must contain the identical shared B4 values')
        feature_by_decision[second] = row
    crossings = []
    episodes = []
    exclusions = []
    for epoch, points in by_epoch.items():
        audit = audit_episode_history(points)
        for crossing in audit['crossings']:
            trigger = crossing['trigger_s']
            status = crossing['status']
            crossings.append({'trigger_s': trigger, 'clock_epoch': epoch,
                              'status': status,
                              'possible_prior_lockout_states': crossing['possible_prior_lockout_states']})
            if status != 'accepted_with_observed_lockout':
                exclusions.append({'trigger_s': trigger, 'clock_epoch': epoch,
                                   'reason': status})
                continue
            event = Event(trigger, trigger+15, True, 'accepted')
            digest = hashlib.sha256(
                f'{asset}|{trigger}|{experiment_version}|{timing_policy}'.encode()).hexdigest()[:24]
            episode_id = f'{asset}-{digest}'
            feature = feature_by_decision.get(event.decision_s)
            if feature is not None and feature.get('timing_quality', {}).get('clock_epoch') != epoch:
                raise ValueError('feature epoch mismatch')
            if feature is not None:
                feature_available = feature.get('latest_input_available_ns',
                                                event.decision_s*1_000_000_000)
                if (type(feature_available) is not int or
                        feature_available > event.decision_s*1_000_000_000):
                    raise ValueError('feature arrived after decision')
            primary = _label(points, event, PRIMARY_HORIZON_S, training_as_of_ms)
            secondary = _label(points, event, SECONDARY_HORIZON_S, training_as_of_ms)
            reasons = []
            if feature is None:
                reasons.append('decision_features_missing')
            elif feature.get('primary_eligible') is not True:
                reasons.append('decision_features_ineligible')
            if feature is not None and feature.get('timing_quality', {}).get('state') != 'qualified':
                reasons.append('decision_timing_unqualified')
            if not primary['valid']:
                reasons.append('primary_label_' + primary['reason'])
            if reasons:
                exclusions.append({'episode_id': episode_id, 'trigger_s': trigger,
                                   'clock_epoch': epoch, 'reason': ','.join(reasons)})
            episodes.append({'episode_id': episode_id, 'asset': asset, 'trigger_s': trigger,
                             'decision_s': event.decision_s, 'clock_epoch': epoch,
                             'experiment_version': experiment_version,
                             'timing_policy': timing_policy, 'label_schema': label_schema,
                             'source_sha256': source_sha256,
                             'decision_feature_available_ms': (
                                 feature_available//1_000_000
                                 if feature is not None else None),
                             'shared': _json_numbers(feature['shared']) if feature else None,
                             'mfsm': _json_numbers(feature['mfsm']) if feature else None,
                             'primary_label': primary, 'secondary_label': secondary,
                             'primary_eligible': not reasons})
    return {'schema': 'E001-episode-dataset-candidate-1',
            'data_kind': 'synthetic_fixture' if synthetic_fixture else 'real_btc',
            'asset': asset, 'experiment_version': experiment_version,
            'timing_policy': timing_policy, 'label_schema': label_schema,
            'source_sha256': source_sha256, 'training_as_of_ms': training_as_of_ms,
            'grid_seconds': sum(map(len, by_epoch.values())), 'clock_epochs': sorted(by_epoch),
            'crossings': crossings, 'episodes': episodes, 'exclusions': exclusions}


def build_synthetic_fixture(path):
    """Expand an explicit compact grid fixture; never infer market provenance."""
    path = Path(path)
    spec = json.loads(path.read_text())
    if (spec.get('schema') != 'E001-synthetic-receipt-grid-1' or
            spec.get('provenance') != 'synthetic_fixture'):
        raise ValueError('fixture input lacks explicit synthetic grid provenance')
    rows = []
    prior_end = -1
    for epoch in spec['grid_epochs']:
        start, end, clock_epoch = (epoch.get('start_s'), epoch.get('end_s'),
                                   epoch.get('clock_epoch'))
        if (type(start) is not int or type(end) is not int or type(clock_epoch) is not int or
                start <= prior_end or end < start or end-start > 100_000):
            raise ValueError('invalid synthetic epoch range')
        changes = {int(second): _price(price) for second, price in epoch['changes'].items()}
        if any(second < start or second > end for second in changes):
            raise ValueError('synthetic change outside epoch')
        missing = set(epoch.get('missing_seconds', []))
        if any(type(second) is not int or second < start or second > end for second in missing):
            raise ValueError('synthetic gap outside epoch')
        price = _price(epoch['initial_price'])
        for second in range(start, end+1):
            price = changes.get(second, price)
            rows.append({'second': second, 'clock_epoch': clock_epoch,
                         'timing_policy': spec['timing_policy'],
                         'composite_price': None if second in missing else price,
                         'latest_received_ns': second*1_000_000_000})
        prior_end = end
    features = []
    for row in spec['decision_features']:
        features.append({'decision_second': row['decision_second'],
                         'timing_policy': spec['timing_policy'],
                         'timing_quality': {'clock_epoch': row['clock_epoch'],
                                            'state': 'qualified'},
                         'primary_eligible': True, 'shared': row['shared'],
                         'mfsm': row['mfsm']})
    return build_episode_dataset(
        rows, features, asset=spec['asset'],
        experiment_version=spec['experiment_version'],
        timing_policy=spec['timing_policy'], label_schema=spec['label_schema'],
        source_sha256=sha256(path), training_as_of_ms=spec['training_as_of_ms'],
        synthetic_fixture=True)
