"""Run the frozen MFSM-RE-OBS-1 one-step observability check.

The oracle table and the restricted observer are separate. Headroom appears
only in the oracle audit and in a privileged diagnostic.
"""

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from mfsm_reference.economy import Account, Parameters, State
from mfsm_reference.observation import (
    Candidate, ObserverEnvelope,
    compatible_candidates, compatible_with_privileged_diagnostic,
    observer_envelope, oracle_response, privileged_diagnostic,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/mfsm_reference_observability_001.json"
ECONOMY_CODE = ROOT / "src/mfsm_reference/economy.py"
OBSERVATION_CODE = ROOT / "src/mfsm_reference/observation.py"

OBSERVER_KEYS = (
    "observed_pre_shock_mark",
    "compatible_candidate_count",
    "compatible_candidate_ids",
    "minimum_next_mark",
    "maximum_next_mark",
    "possible_forced_sale_outcomes",
    "status",
    "witness_ids",
)


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _account(raw: dict) -> Account:
    return Account(cash=raw["cash"], units=raw["units"])


def _state(raw: dict) -> State:
    return State(
        holder=_account(raw["holder"]),
        dealer=_account(raw["dealer"]),
        buyer=_account(raw["buyer"]),
        debt=raw["debt"],
        signals=tuple(raw["signals"]),
        tick=raw["tick"],
        breach_ticks=raw["breach_ticks"],
        mode=raw["mode"],
    )


def _law(raw: dict) -> Parameters:
    fields = dict(raw)
    if fields["delay_weights"] is not None:
        fields["delay_weights"] = tuple(fields["delay_weights"])
    return Parameters(**fields)


def _candidate(raw: dict) -> Candidate:
    return Candidate(raw["id"], _state(raw["state"]), _law(raw["law"]))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_protocol(path: Path = PROTOCOL) -> dict:
    protocol = json.loads(path.read_text(encoding="utf-8"))
    _require(protocol.get("schema") == "MFSM-RE-OBS-1-protocol-1",
             "unexpected observability protocol schema")
    _require(protocol["horizon"]["transitions"] == 1,
             "this runner evaluates one transition")
    _require(protocol["observation_map"]["public"]["fields"] == ["mark"],
             "public observation must be the pre-intervention mark only")
    _require(protocol["observation_map"]["privileged_diagnostic"]["classification"]
             == "privileged_diagnostic",
             "headroom-enhanced reading must be classified as a privileged diagnostic")
    candidates = protocol["candidates"]
    identities = [candidate["id"] for candidate in candidates]
    _require(len(identities) == len(set(identities)) and all(identities),
             "candidate ids must be unique and nonempty")
    known = set(identities)
    for case in protocol["cases"]:
        _require(case["candidate_ids"] and set(case["candidate_ids"]) <= known,
                 f"case {case['id']} names an unknown candidate")
    return protocol


def _envelope_record(case: dict, envelope: ObserverEnvelope) -> dict:
    record = {
        "case_id": case["id"],
        "observed_pre_shock_mark": envelope.observed_mark,
        "compatible_candidate_count": envelope.compatible_candidate_count,
        "compatible_candidate_ids": list(envelope.compatible_candidate_ids),
        "minimum_next_mark": envelope.minimum_next_mark,
        "maximum_next_mark": envelope.maximum_next_mark,
        "possible_forced_sale_outcomes": list(envelope.possible_forced_sale_outcomes),
        "status": envelope.status,
        "witness_ids": list(envelope.witness_ids) if envelope.witness_ids else None,
        "range_interpretation": "conditional_on_declared_candidates_not_a_confidence_interval",
    }
    missing = [key for key in OBSERVER_KEYS if key not in record]
    _require(not missing, "observer record is missing a required output")
    return record


def _privileged_case(case: dict, selected: tuple[Candidate, ...], tolerance: float) -> dict:
    observed_mark = case["observed_pre_shock_mark"]
    public = compatible_candidates(selected, observed_mark, tolerance)
    public_ids = [candidate.candidate_id for candidate in public]
    readings = []
    for candidate in public:
        reading = privileged_diagnostic(candidate.state, candidate.law).headroom
        retained = compatible_with_privileged_diagnostic(
            selected, observed_mark, reading, tolerance)
        retained_ids = [item.candidate_id for item in retained]
        _require(set(retained_ids) <= set(public_ids),
                 "privileged diagnostic added a candidate the public mark excludes")
        readings.append({
            "source_candidate_id": candidate.candidate_id,
            "pre_intervention_headroom": reading,
            "compatible_candidate_ids": retained_ids,
            "compatible_candidate_count": len(retained_ids),
            "removed_candidate_ids": [item for item in public_ids if item not in retained_ids],
        })
    return {"case_id": case["id"], "readings": readings}


def build_report(protocol: dict | None = None) -> dict:
    protocol = load_protocol() if protocol is None else protocol
    tolerance = protocol["comparison_tolerance"]
    pre_shock_value = protocol["intervention"]["pre_shock_value"]
    post_shock_value = protocol["intervention"]["post_shock_value"]
    candidates = tuple(_candidate(raw) for raw in protocol["candidates"])
    by_id = {candidate.candidate_id: candidate for candidate in candidates}
    oracle_rows = []
    for candidate in candidates:
        response = oracle_response(
            candidate, pre_shock_value=pre_shock_value,
            post_shock_value=post_shock_value, tolerance=tolerance)
        oracle_rows.append({
            "candidate_id": response.candidate_id,
            "pre_intervention_mark": response.pre_intervention_mark,
            "pre_intervention_headroom": response.pre_intervention_headroom,
            "next_mark": response.next_mark,
            "forced_sale": response.forced_sale,
            "forced_sale_occurred": response.forced_sale_occurred,
            "mode": response.mode,
            "state": asdict(candidate.state),
            "law": asdict(candidate.law),
        })
    observer_rows = []
    privileged_rows = []
    for case in protocol["cases"]:
        selected = tuple(by_id[candidate_id] for candidate_id in case["candidate_ids"])
        envelope = observer_envelope(
            selected, case["observed_pre_shock_mark"],
            pre_shock_value=pre_shock_value, post_shock_value=post_shock_value,
            tolerance=tolerance)
        observer_rows.append(_envelope_record(case, envelope))
        privileged_rows.append(_privileged_case(case, selected, tolerance))
    return {
        "schema": "MFSM-RE-OBS-1-result-1",
        "status": "synthetic_observability_check_only",
        "question": protocol["question"],
        "protocol_sha256": _sha256(PROTOCOL),
        "economy_code_sha256": _sha256(ECONOMY_CODE),
        "observation_code_sha256": _sha256(OBSERVATION_CODE),
        "runner_sha256": _sha256(Path(__file__)),
        "comparison_tolerance": tolerance,
        "intervention": protocol["intervention"],
        "horizon_transitions": protocol["horizon"]["transitions"],
        "oracle_candidates": oracle_rows,
        "observer": observer_rows,
        "privileged_diagnostic": {
            "classification": "privileged_diagnostic",
            "not_public_data": True,
            "added_field": "pre_intervention_headroom",
            "cases": privileged_rows,
        },
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
    write_result(report, args.output)
    print(json.dumps({
        "output": str(args.output),
        "protocol_sha256": report["protocol_sha256"],
        "cases": [row["case_id"] for row in report["observer"]],
        "statuses": [row["status"] for row in report["observer"]],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
