"""The BTC response audit must not recommend extraction when its gate fails."""

from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/mfsm_btc_response_001_protocol.json"


def _audit_module():
    path = ROOT / "scripts/audit_mfsm_btc_response_feasibility.py"
    spec = spec_from_file_location("audit_mfsm_btc_response_feasibility", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _candidate_record(*, available=True, accepted=0):
    return {
        "available": available,
        "crossings_on_complete_dates": 0 if available else None,
        "accepted_candidate_events_on_complete_dates": accepted if available else None,
        "independent_utc_weeks_on_complete_dates": 0 if available else None,
        "dates_with_accepted_candidate_events": [],
    }


def _result(monkeypatch, *, complete_dates, candidates):
    audit = _audit_module()
    rows = [
        {"date": date, "complete_required_inputs": True, "sources": {}}
        for date in complete_dates
    ]
    monkeypatch.setattr(audit, "_date_rows", lambda protocol: rows)
    monkeypatch.setattr(
        audit, "_spot_candidates", lambda protocol, complete: candidates
    )
    result = audit.build_result(PROTOCOL)
    return result, audit._render_report(result)


def test_zero_complete_dates_do_not_pass_or_recommend_extraction(monkeypatch):
    result, report = _result(
        monkeypatch, complete_dates=[], candidates=_candidate_record()
    )
    assert result["status"] == "INSUFFICIENT_LOCAL_FIELD_OR_EVENT_FEASIBILITY"
    assert result["gate_failures"]
    assert "No local sample date has all four required files" in report
    assert "gate has **not passed**" in report
    assert "field-feasible for development" not in report
    assert "before response-feature extraction" in result["next_gate"]
    assert not result["measurement_field_feasibility"]["spot_trigger"][
        "field_available_on_complete_dates"
    ]


def test_absent_local_archive_fails_through_real_audit_path(tmp_path):
    audit = _audit_module()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    protocol["feasibility"]["tardis_root"] = str(tmp_path / "absent_archive")
    path = tmp_path / "protocol.json"
    path.write_text(json.dumps(protocol), encoding="utf-8")

    result = audit.build_result(path)
    report = audit._render_report(result)
    assert result["status"] == "INSUFFICIENT_LOCAL_FIELD_OR_EVENT_FEASIBILITY"
    assert result["local_tardis"]["complete_required_input_dates"] == 0
    assert "gate has **not passed**" in report
    assert "field-feasible for development" not in report


def test_complete_fields_without_candidate_overlap_do_not_pass(monkeypatch):
    result, report = _result(
        monkeypatch,
        complete_dates=["2026-09-01"],
        candidates=_candidate_record(accepted=0),
    )
    assert result["status"] == "INSUFFICIENT_LOCAL_FIELD_OR_EVENT_FEASIBILITY"
    assert result["measurement_field_feasibility"]["spot_trigger"][
        "field_available_on_complete_dates"
    ]
    assert "No accepted price-defined BTC candidate event overlaps" in report
    assert "gate has **not passed**" in report
    assert "field-feasible for development" not in report


def test_missing_event_ledger_and_success_have_distinct_decisions(monkeypatch):
    failed, failed_report = _result(
        monkeypatch,
        complete_dates=["2026-09-01"],
        candidates=_candidate_record(available=False),
    )
    assert failed["status"] == "INSUFFICIENT_LOCAL_FIELD_OR_EVENT_FEASIBILITY"
    assert "discovery ledger is unavailable" in failed_report

    passed, passed_report = _result(
        monkeypatch,
        complete_dates=["2026-09-01"],
        candidates=_candidate_record(accepted=2),
    )
    assert passed["status"] == "DEVELOPMENT_FEASIBLE_NOT_VALIDATION_READY"
    assert passed["gate_failures"] == []
    assert "field-feasible for development" in passed_report
    assert "outcome-blind response-feature extraction" in passed["next_gate"]


def test_replenishment_boundary_excludes_final_considered_pressure_bin():
    history = json.loads(PROTOCOL.read_text(encoding="utf-8"))["response_history"]
    start = history["window_start_seconds_relative_to_trigger"]
    last_considered = history["window_end_seconds_relative_to_trigger"]
    width = history["bin_seconds"]
    ends = range(start + width, last_considered + 1, width)
    eligible_ends = [end for end in ends if end + width < 0]

    assert history["replenishment_end_strictly_before_trigger"]
    assert last_considered == history[
        "excluded_pressure_bin_end_seconds_relative_to_trigger"
    ]
    assert max(eligible_ends) == history[
        "last_eligible_pressure_bin_end_seconds_relative_to_trigger"
    ]
    assert max(eligible_ends) + width < 0
    assert last_considered + width == 0
