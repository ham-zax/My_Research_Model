"""One-step public observability for the existing MFSM-RE-1 transition.

The restricted observer sees only the pre-intervention mark from ``price``.
``economy.observe_limited`` is a different, richer map and is not used here.
Maintenance headroom is available only as a privileged diagnostic.
"""

from dataclasses import dataclass, replace
from math import isfinite

from mfsm_reference.economy import Parameters, State, headroom, price, step


NOT_IDENTIFIED = "not_identified"
INVARIANT_WITHIN_DECLARED_CANDIDATES = "invariant_within_declared_candidates"
INCOMPATIBLE_OBSERVATION = "incompatible_observation"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    state: State
    law: Parameters


@dataclass(frozen=True)
class PublicObservation:
    """Pre-intervention mark. No hidden state and no post-shock value."""

    mark: float


@dataclass(frozen=True)
class PrivilegedDiagnostic:
    """Headroom-enhanced pre-intervention reading. Not public data."""

    mark: float
    headroom: float


@dataclass(frozen=True)
class OracleResponse:
    candidate_id: str
    pre_intervention_mark: float
    pre_intervention_headroom: float
    next_mark: float
    forced_sale: float
    forced_sale_occurred: bool
    mode: str


@dataclass(frozen=True)
class ObserverEnvelope:
    observed_mark: float
    compatible_candidate_count: int
    compatible_candidate_ids: tuple[str, ...]
    minimum_next_mark: float | None
    maximum_next_mark: float | None
    possible_forced_sale_outcomes: tuple[bool, ...]
    status: str
    witness_ids: tuple[str, str] | None


def _positive_tolerance(tolerance: float) -> float:
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        raise ValueError("comparison tolerance must be a positive finite number")
    if not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("comparison tolerance must be a positive finite number")
    return float(tolerance)


def _finite_number(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    if not isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def public_observation(state: State, law: Parameters) -> PublicObservation:
    """Return the only public pre-intervention observation."""
    return PublicObservation(price(state, law))


def privileged_diagnostic(state: State, law: Parameters) -> PrivilegedDiagnostic:
    """Return mark plus maintenance headroom. This is not a public observation."""
    return PrivilegedDiagnostic(price(state, law), headroom(state, law))


def apply_benchmark_shock(law: Parameters, *, pre_shock_value: float,
                          post_shock_value: float) -> Parameters:
    """Apply the declared benchmark change. This does not read a public signal."""
    pre_shock_value = _finite_number(pre_shock_value, "pre-shock benchmark")
    post_shock_value = _finite_number(post_shock_value, "post-shock benchmark")
    if law.value != pre_shock_value:
        raise ValueError("candidate benchmark is not the named pre-shock value")
    if post_shock_value <= 0 or post_shock_value >= pre_shock_value:
        raise ValueError("named shock must lower the benchmark and keep it positive")
    return replace(law, value=post_shock_value)


def oracle_response(candidate: Candidate, *, pre_shock_value: float,
                    post_shock_value: float, tolerance: float) -> OracleResponse:
    """Apply the named shock to a fully known state and law, then step once."""
    tolerance = _positive_tolerance(tolerance)
    shocked = apply_benchmark_shock(
        candidate.law, pre_shock_value=pre_shock_value, post_shock_value=post_shock_value)
    transition = step(candidate.state, shocked)
    return OracleResponse(
        candidate.candidate_id,
        public_observation(candidate.state, candidate.law).mark,
        privileged_diagnostic(candidate.state, candidate.law).headroom,
        transition.mark_after,
        transition.forced_sale,
        transition.forced_sale > tolerance,
        transition.state.mode,
    )


def compatible_candidates(candidates: tuple[Candidate, ...] | list[Candidate],
                          observed_mark: float, tolerance: float) -> tuple[Candidate, ...]:
    """Keep declared candidates whose public pre-shock mark matches."""
    tolerance = _positive_tolerance(tolerance)
    observed_mark = _finite_number(observed_mark, "observed mark")
    return tuple(
        candidate for candidate in candidates
        if abs(public_observation(candidate.state, candidate.law).mark - observed_mark)
        <= tolerance
    )


def compatible_with_privileged_diagnostic(
        candidates: tuple[Candidate, ...] | list[Candidate], observed_mark: float,
        observed_headroom: float, tolerance: float) -> tuple[Candidate, ...]:
    """Restrict the public matches by pre-shock headroom. This cannot add candidates."""
    tolerance = _positive_tolerance(tolerance)
    observed_headroom = _finite_number(observed_headroom, "privileged headroom")
    return tuple(
        candidate for candidate in compatible_candidates(candidates, observed_mark, tolerance)
        if abs(privileged_diagnostic(candidate.state, candidate.law).headroom
               - observed_headroom) <= tolerance
    )


def _responses_disagree(left: OracleResponse, right: OracleResponse,
                        tolerance: float) -> bool:
    return (abs(left.next_mark - right.next_mark) > tolerance
            or left.forced_sale_occurred != right.forced_sale_occurred)


def observer_envelope(candidates: tuple[Candidate, ...] | list[Candidate],
                      observed_mark: float, *, pre_shock_value: float,
                      post_shock_value: float, tolerance: float) -> ObserverEnvelope:
    """Summarize one-step responses of candidates compatible with the public mark.

    Agreement is invariance inside that declared compatible set. It is not a
    claim that the response is identified for any wider set of economies.
    """
    tolerance = _positive_tolerance(tolerance)
    matched = compatible_candidates(candidates, observed_mark, tolerance)
    if not matched:
        return ObserverEnvelope(
            _finite_number(observed_mark, "observed mark"), 0, (), None, None, (),
            INCOMPATIBLE_OBSERVATION, None)
    responses = tuple(
        oracle_response(candidate, pre_shock_value=pre_shock_value,
                        post_shock_value=post_shock_value, tolerance=tolerance)
        for candidate in matched
    )
    witness = None
    status = INVARIANT_WITHIN_DECLARED_CANDIDATES
    for index, left in enumerate(responses):
        for right in responses[index + 1:]:
            if _responses_disagree(left, right, tolerance):
                witness = (left.candidate_id, right.candidate_id)
                status = NOT_IDENTIFIED
                break
        if witness is not None:
            break
    marks = tuple(response.next_mark for response in responses)
    outcomes = tuple(sorted({response.forced_sale_occurred for response in responses}))
    return ObserverEnvelope(
        _finite_number(observed_mark, "observed mark"),
        len(matched),
        tuple(candidate.candidate_id for candidate in matched),
        min(marks),
        max(marks),
        outcomes,
        status,
        witness,
    )
