"""MFSM-RE-PUBHIST-1 public-history observability checks."""

from dataclasses import asdict, fields, replace
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import pytest

from mfsm_reference.economy import Account, Parameters, State
from mfsm_reference.observation import (
    INCOMPATIBLE_OBSERVATION,
    Candidate,
    oracle_response,
)
from mfsm_reference.public_history import (
    P0,
    P1,
    P2,
    PublicHistoryTrace,
    compatible_histories,
    observer_envelope,
    one_step_response,
    public_trace,
    simulate_prelude,
    traces_compatible,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/mfsm_reference_public_history_001.json"
OLD_PROTOCOL = ROOT / "experiments/mfsm_reference_observability_001.json"


def load_runner():
    path = ROOT / "scripts/run_mfsm_reference_public_history.py"
    spec = spec_from_file_location("run_mfsm_reference_public_history", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def protocol():
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def history_by(
    histories,
    *,
    candidate_id,
    prelude_id,
):
    return next(
        history
        for history in histories
        if history.candidate_id == candidate_id
        and history.prelude_id == prelude_id
    )


def test_flat_path_reproduces_the_old_mark_only_one_step_responses():
    runner = load_runner()
    frozen = protocol()
    histories = runner.build_histories(frozen)
    response_config = frozen["response_comparison"]
    shock = frozen["intervention"]

    old = json.loads(OLD_PROTOCOL.read_text(encoding="utf-8"))
    old_candidates = {
        raw["id"]: runner_module_candidate(raw)
        for raw in old["candidates"]
    }

    pairs = (
        ("d750_i010_exponential", "debt_750_exponential"),
        ("d700_i010_exponential", "debt_700_exponential"),
        ("d750_i010_hyperbolic", "debt_750_hyperbolic"),
    )
    for new_id, old_id in pairs:
        history = history_by(
            histories,
            candidate_id=new_id,
            prelude_id="flat",
        )
        new_response = one_step_response(
            history,
            pre_shock_value=shock["pre_shock_value"],
            post_shock_value=shock["post_shock_value"],
            sale_occurrence_threshold_units=response_config[
                "sale_occurrence_threshold_units"
            ],
        )
        old_response = oracle_response(
            old_candidates[old_id],
            pre_shock_value=shock["pre_shock_value"],
            post_shock_value=shock["post_shock_value"],
            tolerance=response_config["sale_occurrence_threshold_units"],
        )
        assert new_response.pre_shock_mark == old_response.pre_intervention_mark
        assert new_response.next_mark == old_response.next_mark
        assert new_response.forced_sale == old_response.forced_sale
        assert (
            new_response.forced_sale_occurred
            == old_response.forced_sale_occurred
        )


def runner_module_candidate(raw):
    state = raw["state"]
    law = dict(raw["law"])
    if law["delay_weights"] is not None:
        law["delay_weights"] = tuple(law["delay_weights"])
    return Candidate(
        raw["id"],
        State(
            holder=Account(**state["holder"]),
            dealer=Account(**state["dealer"]),
            buyer=Account(**state["buyer"]),
            debt=state["debt"],
            signals=tuple(state["signals"]),
            tick=state["tick"],
            breach_ticks=state["breach_ticks"],
            mode=state["mode"],
        ),
        Parameters(**law),
    )


def test_public_trace_exposes_only_declared_public_fields_and_self_matches():
    runner = load_runner()
    frozen = protocol()
    histories = runner.build_histories(frozen)
    exact = frozen["observation_settings"]["exact"]

    assert [field.name for field in fields(PublicHistoryTrace)] == [
        "marks",
        "total_executed_units",
    ]

    forbidden = {
        "debt",
        "headroom",
        "dealer",
        "benchmark",
        "prelude",
        "candidate",
        "mode",
        "forced_sale",
        "buyer_purchase",
        "post_shock",
    }
    for history in histories:
        for map_id in (P0, P1, P2):
            observed = public_trace(history, map_id)
            keys = set(asdict(observed))
            assert keys == {"marks", "total_executed_units"}
            serialized = json.dumps(asdict(observed), sort_keys=True)
            assert all(token not in serialized for token in forbidden)
            matched = compatible_histories(
                histories,
                observed,
                map_id=map_id,
                price_abs_band=exact["price_abs_band"],
                volume_abs_band=exact["volume_abs_band"],
            )
            assert history.opaque_id in {
                item.opaque_id for item in matched
            }


def test_map_subsets_wider_band_monotonicity_and_negative_control_hold_everywhere():
    runner = load_runner()
    report = runner.build_report(protocol())

    assert report["history_count"] == 36
    assert report["checks"]["all_public_subset_invariants_passed"] is True
    assert report["checks"]["all_wider_band_monotonicity_passed"] is True
    assert report["checks"]["predeclared_negative_control_p2_equals_p1"] is True

    for scope in ("pooled_path_hidden", "known_path_diagnostic"):
        checks = report["checks"][scope]
        assert checks["subset_violations"] == []
        assert checks["band_violations"] == []
        assert checks["negative_control_violations"] == []


def test_wide_observation_band_does_not_change_response_disagreement_thresholds():
    runner = load_runner()
    frozen = protocol()
    histories = runner.build_histories(frozen)
    shock = frozen["intervention"]
    response = frozen["response_comparison"]

    exponential = history_by(
        histories,
        candidate_id="d750_i010_exponential",
        prelude_id="flat",
    )
    hyperbolic = history_by(
        histories,
        candidate_id="d750_i010_hyperbolic",
        prelude_id="flat",
    )
    exp_response = one_step_response(
        exponential,
        pre_shock_value=shock["pre_shock_value"],
        post_shock_value=shock["post_shock_value"],
        sale_occurrence_threshold_units=response[
            "sale_occurrence_threshold_units"
        ],
    )
    hyp_response = one_step_response(
        hyperbolic,
        pre_shock_value=shock["pre_shock_value"],
        post_shock_value=shock["post_shock_value"],
        sale_occurrence_threshold_units=response[
            "sale_occurrence_threshold_units"
        ],
    )
    mark_gap = abs(exp_response.next_mark - hyp_response.next_mark)
    assert mark_gap == pytest.approx(0.0224, abs=5e-4)
    assert mark_gap > response["next_mark_abs_tolerance"]
    assert mark_gap < frozen["observation_settings"]["wide"]["price_abs_band"]

    observed = public_trace(exponential, P0)
    for setting in ("exact", "wide"):
        bands = frozen["observation_settings"][setting]
        envelope = observer_envelope(
            (exponential, hyperbolic),
            observed,
            map_id=P0,
            price_abs_band=bands["price_abs_band"],
            volume_abs_band=bands["volume_abs_band"],
            pre_shock_value=shock["pre_shock_value"],
            post_shock_value=shock["post_shock_value"],
            next_mark_abs_tolerance=response["next_mark_abs_tolerance"],
            sale_occurrence_threshold_units=response[
                "sale_occurrence_threshold_units"
            ],
        )
        assert envelope.witness_ids is not None
        assert envelope.minimum_next_mark != envelope.maximum_next_mark


def test_sale_occurrence_threshold_is_not_the_wide_volume_matching_band():
    state = State(
        holder=Account(0.0, 10.0),
        dealer=Account(1000.0, 0.0),
        buyer=Account(1000.0, 0.0),
        debt=750.0,
    )
    law = Parameters(
        value=100.0,
        impact=0.01,
        inventory_limit=20.0,
        maintenance=0.25,
        restore=0.30,
        buyer_speed=20.0,
        delay=2,
        deadline=10,
        liquidation_rule="fixed_lot",
        lot_units=0.05,
    )
    case = simulate_prelude(
        Candidate("tiny_sale", state, law),
        opaque_id="tiny",
        prelude_id="flat",
        benchmark_values=(100.0, 100.0, 100.0),
    )
    response = one_step_response(
        case,
        pre_shock_value=100.0,
        post_shock_value=98.0,
        sale_occurrence_threshold_units=1e-9,
    )
    assert response.forced_sale == pytest.approx(0.05)
    assert response.forced_sale < 0.1
    assert response.forced_sale_occurred is True


def test_unequal_trace_lengths_and_no_match_are_incompatible():
    observed = PublicHistoryTrace((100.0, 99.0))
    possible = PublicHistoryTrace((100.0,))
    assert (
        traces_compatible(
            observed,
            possible,
            price_abs_band=1e-9,
            volume_abs_band=1e-9,
        )
        is False
    )

    runner = load_runner()
    frozen = protocol()
    histories = runner.build_histories(frozen)
    shock = frozen["intervention"]
    response = frozen["response_comparison"]
    envelope = observer_envelope(
        histories,
        PublicHistoryTrace((1.0,)),
        map_id=P0,
        price_abs_band=1e-9,
        volume_abs_band=1e-9,
        pre_shock_value=shock["pre_shock_value"],
        post_shock_value=shock["post_shock_value"],
        next_mark_abs_tolerance=response["next_mark_abs_tolerance"],
        sale_occurrence_threshold_units=response[
            "sale_occurrence_threshold_units"
        ],
    )
    assert envelope.status == INCOMPATIBLE_OBSERVATION
    assert envelope.compatible_history_count == 0
    assert envelope.minimum_next_mark is None
    assert envelope.maximum_next_mark is None
    assert envelope.witness_ids is None


def test_runner_separates_oracle_metadata_from_observer_records(tmp_path):
    runner = load_runner()
    frozen = protocol()
    report = runner.build_report(frozen)

    assert report["schema"] == "MFSM-RE-PUBHIST-1-result-1"
    assert report["candidate_count"] == 18
    assert report["history_count"] == 36
    assert len(report["oracle_histories"]) == 36
    assert report["invalid_candidates"] == []

    oracle = report["oracle_histories"][0]
    assert "candidate_id" in oracle
    assert "prelude_id" in oracle
    assert "final_hidden_state" in oracle
    assert "one_step_response" in oracle

    def keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                yield key
                yield from keys(item)
        elif isinstance(value, list):
            for item in value:
                yield from keys(item)

    observer_keys = set(keys(report["observer"]))
    for hidden_key in (
        "candidate_id",
        "prelude_id",
        "debt",
        "headroom",
        "benchmark_path",
        "final_hidden_state",
        "forced_sale",
        "buyer_purchase",
        "mode",
        "probability",
    ):
        assert hidden_key not in observer_keys

    destination = tmp_path / "public_history.json"
    runner.write_result(report, destination)
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    assert loaded["protocol_sha256"] == runner._sha256(PROTOCOL)
    assert loaded["economy_code_sha256"] == runner._sha256(
        ROOT / "src/mfsm_reference/economy.py"
    )
    assert loaded["public_history_code_sha256"] == runner._sha256(
        ROOT / "src/mfsm_reference/public_history.py"
    )
    assert loaded["empirical_data_used"] is False
    assert loaded["model_fitted"] is False
    assert loaded["probabilities_used"] is False
    assert loaded["trading_edge_claim"] is False
    with pytest.raises(FileExistsError):
        runner.write_result(report, destination)
