"""Same-family histogram boosting and disjoint sigmoid calibration."""

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.frozen import FrozenEstimator


SEED = 1001
TUNING_GRID = (
    {'max_iter': 20, 'max_leaf_nodes': 7, 'min_samples_leaf': 5},
    {'max_iter': 40, 'max_leaf_nodes': 7, 'min_samples_leaf': 5},
)


def fit_calibrated(rows, fit_indices, calibration_indices, *, feature_key, params):
    """Fit on earlier episodes and calibrate on a disjoint later block."""
    if set(fit_indices) & set(calibration_indices):
        raise ValueError('fit/calibration overlap')
    fit_x = [rows[i][feature_key] for i in fit_indices]
    fit_y = [rows[i]['y'] for i in fit_indices]
    cal_x = [rows[i][feature_key] for i in calibration_indices]
    cal_y = [rows[i]['y'] for i in calibration_indices]
    if set(fit_y) != {0, 1} or set(cal_y) != {0, 1}:
        raise ValueError('both classes required for fit and calibration')
    estimator = HistGradientBoostingClassifier(
        loss='log_loss', early_stopping=False, random_state=SEED,
        l2_regularization=0.1, **params)
    estimator.fit(fit_x, fit_y)
    calibrated = CalibratedClassifierCV(FrozenEstimator(estimator), method='sigmoid')
    calibrated.fit(cal_x, cal_y)
    return calibrated


def probabilities(estimator, rows, indices, *, feature_key):
    return [float(pair[1]) for pair in estimator.predict_proba(
        [rows[i][feature_key] for i in indices])]
