"""Public pre-shock history adapter for the unchanged MFSM-RE-1 economy.

This module is separate from :mod:`mfsm_reference.observation` so the frozen
MFSM-RE-OBS-1 mark-only interface remains unchanged. Public traces contain only
marks and, for P2, anonymous total executed units observed after completed
pre-shock transitions. Candidate identity, benchmark path, balances, debt,
inventory, trade attribution, headroom, and all post-shock values stay oracle
metadata.
"""

from dataclasses import dataclass, replace
from math import isfinite
from typing import Iterable, Sequence

from mfsm_reference.economy import Parameters, State, headroom, price, step
from mfsm_reference.observation import (
    INCOMPATIBLE_OBSERVATION,
    INVARIANT_WITHIN_DECLARED_CANDIDATES,
    NOT_IDENTIFIED,
    Candidate,
    apply_benchmark_shock,
)


P0 = "P0"
P1 = "P1"
P2 = "P2"
PUBLIC_MAPS = frozenset({P0, P1, P2})


@dataclass(frozen=True)
class PublicHistoryTrace:
    """One public pre-shock trace with no candidate or path identity."""

    marks: tuple[float, ...]
    total_executed_units: tuple[float, ...] | None = None


@dataclass(frozen=True)
class HistoryCase:
    """Oracle-owned simulated prelude and its final pre-shock state."""

    opaque_id: str
    candidate_id: str
    prelude_id: str
    initial_state: State
    initial_law: Parameters
    final_state: State
    final_law: Parameters
    initial_mark: float
    post_transition_marks: tuple[float, ...]
    total_executed_units: tuple[float, ...]
    forced_sales: tuple[float, ...]
    buyer_purchases: tuple[float, ...]
    modes: tuple[str, ...]


@dataclass(frozen=True)
class HistoryResponse:
    """Oracle one-step response after the named shock."""

    opaque_id: str
    pre_shock_mark: float
    pre_shock_headroom: float
    next_mark: float
    forced_sale: float
    forced_sale_occurred: bool
    mode: str


@dataclass(frozen=True)
class HistoryEnvelope:
    """Response span over histories compatible with one public trace."""

    compatible_history_count: int
    compatible_history_ids: tuple[str, ...]
    minimum_next_mark: float | None
    maximum_next_mark: float | None
    possible_forced_sale_outcomes: tuple[bool, ...]
    status: str
    witness_ids: tuple[str, str] | None


