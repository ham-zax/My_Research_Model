from decimal import Decimal

from mfsm_e001.events import CompositePoint
from mfsm_e001.sampling import audit_episode_history


def series(end, dips=(), missing=()):
    return [CompositePoint(s, None if s in missing else Decimal("98" if s in dips else "100"),
                           s * 1000) for s in range(end + 1)]


def statuses(points):
    return {row["trigger_s"]: row["status"] for row in audit_episode_history(points)["crossings"]}


def test_early_sample_crossing_does_not_assume_clear_prior_lockout():
    assert statuses(series(400, dips=(301,))) == {301: "ambiguous_lockout_history"}


def test_observed_quiet_history_can_establish_eligibility():
    assert statuses(series(7600, dips=(7501,))) == {7501: "accepted_with_observed_lockout"}


def test_fixed_two_hour_burn_in_alone_does_not_resolve_early_ambiguous_event():
    result = statuses(series(7400, dips=(301, 7300)))
    assert result == {301: "ambiguous_lockout_history", 7300: "ambiguous_lockout_history"}


def test_exact_lockout_boundary_can_resolve_all_earlier_possibilities():
    result = statuses(series(7600, dips=(301, 7501)))
    assert result[7501] == "accepted_with_observed_lockout"


def test_missing_trigger_comparison_can_restore_lockout_uncertainty():
    assert statuses(series(7900, dips=(7800,), missing=(7600,)))[7800] == "ambiguous_lockout_history"


def test_gap_during_confirmed_lockout_does_not_start_a_second_episode():
    result = statuses(series(7900, dips=(7501, 7800), missing=(7600,)))
    assert result[7501] == "accepted_with_observed_lockout"
    assert result[7800] == "locked_out"
