"""Fixed candidate chronological partitions and paired episode validation."""

import math


FIT_MIN = 50
CALIBRATION_SIZE = 20
VALIDATION_SIZE = 20
TEST_SIZE = 20


def _number(value):
    if value is None or isinstance(value, bool):
        raise ValueError('missing required feature')
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError('missing required feature') from None
    if not math.isfinite(result):
        raise ValueError('missing required feature')
    return result


def prepare_rows(episodes, shared_features, mfsm_combinations):
    if (not shared_features or not mfsm_combinations or
            len(set(shared_features)) != len(shared_features) or
            len(set(mfsm_combinations)) != len(mfsm_combinations) or
            set(shared_features) & set(mfsm_combinations)):
        raise ValueError('invalid paired feature contract')
    prepared = []
    seen = set()
    last_decision = -1
    for episode in episodes:
        ident, decision = episode.get('episode_id'), episode.get('decision_s')
        label = episode.get('primary_label', {})
        if not isinstance(ident, str) or ident in seen or type(decision) is not int or decision <= last_decision:
            raise ValueError('duplicate identity or unordered decision')
        seen.add(ident)
        last_decision = decision
        if (episode.get('primary_eligible') is not True or label.get('valid') is not True or
                label.get('value') not in (0, 1)):
            raise ValueError('ineligible episode in matched model input')
        maturity = label.get('training_maturity_ms')
        if type(maturity) is not int or maturity < decision*1000:
            raise ValueError('invalid label maturity')
        shared, mfsm = episode.get('shared'), episode.get('mfsm')
        if not isinstance(shared, dict) or not isinstance(mfsm, dict):
            raise ValueError('missing required feature')
        if any(key not in mfsm or mfsm[key] != value for key, value in shared.items()):
            raise ValueError('shared feature mismatch')
        x_shared = [_number(shared.get(name)) for name in shared_features]
        x_extra = [_number(mfsm.get(name)) for name in mfsm_combinations]
        prepared.append({'episode_id': ident, 'decision_s': decision,
                         'maturity_ms': maturity, 'y': int(label['value']),
                         'x_b4': x_shared, 'x_mfsm': x_shared+x_extra})
    return prepared


def walk_forward_splits(rows):
    """Expanding fit, disjoint 20/20 calibration/validation, then 20 test rows."""
    minimum = FIT_MIN + CALIBRATION_SIZE + VALIDATION_SIZE + 2*TEST_SIZE
    if len(rows) < minimum:
        raise ValueError(f'insufficient episodes: need at least {minimum}')
    folds = []
    for test_start in range(FIT_MIN+CALIBRATION_SIZE+VALIDATION_SIZE,
                            len(rows)-TEST_SIZE+1, TEST_SIZE):
        fit_end = test_start-CALIBRATION_SIZE-VALIDATION_SIZE
        cal_end = fit_end+CALIBRATION_SIZE
        fold = {'fit': list(range(0, fit_end)),
                'calibration': list(range(fit_end, cal_end)),
                'validation': list(range(cal_end, test_start)),
                'test': list(range(test_start, test_start+TEST_SIZE))}
        for earlier, later in (('fit', 'calibration'), ('calibration', 'validation'),
                               ('validation', 'test')):
            cutoff = rows[fold[later][0]]['decision_s']*1000
            if any(rows[i]['maturity_ms'] > cutoff for i in fold[earlier]):
                raise ValueError(f'immature label crosses {earlier}/{later} cutoff')
        for role in ('fit', 'calibration'):
            if {rows[i]['y'] for i in fold[role]} != {0, 1}:
                raise ValueError(f'both classes required in {role}')
        folds.append(fold)
    return folds
