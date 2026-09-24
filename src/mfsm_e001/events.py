"""Receipt-aware independent spot composite and Experiment 001 crossings."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class SpotTick:
    venue: str
    event_ms: int
    received_ms: int
    price: Decimal


@dataclass(frozen=True)
class CompositePoint:
    second: int
    price: Decimal | None
    latest_received_ms: int | None


@dataclass(frozen=True)
class Event:
    trigger_s: int
    decision_s: int
    accepted: bool
    reason: str


def build_composite(ticks: Iterable[SpotTick], *, start_s: int, end_s: int) -> list[CompositePoint]:
    """Two-source equal-weight composite; both trades must be observable and fresh."""
    source = {"bybit": [], "binance": []}
    for tick in ticks:
        if tick.venue not in source:
            raise ValueError("unapproved spot constituent")
        if tick.price <= 0 or tick.received_ms < tick.event_ms:
            raise ValueError("invalid spot tick")
        source[tick.venue].append(tick)
    for values in source.values():
        values.sort(key=lambda x: (x.received_ms, x.event_ms))
    offsets = {"bybit": 0, "binance": 0}
    latest: dict[str, SpotTick | None] = {"bybit": None, "binance": None}
    result = []
    for second in range(start_s, end_s + 1):
        boundary = second * 1000
        selected = []
        for venue in ("bybit", "binance"):
            records = source[venue]
            while offsets[venue] < len(records) and records[offsets[venue]].received_ms <= boundary:
                row = records[offsets[venue]]
                if latest[venue] is None or (row.event_ms, row.received_ms) > (
                        latest[venue].event_ms, latest[venue].received_ms):
                    latest[venue] = row
                offsets[venue] += 1
            row = latest[venue]
            if row is not None and row.event_ms <= boundary and boundary - row.event_ms <= 1000:
                selected.append(row)
        if len(selected) != 2:
            result.append(CompositePoint(second, None, None))
        else:
            result.append(CompositePoint(second, (selected[0].price + selected[1].price) / 2,
                                         max(x.received_ms for x in selected)))
    return result


def detect_events(points: Iterable[CompositePoint]) -> list[Event]:
    """Return accepted crossings and those suppressed by the two-hour lockout."""
    by_second = {point.second: point for point in points}
    events: list[Event] = []
    last_accepted: int | None = None

    def falling(second: int) -> bool | None:
        current, earlier = by_second.get(second), by_second.get(second - 300)
        if not current or not earlier or current.price is None or earlier.price is None:
            return None
        return current.price / earlier.price - 1 <= Decimal("-0.0100")

    for second in sorted(by_second):
        now, before = falling(second), falling(second - 1)
        if now is True and before is False:
            accepted = last_accepted is None or second >= last_accepted + 7200
            events.append(Event(second, second + 15, accepted,
                                "accepted" if accepted else "episode_lockout"))
            if accepted:
                last_accepted = second
    return events
