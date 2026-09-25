"""MFSM-RE-OBS-1: what one pre-shock mark determines after the named shock."""

from dataclasses import asdict, fields, replace
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import exp
from pathlib import Path

import pytest

from mfsm_reference.economy import Account, Parameters, State, headroom, price, step
from mfsm_reference.observation import (
    INCOMPATIBLE_OBSERVATION, INVARIANT_WITHIN_DECLARED_CANDIDATES, NOT_IDENTIFIED,
    Candidate, PublicObservation,
    compatible_candidates, compatible_with_privileged_diagnostic,
    observer_envelope, oracle_response, public_observation,
)


ROOT = Path(__file__).resolve().parents[1]
SENSITIVITY = ROOT / "artifacts/mfsm_reference_sensitivity_result.json"
PROTOCOL = ROOT / "experiments/mfsm_reference_observability_001.json"
TOLERANCE = 1e-9
SHOCK = {"pre_shock_value": 100, "post_shock_value": 98, "tolerance": TOLERANCE}


def reference_state(*, debt=750, dealer_units=0):
    return State(Account(0, 10), Account(1000, dealer_units), Account(1000, 0), debt=debt)


def reference_law(**changes):
    fields_ = dict(value=100, impact=0.01, inventory_limit=20, maintenance=0.25,
                   restore=0.30, buyer_speed=20, delay=2, deadline=10)
    fields_.update(changes)
    return Parameters(**fields_)


def candidate(candidate_id, **changes):
    state_changes = {key: changes.pop(key) for key in ("debt", "dealer_units") if key in changes}
    return Candidate(candidate_id, reference_state(**state_changes), reference_law(**changes))


def envelope(candidates, observed_mark=100.0, **shock):
    options = dict(SHOCK)
    options.update(shock)
    return observer_envelope(candidates, observed_mark, **options)


def sensitivity_observation():
    return json.loads(SENSITIVITY.read_text(encoding="utf-8"))["limited_observation"]