def _positive_number(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a positive finite number")
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be a positive finite number")
    return float(value)


def _finite_number(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    if not isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def _validate_trace(trace: PublicHistoryTrace) -> None:
    if not trace.marks:
        raise ValueError("public trace must contain at least one mark")
    for mark in trace.marks:
        _finite_number(mark, "public mark")
    if trace.total_executed_units is None:
        return
    if len(trace.total_executed_units) != len(trace.marks) - 1:
        raise ValueError("volume history must have one entry per completed transition")
    for units in trace.total_executed_units:
        units = _finite_number(units, "public total executed units")
        if units < 0:
            raise ValueError("public total executed units must be nonnegative")


def simulate_prelude(
    candidate: Candidate,
    *,
    opaque_id: str,
    prelude_id: str,
    benchmark_values: Iterable[float],
) -> HistoryCase:
    """Apply a fixed benchmark prelude causally and retain public post-step data."""

    if not opaque_id or not prelude_id:
        raise ValueError("history and prelude ids must be nonempty")
    values = tuple(
        _positive_number(value, "prelude benchmark") for value in benchmark_values
    )
    if not values:
        raise ValueError("prelude must contain at least one transition")

    state = candidate.state
    law = candidate.law
    initial_mark = price(state, law)
    marks: list[float] = []
    totals: list[float] = []
    forced_sales: list[float] = []
    buyer_purchases: list[float] = []
    modes: list[str] = []

    for benchmark in values:
        law = replace(law, value=benchmark)
        transition = step(state, law)
        state = transition.state
        marks.append(transition.mark_after)
        forced_sales.append(transition.forced_sale)
        buyer_purchases.append(transition.buyer_purchase)
        totals.append(transition.forced_sale + transition.buyer_purchase)
        modes.append(transition.state.mode)

    return HistoryCase(
        opaque_id=opaque_id,
        candidate_id=candidate.candidate_id,
        prelude_id=prelude_id,
        initial_state=candidate.state,
        initial_law=candidate.law,
        final_state=state,
        final_law=law,
        initial_mark=initial_mark,
        post_transition_marks=tuple(marks),
        total_executed_units=tuple(totals),
        forced_sales=tuple(forced_sales),
        buyer_purchases=tuple(buyer_purchases),
        modes=tuple(modes),
    )


def public_trace(case: HistoryCase, map_id: str) -> PublicHistoryTrace:
    """Project one oracle history onto a declared public observation map."""

    if map_id == P0:
        trace = PublicHistoryTrace((case.post_transition_marks[-1],))
    elif map_id == P1:
        trace = PublicHistoryTrace((case.initial_mark, *case.post_transition_marks))
    elif map_id == P2:
        trace = PublicHistoryTrace(
            (case.initial_mark, *case.post_transition_marks),
            case.total_executed_units,
        )
    else:
        raise ValueError(f"unknown public observation map: {map_id}")
    _validate_trace(trace)
    return trace


def traces_compatible(
    observed: PublicHistoryTrace,
    possible: PublicHistoryTrace,
    *,
    price_abs_band: float,
    volume_abs_band: float,
) -> bool:
    """Match every public field inside its own absolute observation band."""

    price_abs_band = _positive_number(price_abs_band, "price observation band")
    volume_abs_band = _positive_number(volume_abs_band, "volume observation band")
    _validate_trace(observed)
    _validate_trace(possible)

    if len(observed.marks) != len(possible.marks):
        return False
    if any(
        abs(left - right) > price_abs_band
        for left, right in zip(observed.marks, possible.marks, strict=True)
    ):
        return False
    if (observed.total_executed_units is None) != (
        possible.total_executed_units is None
    ):
        return False
    if observed.total_executed_units is None:
        return True
    if len(observed.total_executed_units) != len(possible.total_executed_units):
        return False
    return all(
        abs(left - right) <= volume_abs_band
        for left, right in zip(
            observed.total_executed_units,
            possible.total_executed_units,
            strict=True,
        )
    )


def compatible_histories(
    cases: Sequence[HistoryCase],
    observed: PublicHistoryTrace,
    *,
    map_id: str,
    price_abs_band: float,
    volume_abs_band: float,
) -> tuple[HistoryCase, ...]:
    """Return possible histories compatible with a public trace in input order."""

    if map_id not in PUBLIC_MAPS:
        raise ValueError(f"unknown public observation map: {map_id}")
    return tuple(
        case
        for case in cases
        if traces_compatible(
            observed,
            public_trace(case, map_id),
            price_abs_band=price_abs_band,
            volume_abs_band=volume_abs_band,
        )
    )


def one_step_response(
    case: HistoryCase,
    *,
    pre_shock_value: float,
    post_shock_value: float,
    sale_occurrence_threshold_units: float,
) -> HistoryResponse:
    """Apply the declared one-step shock to one fully known pre-shock history."""

    sale_occurrence_threshold_units = _positive_number(
        sale_occurrence_threshold_units, "sale occurrence threshold"
    )
    shocked = apply_benchmark_shock(
        case.final_law,
        pre_shock_value=pre_shock_value,
        post_shock_value=post_shock_value,
    )
    transition = step(case.final_state, shocked)
    return HistoryResponse(
        opaque_id=case.opaque_id,
        pre_shock_mark=price(case.final_state, case.final_law),
        pre_shock_headroom=headroom(case.final_state, case.final_law),
        next_mark=transition.mark_after,
        forced_sale=transition.forced_sale,
        forced_sale_occurred=(
            transition.forced_sale > sale_occurrence_threshold_units
        ),
        mode=transition.state.mode,
    )


def responses_disagree(
    left: HistoryResponse,
    right: HistoryResponse,
    *,
    next_mark_abs_tolerance: float,
) -> bool:
    """Compare response values without consulting observation matching bands."""

    next_mark_abs_tolerance = _positive_number(
        next_mark_abs_tolerance, "next-mark response tolerance"
    )
    return (
        abs(left.next_mark - right.next_mark) > next_mark_abs_tolerance
        or left.forced_sale_occurred != right.forced_sale_occurred
    )


def observer_envelope(
    cases: Sequence[HistoryCase],
    observed: PublicHistoryTrace,
    *,
    map_id: str,
    price_abs_band: float,
    volume_abs_band: float,
    pre_shock_value: float,
    post_shock_value: float,
    next_mark_abs_tolerance: float,
    sale_occurrence_threshold_units: float,
) -> HistoryEnvelope:
    """Summarize one-step responses over histories matching one public trace."""

    matched = compatible_histories(
        cases,
        observed,
        map_id=map_id,
        price_abs_band=price_abs_band,
        volume_abs_band=volume_abs_band,
    )
    if not matched:
        return HistoryEnvelope(
            compatible_history_count=0,
            compatible_history_ids=(),
            minimum_next_mark=None,
            maximum_next_mark=None,
            possible_forced_sale_outcomes=(),
            status=INCOMPATIBLE_OBSERVATION,
            witness_ids=None,
        )

    responses = tuple(
        one_step_response(
            case,
            pre_shock_value=pre_shock_value,
            post_shock_value=post_shock_value,
            sale_occurrence_threshold_units=sale_occurrence_threshold_units,
        )
        for case in matched
    )
    witness = None
    status = INVARIANT_WITHIN_DECLARED_CANDIDATES
    for index, left in enumerate(responses):
        for right in responses[index + 1 :]:
            if responses_disagree(
                left,
                right,
                next_mark_abs_tolerance=next_mark_abs_tolerance,
            ):
                witness = (left.opaque_id, right.opaque_id)
                status = NOT_IDENTIFIED
                break
        if witness is not None:
            break

    marks = tuple(response.next_mark for response in responses)
    outcomes = tuple(
        sorted({response.forced_sale_occurred for response in responses})
    )
    return HistoryEnvelope(
        compatible_history_count=len(matched),
        compatible_history_ids=tuple(case.opaque_id for case in matched),
        minimum_next_mark=min(marks),
        maximum_next_mark=max(marks),
        possible_forced_sale_outcomes=outcomes,
        status=status,
        witness_ids=witness,
    )
