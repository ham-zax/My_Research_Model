"""First-passage outcomes on the independent one-second spot grid."""

from dataclasses import dataclass
from decimal import Decimal

from .events import CompositePoint, Event


@dataclass(frozen=True)
class Label:
    horizon_s: int
    valid: bool
    value: int | None
    state: str | None
    reason: str | None
    first_hit_s: int | None
    available_ms: int | None


def label_event(points: list[CompositePoint], event: Event, *, horizon_s: int) -> Label:
    """Stop at first barrier hit; any preceding invalid grid point voids label."""
    by_second = {point.second: point for point in points}
    decision = by_second.get(event.decision_s)
    if not event.accepted:
        raise ValueError("cannot label a locked-out crossing")
    if decision is None or decision.price is None:
        return Label(horizon_s, False, None, None, "missing_decision_price", None, None)
    lower = decision.price * (1 - Decimal("0.0100"))
    upper = decision.price * (1 + Decimal("0.0075"))
    available_ms = max(event.decision_s * 1000, decision.latest_received_ms or 0)
    for second in range(event.decision_s + 1, event.decision_s + horizon_s + 1):
        point = by_second.get(second)
        if point is None or point.price is None:
            return Label(horizon_s, False, None, None, "missing_price_before_hit", None, None)
        available_ms = max(available_ms, second * 1000, point.latest_received_ms or 0)
        if point.price <= lower:
            return Label(horizon_s, True, 1, "downside-first", None, second, available_ms)
        if point.price >= upper:
            return Label(horizon_s, True, 0, "recovery-first", None, second, available_ms)
    return Label(horizon_s, True, 0, "neither-by-horizon", None, None, available_ms)
