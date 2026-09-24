"""MFSM-RE-1: the deterministic economy specified in MFSM_Reference_Economy.md.

This is a restricted theoretical model, not an estimated market simulator.
"""

from dataclasses import dataclass, replace
from math import exp, expm1, isfinite, log1p


TERMINAL_MODES = frozenset({"DEFAULT", "MARGIN_FAILURE"})


def _nonnegative_finite(*values: float) -> None:
    if any(not isfinite(x) or x < 0 for x in values):
        raise ValueError("amounts must be finite and nonnegative")


@dataclass(frozen=True)
class Account:
    cash: float
    units: float

    def __post_init__(self):
        _nonnegative_finite(self.cash, self.units)


@dataclass(frozen=True)
class Parameters:
    value: float
    impact: float
    inventory_limit: float
    maintenance: float = 0.25
    restore: float = 0.30
    buyer_speed: float = 20.0
    delay: int = 2
    deadline: int = 10
    currency_tolerance: float = 1e-9

    def __post_init__(self):
        _nonnegative_finite(self.value, self.impact, self.inventory_limit,
                            self.buyer_speed, self.currency_tolerance)
        if self.value == 0 or self.currency_tolerance == 0:
            raise ValueError("value and currency tolerance must be positive")
        if not 0 < self.maintenance < self.restore < 1:
            raise ValueError("require 0 < maintenance < restore < 1")
        if type(self.delay) is not int or self.delay < 0:
            raise ValueError("delay must be a nonnegative integer")
        if type(self.deadline) is not int or self.deadline < 1:
            raise ValueError("deadline must be a positive integer")
        if self.impact * self.inventory_limit > 100:
            raise ValueError("impact times inventory limit exceeds numerical domain")


@dataclass(frozen=True)
class State:
    holder: Account
    dealer: Account
    buyer: Account
    debt: float
    signals: tuple[float, ...] = ()
    tick: int = 0
    breach_ticks: int = 0
    mode: str = "NORMAL"

    def __post_init__(self):
        _nonnegative_finite(self.debt, *self.signals)
        if any(g > 1 for g in self.signals):
            raise ValueError("dislocation history must lie in [0, 1]")
        if any(type(n) is not int or n < 0 for n in (self.tick, self.breach_ticks)):
            raise ValueError("tick and breach count must be nonnegative integers")
        if self.mode not in {"NORMAL", "MARGIN", *TERMINAL_MODES}:
            raise ValueError("unknown mode")


@dataclass(frozen=True)
class Transition:
    state: State
    forced_sale: float
    buyer_purchase: float
    mark_before: float
    mark_after: float


def price(state: State, law: Parameters) -> float:
    value = law.value * exp(-law.impact * state.dealer.units)
    if not isfinite(value) or value <= 0:
        raise ValueError("mark outside floating-point domain")
    return value


def headroom(state: State, law: Parameters) -> float:
    return (state.holder.cash + (1 - law.maintenance) * price(state, law)
            * state.holder.units - state.debt)


def equity(state: State, law: Parameters) -> float:
    return state.holder.cash + price(state, law) * state.holder.units - state.debt


def _buy_cost(mark: float, units: float, impact: float) -> float:
    return mark * units if impact == 0 else mark * (expm1(impact * units) / impact)


def _sell_proceeds(mark: float, units: float, impact: float) -> float:
    return mark * units if impact == 0 else mark * (-expm1(-impact * units) / impact)


def _buy_limit(cash: float, mark: float, impact: float) -> float:
    return cash / mark if impact == 0 else log1p(impact * cash / mark) / impact


def _sell_limit(cash: float, mark: float, impact: float) -> float:
    if impact == 0:
        return cash / mark
    fraction = impact * cash / mark
    return float("inf") if fraction >= 1 else -log1p(-fraction) / impact


def step(state: State, law: Parameters) -> Transition:
    """Apply one ordered, cash-constrained transition; terminal modes absorb."""
    if state.dealer.units > law.inventory_limit:
        raise ValueError("initial dealer inventory exceeds its limit")
    if len(state.signals) > law.delay:
        raise ValueError("signal history exceeds the declared delay")
    mark_before = price(state, law)
    if state.mode in TERMINAL_MODES:
        return Transition(state, 0.0, 0.0, mark_before, mark_before)
    if equity(state, law) < -law.currency_tolerance:
        return Transition(replace(state, mode="DEFAULT"), 0.0, 0.0,
                          mark_before, mark_before)

    # Record the observation before either trade. Missing synthetic prehistory is zero.
    signal = -expm1(-law.impact * state.dealer.units)
    delayed = (signal if law.delay == 0 else
               state.signals[0] if len(state.signals) == law.delay else 0.0)
    bought = min(law.buyer_speed * delayed, state.dealer.units,
                 _buy_limit(state.buyer.cash, mark_before, law.impact))
    paid = min(state.buyer.cash, _buy_cost(mark_before, bought, law.impact))
    current = replace(
        state,
        dealer=Account(state.dealer.cash + paid, state.dealer.units - bought),
        buyer=Account(state.buyer.cash - paid, state.buyer.units + bought),
    )

    mark = price(current, law)
    sold = 0.0
    if headroom(current, law) < -law.currency_tolerance:
        restore_gap = (current.debt - current.holder.cash
                       - (1 - law.restore) * mark * current.holder.units)
        requested = min(current.holder.units, max(0.0, restore_gap) / (law.restore * mark))
        sold = min(requested, max(0.0, law.inventory_limit - current.dealer.units),
                   _sell_limit(current.dealer.cash, mark, law.impact))
        proceeds = min(current.dealer.cash, _sell_proceeds(mark, sold, law.impact))
        current = replace(
            current,
            holder=Account(current.holder.cash + proceeds, current.holder.units - sold),
            dealer=Account(current.dealer.cash - proceeds, current.dealer.units + sold),
        )

    breach_ticks = (state.breach_ticks + 1
                    if headroom(current, law) < -law.currency_tolerance else 0)
    if equity(current, law) < -law.currency_tolerance:
        mode = "DEFAULT"
    elif breach_ticks >= law.deadline:
        mode = "MARGIN_FAILURE"
    else:
        mode = "MARGIN" if breach_ticks else "NORMAL"
    history = (state.signals + (signal,))[-law.delay:] if law.delay else ()
    current = replace(current, signals=history, tick=state.tick + 1,
                      breach_ticks=breach_ticks, mode=mode)
    return Transition(current, sold, bought, mark_before, price(current, law))