def load_runner():
    path = ROOT / "scripts/run_mfsm_reference_observability.py"
    spec = spec_from_file_location("run_mfsm_reference_observability", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hidden_debt_is_not_identified_from_the_pre_shock_mark():
    stored = sensitivity_observation()["hidden_state_uncertainty"]
    high = candidate("debt_750_exponential", debt=750)
    low = candidate("debt_700_exponential", debt=700)
    assert public_observation(high.state, high.law) == public_observation(low.state, low.law)
    assert public_observation(high.state, high.law).mark == 100
    high_response = oracle_response(high, **SHOCK)
    low_response = oracle_response(low, **SHOCK)
    assert high_response.next_mark == stored["tick_0_mark_range"][0]
    assert low_response.next_mark == stored["tick_0_mark_range"][1]
    assert high_response.next_mark == pytest.approx(95.889719, abs=5e-7)
    assert low_response.next_mark == pytest.approx(98.0)
    assert high_response.forced_sale == stored["tick_0_forced_sales"][0]
    assert low_response.forced_sale == stored["tick_0_forced_sales"][1]
    assert high_response.forced_sale_occurred and not low_response.forced_sale_occurred
    assert headroom(high.state, replace(high.law, value=98)) == stored["post_shock_headrooms_before"][0]
    assert headroom(low.state, replace(low.law, value=98)) == stored["post_shock_headrooms_before"][1]

    report = envelope((high, low))
    assert report.status == NOT_IDENTIFIED
    assert report.compatible_candidate_count == 2
    assert report.minimum_next_mark == stored["tick_0_mark_range"][0]
    assert report.maximum_next_mark == stored["tick_0_mark_range"][1]
    assert report.possible_forced_sale_outcomes == (False, True)
    assert report.witness_ids == ("debt_750_exponential", "debt_700_exponential")
    assert "global" not in report.status


def test_impact_laws_that_share_the_pre_shock_mark_disagree_after_the_shock():
    stored = sensitivity_observation()["structural_law_uncertainty"]["tick_0_marks"]
    exponential = candidate("debt_750_exponential")
    hyperbolic = candidate("debt_750_hyperbolic", impact_curve="hyperbolic")
    assert public_observation(exponential.state, exponential.law) == public_observation(
        hyperbolic.state, hyperbolic.law)
    exponential_response = oracle_response(exponential, **SHOCK)
    hyperbolic_response = oracle_response(hyperbolic, **SHOCK)
    assert exponential_response.next_mark == stored[0]
    assert hyperbolic_response.next_mark == stored[1]
    assert exponential_response.forced_sale_occurred
    assert hyperbolic_response.forced_sale_occurred
    assert exponential_response.next_mark != pytest.approx(hyperbolic_response.next_mark, abs=1e-6)

    report = envelope((exponential, hyperbolic))
    assert report.status == NOT_IDENTIFIED
    assert report.compatible_candidate_count == 2
    assert report.possible_forced_sale_outcomes == (True,)
    assert report.minimum_next_mark == min(stored)
    assert report.maximum_next_mark == max(stored)
    assert report.witness_ids == ("debt_750_exponential", "debt_750_hyperbolic")


def test_an_unmatched_mark_is_an_incompatible_observation():
    report = envelope((candidate("debt_750_exponential"), candidate("debt_700_exponential", debt=700)),
                      observed_mark=50.0)
    assert report.status == INCOMPATIBLE_OBSERVATION
    assert report.compatible_candidate_count == 0
    assert report.compatible_candidate_ids == ()
    assert report.minimum_next_mark is None
    assert report.maximum_next_mark is None
    assert report.possible_forced_sale_outcomes == ()
    assert report.witness_ids is None


def test_public_observation_contains_no_future_or_hidden_information():
    state = reference_state(debt=750)
    law = reference_law()
    observed = public_observation(state, law)
    assert [field.name for field in fields(PublicObservation)] == ["mark"]
    assert set(asdict(observed)) == {"mark"}
    assert observed.mark == price(state, law)
    shocked = replace(law, value=98)
    transition = step(state, shocked)
    assert public_observation(state, law) == observed
    assert observed.mark != transition.mark_after
    assert public_observation(replace(state, debt=700), law) == observed

    immediate = reference_law(delay=0)
    delayed = reference_law(delay=5)
    inventoried = reference_state(debt=0, dealer_units=1)
    assert public_observation(inventoried, immediate) == public_observation(inventoried, delayed)
    immediate_step = step(inventoried, replace(immediate, value=98))
    delayed_step = step(inventoried, replace(delayed, value=98))
    assert immediate_step.buyer_purchase > 0
    assert delayed_step.buyer_purchase == 0
    assert public_observation(inventoried, immediate).mark == pytest.approx(100 * exp(-0.01))
    assert public_observation(inventoried, immediate).mark != immediate_step.mark_after


def test_privileged_headroom_can_only_remove_compatible_candidates():
    high = candidate("debt_750_exponential", debt=750)
    low = candidate("debt_700_exponential", debt=700)
    hyperbolic = candidate("debt_750_hyperbolic", debt=750, impact_curve="hyperbolic")
    shifted = candidate("inventory_discount", debt=750, dealer_units=1)
    candidates = (high, low, hyperbolic, shifted)
    public = compatible_candidates(candidates, 100.0, TOLERANCE)
    assert {item.candidate_id for item in public} == {
        "debt_750_exponential", "debt_700_exponential", "debt_750_hyperbolic"}
    for reading in (0.0, 50.0, -15.0, 35.0, 1e9):
        retained = compatible_with_privileged_diagnostic(candidates, 100.0, reading, TOLERANCE)
        assert {item.candidate_id for item in retained} <= {item.candidate_id for item in public}
        assert "inventory_discount" not in {item.candidate_id for item in retained}

    debt_only = compatible_with_privileged_diagnostic(
        candidates, 100.0, headroom(high.state, high.law), TOLERANCE)
    assert {item.candidate_id for item in debt_only} == {
        "debt_750_exponential", "debt_750_hyperbolic"}
    curves = (high, hyperbolic)
    assert compatible_with_privileged_diagnostic(
        curves, 100.0, headroom(high.state, high.law), TOLERANCE) == curves


def test_agreement_is_only_invariance_within_the_declared_candidates():
    selling = candidate("restore_buyer", buyer_speed=20)
    silent = candidate("no_buyer", buyer_speed=0)
    report = envelope((selling, silent))
    assert report.status == INVARIANT_WITHIN_DECLARED_CANDIDATES
    assert report.compatible_candidate_count == 2
    assert report.witness_ids is None
    assert report.minimum_next_mark == report.maximum_next_mark
    assert report.possible_forced_sale_outcomes == (True,)

    shifted = candidate("inventory_discount", dealer_units=1)
    singleton = envelope((selling, shifted), observed_mark=price(shifted.state, shifted.law))
    assert singleton.compatible_candidate_count == 1
    assert singleton.compatible_candidate_ids == ("inventory_discount",)
    assert singleton.status == INVARIANT_WITHIN_DECLARED_CANDIDATES


def test_witnesses_are_the_first_disagreeing_pair_in_declared_order():
    fast = candidate("fast_buyer", buyer_speed=20)
    slow = candidate("slow_buyer", buyer_speed=0)
    low_debt = candidate("debt_700_exponential", debt=700)
    report = envelope((fast, slow, low_debt))
    assert report.status == NOT_IDENTIFIED
    assert report.witness_ids == ("fast_buyer", "debt_700_exponential")


def test_protocol_runner_keeps_the_observer_apart_from_the_oracle(tmp_path):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert protocol["status"] == "frozen_before_execution"
    assert protocol["intervention"]["pre_shock_value"] == 100
    assert protocol["intervention"]["post_shock_value"] == 98
    assert protocol["comparison_tolerance"] == TOLERANCE
    assert protocol["horizon"]["transitions"] == 1
    assert protocol["observation_map"]["public"]["fields"] == ["mark"]
    assert "debt" in protocol["observation_map"]["public"]["excludes"]
    assert "post_intervention_value" in protocol["observation_map"]["public"]["excludes"]
    report = runner.build_report(protocol)
    stored = sensitivity_observation()
    hidden = stored["hidden_state_uncertainty"]
    curves = stored["structural_law_uncertainty"]["tick_0_marks"]
    by_case = {row["case_id"]: row for row in report["observer"]}
    assert by_case["hidden_debt"]["status"] == NOT_IDENTIFIED
    assert by_case["hidden_debt"]["minimum_next_mark"] == hidden["tick_0_mark_range"][0]
    assert by_case["hidden_debt"]["maximum_next_mark"] == hidden["tick_0_mark_range"][1]
    assert by_case["hidden_debt"]["possible_forced_sale_outcomes"] == [False, True]
    assert by_case["impact_law"]["status"] == NOT_IDENTIFIED
    assert by_case["impact_law"]["minimum_next_mark"] == min(curves)
    assert by_case["impact_law"]["maximum_next_mark"] == max(curves)
    oracle = {row["candidate_id"]: row for row in report["oracle_candidates"]}
    assert oracle["debt_750_exponential"]["state"]["debt"] == 750
    assert oracle["debt_700_exponential"]["mode"] == "NORMAL"
    assert oracle["debt_750_exponential"]["mode"] == "NORMAL"

    def keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                yield key
                yield from keys(item)
        elif isinstance(value, list):
            for item in value:
                yield from keys(item)

    observer_keys = set(keys(report["observer"]))
    for hidden_key in ("debt", "headroom", "dealer_units", "benchmark", "mode",
                       "forced_sale", "holder", "probability"):
        assert hidden_key not in observer_keys
    assert report["privileged_diagnostic"]["classification"] == "privileged_diagnostic"
    privileged = {row["case_id"]: row for row in report["privileged_diagnostic"]["cases"]}
    debt_readings = {row["source_candidate_id"]: row for row in privileged["hidden_debt"]["readings"]}
    assert debt_readings["debt_750_exponential"]["removed_candidate_ids"] == ["debt_700_exponential"]
    assert debt_readings["debt_700_exponential"]["removed_candidate_ids"] == ["debt_750_exponential"]
    curve_readings = {row["source_candidate_id"]: row for row in privileged["impact_law"]["readings"]}
    assert curve_readings["debt_750_exponential"]["removed_candidate_ids"] == []
    assert curve_readings["debt_750_hyperbolic"]["compatible_candidate_count"] == 2

    destination = tmp_path / "observability.json"
    runner.write_result(report, destination)
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    assert loaded["protocol_sha256"] == runner._sha256(PROTOCOL)
    assert loaded["economy_code_sha256"] == runner._sha256(ROOT / "src/mfsm_reference/economy.py")
    assert loaded["observation_code_sha256"] == runner._sha256(ROOT / "src/mfsm_reference/observation.py")
    assert loaded["empirical_data_used"] is False
    assert loaded["probabilities_used"] is False
    with pytest.raises(FileExistsError):
        runner.write_result(report, destination)
