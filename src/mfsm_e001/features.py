"""Causal L2 price-level features and shared Experiment 001 representation."""

from decimal import Decimal
from statistics import median

from .data import BookUpdate, DataError, Liquidation, Trade


def _mid(bids: dict[Decimal, Decimal], asks: dict[Decimal, Decimal]) -> Decimal | None:
    bid = max((price for price, size in bids.items() if size > 0), default=None)
    ask = min((price for price, size in asks.items() if size > 0), default=None)
    if bid is None or ask is None or bid >= ask:
        return None
    return (bid + ask) / 2


def _bid_depth(bids: dict[Decimal, Decimal], asks: dict[Decimal, Decimal]) -> Decimal | None:
    mid = _mid(bids, asks)
    if mid is None:
        return None
    return sum((p * q for p, q in bids.items()
                if mid * (1 - Decimal("0.0025")) <= p <= mid), Decimal(0))


def _replay(updates: list[BookUpdate], decision_ms: int):
    eligible = sorted((u for u in updates if u.event_ms <= decision_ms and u.received_ms <= decision_ms),
                      key=lambda u: (u.event_ms, u.sequence))
    bids: dict[Decimal, Decimal] = {}
    asks: dict[Decimal, Decimal] = {}
    states = []
    initialized = False
    previous = None
    for update in eligible:
        if update.source_gap and update.kind == "delta":
            bids.clear()
            asks.clear()
            initialized = False
            states.append((update, {}, {}, []))
            previous = update
            continue
        if previous is not None and update.kind == "delta":
            if update.sequence <= previous.sequence or update.update_id <= previous.update_id:
                raise DataError("nonmonotonic book update")
        if update.kind == "snapshot":
            bids.clear()
            asks.clear()
            initialized = True
        elif not initialized:
            continue
        changes = []
        for side, incoming in ((bids, update.bids), (asks, update.asks)):
            for price, size in incoming:
                old = side.get(price, Decimal(0))
                delta = size - old
                if size == 0:
                    side.pop(price, None)
                else:
                    side[price] = size
                if side is bids and delta and update.kind == "delta":
                    changes.append((price, delta))
        states.append((update, dict(bids), dict(asks), changes))
        previous = update
    return states if initialized else None


def _persistent_from_states(states, decision_ms: int) -> Decimal | None:
    left = decision_ms - 15_000
    if not states or not any(u.kind == "snapshot" and u.event_ms <= left for u, *_ in states):
        return None
    if any((u.source_gap or (u.kind == "snapshot" and u.event_ms > left))
           and left <= u.event_ms <= decision_ms for u, *_ in states):
        return None
    total = Decimal(0)
    for idx, (update, bids, asks, changes) in enumerate(states):
        if not (left <= update.event_ms <= decision_ms - 1000):
            continue
        mid = _mid(bids, asks)
        if mid is None:
            continue
        lower = mid * (1 - Decimal("0.0025"))
        for price, delta in changes:
            if delta <= 0 or not lower <= price <= mid:
                continue
            endpoint = update.event_ms + 1000
            reductions = sum((-change for later, _, _, later_changes in states[idx + 1:]
                              if update.event_ms < later.event_ms <= endpoint
                              for later_price, change in later_changes
                              if later_price == price and change < 0), Decimal(0))
            credited = max(Decimal(0), delta - reductions)
            endpoint_state = max((state for state in states if state[0].event_ms <= endpoint),
                                 key=lambda state: state[0].event_ms)
            end_mid = _mid(endpoint_state[1], endpoint_state[2])
            if end_mid is None or not end_mid * (1 - Decimal("0.0025")) <= price <= end_mid:
                continue
            total += price * credited
    return total / 15


def persistent_bid_additions(updates: list[BookUpdate], *, decision_ms: int) -> Decimal | None:
    """Observed additions surviving one second, divided by the full 15-second window."""
    states = _replay(updates, decision_ms)
    return None if states is None else _persistent_from_states(states, decision_ms)


