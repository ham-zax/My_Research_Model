"""Run the frozen MFSM-RE-PUBHIST-1 public-history observability check."""

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from mfsm_reference.economy import Account, Parameters, State, TERMINAL_MODES
from mfsm_reference.observation import Candidate
from mfsm_reference.public_history import (
    P0,
    P1,
    P2,
    HistoryCase,
    PublicHistoryTrace,
    observer_envelope,
    one_step_response,
    public_trace,
    simulate_prelude,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/mfsm_reference_public_history_001.json"
ECONOMY_CODE = ROOT / "src/mfsm_reference/economy.py"
OBSERVATION_CODE = ROOT / "src/mfsm_reference/observation.py"
PUBLIC_HISTORY_CODE = ROOT / "src/mfsm_reference/public_history.py"
PUBLIC_MAPS = (P0, P1, P2)


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_protocol(path: Path = PROTOCOL) -> dict:
    protocol = json.loads(path.read_text(encoding="utf-8"))
    _require(
        protocol.get("schema") == "MFSM-RE-PUBHIST-1-protocol-1",
        "unexpected public-history protocol schema",
    )
    _require(
        protocol.get("status") == "frozen_before_execution",
        "public-history protocol must be frozen before execution",
    )
    _require(
        set(protocol["observation_maps"]) == set(PUBLIC_MAPS),
        "protocol must define exactly P0, P1, and P2",
    )
    grid = protocol["candidate_grid"]
    expected_candidates = (
        len(grid["debts"]) * len(grid["impacts"]) * len(grid["impact_curves"])
    )
    _require(
        expected_candidates == grid["candidate_count"] == 18,
        "candidate grid must contain the frozen 18 configurations",
    )
    preludes = protocol["preludes"]
    _require(len(preludes) == 2, "protocol must contain the two frozen preludes")
    _require(
        all(
            len(prelude["benchmark_values"]) == prelude["transitions"] == 3
            for prelude in preludes
        ),
        "each prelude must contain exactly three transitions",
    )
    pre_shock = protocol["intervention"]["pre_shock_value"]
    _require(
        all(prelude["benchmark_values"][-1] == pre_shock for prelude in preludes),
        "every prelude must end at the named pre-shock benchmark",
    )
    _require(
        grid["candidate_count"] * len(preludes) == protocol["truth_cases"]["count"] == 36,
        "truth-case count must be 36",
    )
    response = protocol["response_comparison"]
    _require(
        response["next_mark_abs_tolerance"] > 0
        and response["sale_occurrence_threshold_units"] > 0,
        "response tolerances must be positive",
    )
    return protocol


def _account(raw: dict) -> Account:
    return Account(cash=raw["cash"], units=raw["units"])


def _initial_state(protocol: dict, debt: float) -> State:
    raw = protocol["initial_state"]
    return State(
        holder=_account(raw["holder"]),
        dealer=_account(raw["dealer"]),
        buyer=_account(raw["buyer"]),
        debt=debt,
        signals=tuple(raw["signals"]),
        tick=raw["tick"],
        breach_ticks=raw["breach_ticks"],
        mode=raw["mode"],
    )


def _law(protocol: dict, impact: float, impact_curve: str) -> Parameters:
    fields = dict(protocol["fixed_law"])
    if fields["delay_weights"] is not None:
        fields["delay_weights"] = tuple(fields["delay_weights"])
    fields["impact"] = impact
    fields["impact_curve"] = impact_curve
    return Parameters(**fields)


def build_candidates(protocol: dict) -> tuple[Candidate, ...]:
    candidates = []
    for debt in protocol["candidate_grid"]["debts"]:
        for impact in protocol["candidate_grid"]["impacts"]:
            for curve in protocol["candidate_grid"]["impact_curves"]:
                candidate_id = f"{debt['id']}_{impact['id']}_{curve}"
                candidates.append(
                    Candidate(
                        candidate_id,
                        _initial_state(protocol, debt["value"]),
                        _law(protocol, impact["value"], curve),
                    )
                )
    _require(
        len(candidates) == protocol["candidate_grid"]["candidate_count"],
        "candidate expansion does not match the frozen catalog count",
    )
    _require(
        len({candidate.candidate_id for candidate in candidates}) == len(candidates),
        "candidate ids must be unique",
    )
    return tuple(candidates)


def build_histories(protocol: dict) -> tuple[HistoryCase, ...]:
    histories = []
    index = 1
    for candidate in build_candidates(protocol):
        for prelude in protocol["preludes"]:
            history = simulate_prelude(
                candidate,
                opaque_id=f"h{index:03d}",
                prelude_id=prelude["id"],
                benchmark_values=prelude["benchmark_values"],
            )
            _require(
                history.final_law.value == protocol["intervention"]["pre_shock_value"],
                f"{history.opaque_id} does not end at the named pre-shock benchmark",
            )
            _require(
                history.final_state.mode not in TERMINAL_MODES,
                f"{history.opaque_id} enters terminal mode during the prelude",
            )
            histories.append(history)
            index += 1
    _require(
        len(histories) == protocol["truth_cases"]["count"],
        "history expansion does not match the frozen truth-case count",
    )
    return tuple(histories)


def _trace_record(trace: PublicHistoryTrace) -> dict:
    return {
        "marks": list(trace.marks),
        "anonymous_total_executed_units": (
            list(trace.total_executed_units)
            if trace.total_executed_units is not None
            else None
        ),
    }


def _envelope_record(envelope, observed: PublicHistoryTrace) -> dict:
    return {
        "observed_public_trace": _trace_record(observed),
        "compatible_history_count": envelope.compatible_history_count,
        "compatible_opaque_history_ids": list(envelope.compatible_history_ids),
        "minimum_next_mark": envelope.minimum_next_mark,
        "maximum_next_mark": envelope.maximum_next_mark,
        "possible_forced_sale_outcomes": list(
            envelope.possible_forced_sale_outcomes
        ),
        "status": envelope.status,
        "witness_ids": list(envelope.witness_ids) if envelope.witness_ids else None,
        "range_interpretation": (
            "conditional_on_declared_candidates_not_a_confidence_interval"
        ),
    }


def _scope_records(
    protocol: dict,
    histories: tuple[HistoryCase, ...],
    truth: HistoryCase,
    possible: tuple[HistoryCase, ...],
) -> dict:
    intervention = protocol["intervention"]
    response = protocol["response_comparison"]
    records = {}
    for setting_id, bands in protocol["observation_settings"].items():
        maps = {}
        for map_id in PUBLIC_MAPS:
            observed = public_trace(truth, map_id)
            envelope = observer_envelope(
                possible,
                observed,
                map_id=map_id,
                price_abs_band=bands["price_abs_band"],
                volume_abs_band=bands["volume_abs_band"],
                pre_shock_value=intervention["pre_shock_value"],
                post_shock_value=intervention["post_shock_value"],
                next_mark_abs_tolerance=response["next_mark_abs_tolerance"],
                sale_occurrence_threshold_units=response[
                    "sale_occurrence_threshold_units"
                ],
            )
            maps[map_id] = _envelope_record(envelope, observed)
        records[setting_id] = maps
    return records


def _ids(record: dict) -> set[str]:
    return set(record["compatible_opaque_history_ids"])


def _check_scope_invariants(scope: list[dict]) -> dict:
    subset_violations = []
    band_violations = []
    negative_control_violations = []

    for truth in scope:
        truth_id = truth["truth_history_id"]
        exact = truth["settings"]["exact"]
        wide = truth["settings"]["wide"]
        for setting_id, maps in (("exact", exact), ("wide", wide)):
            p0 = _ids(maps[P0])
            p1 = _ids(maps[P1])
            p2 = _ids(maps[P2])
            if not (p2 <= p1 <= p0):
                subset_violations.append(
                    {
                        "truth_history_id": truth_id,
                        "setting": setting_id,
                        "P0": sorted(p0),
                        "P1": sorted(p1),
                        "P2": sorted(p2),
                    }
                )
            if p2 != p1:
                negative_control_violations.append(
                    {
                        "truth_history_id": truth_id,
                        "setting": setting_id,
                        "P1": sorted(p1),
                        "P2": sorted(p2),
                    }
                )

        for map_id in PUBLIC_MAPS:
            exact_ids = _ids(exact[map_id])
            wide_ids = _ids(wide[map_id])
            if not exact_ids <= wide_ids:
                band_violations.append(
                    {
                        "truth_history_id": truth_id,
                        "map": map_id,
                        "exact": sorted(exact_ids),
                        "wide": sorted(wide_ids),
                    }
                )

    return {
        "subset_p2_p1_p0_passed": not subset_violations,
        "subset_violations": subset_violations,
        "wider_band_monotonicity_passed": not band_violations,
        "band_violations": band_violations,
        "predeclared_negative_control_p2_equals_p1": (
            not negative_control_violations
        ),
        "negative_control_violations": negative_control_violations,
    }


def _oracle_record(protocol: dict, history: HistoryCase) -> dict:
    prelude = next(
        item for item in protocol["preludes"] if item["id"] == history.prelude_id
    )
    intervention = protocol["intervention"]
    response_config = protocol["response_comparison"]
    response = one_step_response(
        history,
        pre_shock_value=intervention["pre_shock_value"],
        post_shock_value=intervention["post_shock_value"],
        sale_occurrence_threshold_units=response_config[
            "sale_occurrence_threshold_units"
        ],
    )
    return {
        "opaque_history_id": history.opaque_id,
        "candidate_id": history.candidate_id,
        "prelude_id": history.prelude_id,
        "benchmark_path": prelude["benchmark_values"],
        "initial_state": asdict(history.initial_state),
        "initial_law": asdict(history.initial_law),
        "prelude_trace": {
            "initial_mark": history.initial_mark,
            "post_transition_marks": list(history.post_transition_marks),
            "forced_sales": list(history.forced_sales),
            "buyer_purchases": list(history.buyer_purchases),
            "anonymous_total_executed_units": list(history.total_executed_units),
            "modes": list(history.modes),
        },
        "final_hidden_state": asdict(history.final_state),
        "final_law": asdict(history.final_law),
        "one_step_response": asdict(response),
    }


def build_report(protocol: dict | None = None) -> dict:
    protocol = load_protocol() if protocol is None else protocol
    histories = build_histories(protocol)

    pooled = []
    known_path = []
    for truth in histories:
        pooled.append(
            {
                "truth_history_id": truth.opaque_id,
                "settings": _scope_records(
                    protocol, histories, truth, histories
                ),
            }
        )
        same_path = tuple(
            history
            for history in histories
            if history.prelude_id == truth.prelude_id
        )
        known_path.append(
            {
                "truth_history_id": truth.opaque_id,
                "settings": _scope_records(
                    protocol, histories, truth, same_path
                ),
            }
        )

    pooled_checks = _check_scope_invariants(pooled)
    known_path_checks = _check_scope_invariants(known_path)
    _require(
        pooled_checks["subset_p2_p1_p0_passed"]
        and known_path_checks["subset_p2_p1_p0_passed"],
        "public-map subset invariant failed",
    )
    _require(
        pooled_checks["wider_band_monotonicity_passed"]
        and known_path_checks["wider_band_monotonicity_passed"],
        "wider observation band removed a compatible history",
    )

    return {
        "schema": "MFSM-RE-PUBHIST-1-result-1",
        "status": "synthetic_public_history_observability_check_only",
        "question": protocol["question"],
        "protocol_sha256": _sha256(PROTOCOL),
        "economy_code_sha256": _sha256(ECONOMY_CODE),
        "observation_code_sha256": _sha256(OBSERVATION_CODE),
        "public_history_code_sha256": _sha256(PUBLIC_HISTORY_CODE),
        "runner_sha256": _sha256(Path(__file__)),
        "candidate_count": protocol["candidate_grid"]["candidate_count"],
        "history_count": len(histories),
        "observation_settings": protocol["observation_settings"],
        "response_comparison": protocol["response_comparison"],
        "intervention": protocol["intervention"],
        "oracle_histories": [
            _oracle_record(protocol, history) for history in histories
        ],
        "observer": {
            "pooled_path_hidden": pooled,
            "known_path_diagnostic": known_path,
        },
        "checks": {
            "pooled_path_hidden": pooled_checks,
            "known_path_diagnostic": known_path_checks,
            "all_public_subset_invariants_passed": (
                pooled_checks["subset_p2_p1_p0_passed"]
                and known_path_checks["subset_p2_p1_p0_passed"]
            ),
            "all_wider_band_monotonicity_passed": (
                pooled_checks["wider_band_monotonicity_passed"]
                and known_path_checks["wider_band_monotonicity_passed"]
            ),
            "predeclared_negative_control_p2_equals_p1": (
                pooled_checks["predeclared_negative_control_p2_equals_p1"]
                and known_path_checks[
                    "predeclared_negative_control_p2_equals_p1"
                ]
            ),
        },
        "invalid_candidates": [],
        "interpretation_limits": protocol["interpretation_limits"],
        "empirical_data_used": False,
        "model_fitted": False,
        "probabilities_used": False,
        "trading_edge_claim": False,
    }


def write_result(report: dict, destination: Path) -> None:
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report()
    _require(
        report["checks"]["predeclared_negative_control_p2_equals_p1"],
        "predeclared P2=P1 negative control failed; audit before writing a result",
    )
    write_result(report, args.output)
    statuses = {}
    for scope_id, rows in report["observer"].items():
        values = set()
        for row in rows:
            for setting in row["settings"].values():
                for record in setting.values():
                    values.add(record["status"])
        statuses[scope_id] = sorted(values)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "protocol_sha256": report["protocol_sha256"],
                "histories": report["history_count"],
                "statuses": statuses,
                "negative_control_passed": report["checks"][
                    "predeclared_negative_control_p2_equals_p1"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