def pre_event_depth_median(updates: list[BookUpdate], *, trigger_ms: int) -> Decimal | None:
    """Median visible bid depth on the 1800 whole seconds before the trigger."""
    if trigger_ms % 1000:
        raise ValueError("trigger must lie on the canonical one-second grid")
    left = trigger_ms - 1_800_000
    states = _replay(updates, trigger_ms - 1)
    if not states or not any(u.kind == "snapshot" and u.event_ms <= left for u, *_ in states):
        return None
    if any(u.source_gap and left <= u.event_ms < trigger_ms for u, *_ in states):
        return None
    depths = []
    idx = 0
    current = None
    for ms in range(left, trigger_ms, 1000):
        while idx < len(states) and states[idx][0].event_ms <= ms:
            current = states[idx]
            idx += 1
        if current is None:
            return None
        depth = _bid_depth(current[1], current[2])
        if depth is None:
            return None
        depths.append(depth)
    return median(depths) if depths else None


def neutral_trade_windows(trades: list[Trade], liquidations: list[Liquidation],
                          *, decision_ms: int) -> dict:
    """Shared causal trade summaries; liquidation notional remains unavailable."""
    result = {"aggressive_sell_may_include_liquidations": True}
    for seconds in (1, 5, 15, 30, 60, 300):
        left = decision_ms - seconds * 1000
        sell = sum((t.notional_quote for t in trades if t.taker_side == "Sell"
                    and left < t.event_ms <= decision_ms and t.received_ms <= decision_ms),
                   Decimal(0))
        liq_size = sum((x.base_size for x in liquidations if x.pressure_side == "Sell"
                        and left < x.event_ms <= decision_ms and x.received_ms <= decision_ms),
                       Decimal(0))
        result[f"aggressive_sell_notional_{seconds}s"] = sell
        result[f"liquidation_sell_size_base_{seconds}s"] = liq_size
        result[f"liquidation_sell_notional_{seconds}s"] = None
    return result


def capacity_features(updates: list[BookUpdate], *, decision_ms: int,
                      pre_depth_median: Decimal | None,
                      aggressive_sell_notional: Decimal | None,
                      liquidation_sell_notional: Decimal | None) -> dict:
    """Venue-specific visible-capacity proxy; no claim of causal absorption."""
    states = _replay(updates, decision_ms)
    depth = None
    rate = None
    if states:
        latest, bids, asks, _ = states[-1]
        depth = _bid_depth(bids, asks)
        if depth is not None:
            rate = _persistent_from_states(states, decision_ms)
    floor = pre_depth_median * Decimal("0.01") if pre_depth_median is not None and pre_depth_median > 0 else None
    raw_capacity = depth + 30 * rate if depth is not None and rate is not None else None
    capacity = max(raw_capacity, floor) if raw_capacity is not None and floor is not None else None
    return {
        "visible_bid_depth": depth,
        "replenishment_rate": rate,
        "capacity_floor": floor,
        "capacity_proxy": capacity,
        "low_capacity": raw_capacity <= floor if raw_capacity is not None and floor is not None else None,
        "aggressive_sell_notional": aggressive_sell_notional,
        "liquidation_notional": liquidation_sell_notional,
    }


def split_feature_sets(shared: dict) -> tuple[dict, dict]:
    """MFSM gets only deterministic combinations of the exact shared B4 base."""
    b4 = dict(shared)
    mfsm = dict(shared)
    capacity = shared.get("capacity_proxy")
    sell = shared.get("aggressive_sell_notional")
    liquidation = shared.get("liquidation_notional")
    mfsm["sell_pressure_ratio"] = sell / capacity if sell is not None and capacity else None
    mfsm["liquidation_pressure_ratio"] = liquidation / capacity if liquidation is not None and capacity else None
    return b4, mfsm
