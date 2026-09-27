"""MFSM-SIM-1: a stochastic, multi-holder extension of MFSM-RE-1.

See docs/mfsm_sim_edge_plan.md. The execution integrals and sizing rules are the
MFSM-RE-1 functions, evaluated with the dealer quote anchor ``u`` in place of
the benchmark and with effective inventory ``q_D - q_ref``. In the declared
limit (one holder, no value noise or news, instant anchor, ``q_ref = 0``, no
noise, dump or outside trader, freeze on holder failure) every step equals
``mfsm_reference.economy.step`` exactly. Randomness enters only through draws
passed to ``step``, so paired runs share random numbers.

This is a synthetic, uncalibrated member. It is not a market simulator.
"""

from dataclasses import dataclass, replace
from math import exp, expm1, isfinite

from mfsm_reference.economy import (
    Account,
    Parameters,
    TERMINAL_MODES,
    _buy_cost,
    _buy_limit,
    _sell_limit,
    _sell_proceeds,
)


@dataclass(frozen=True)
class WorldLaw:
    """Structural law. ``base.value`` is ignored; value lives in the state."""

    base: Parameters
    value_volatility: float = 0.0
    anchor_speed: float = 1.0
    reference_inventory: float = 0.0
    noise_scale: float = 0.0
    terminal_liquidation: bool = True
    freeze_when_all_terminal: bool = False
    shock_tick: int | None = None
    news_size: float = 0.0
    dump_units: float = 0.0

    def __post_init__(self):
        values = (self.value_volatility, self.anchor_speed,
                  self.reference_inventory, self.noise_scale,
                  self.news_size, self.dump_units)
        if any(not isfinite(x) or x < 0 for x in values):
            raise ValueError("world parameters must be finite and nonnegative")
        if not 0 < self.anchor_speed <= 1:
            raise ValueError("anchor speed must lie in (0, 1]")
        if self.reference_inventory > self.base.inventory_limit:
            raise ValueError("reference inventory exceeds the dealer limit")
        if (self.base.impact_curve == "hyperbolic"
                and self.base.impact * self.reference_inventory >= 1):
            raise ValueError("hyperbolic curve needs impact * reference inventory < 1")
        if self.shock_tick is not None and (type(self.shock_tick) is not int
                                            or self.shock_tick < 0):
            raise ValueError("shock tick must be a nonnegative integer")
        if self.base.delay_weights is not None:
            raise ValueError("distributed delay is not yet supported in MFSM-SIM-1")


@dataclass(frozen=True)
class Holder:
    account: Account
    debt: float
    breach_ticks: int = 0
    mode: str = "NORMAL"


@dataclass(frozen=True)
class World:
    """Closed state. Everything except the published tape is hidden."""

    value: float
    anchor: float
    dealer: Account
    buyer: Account
    holders: tuple[Holder, ...]
    noise: Account
    dumper: Account
    trader: Account
    signals: tuple[float, ...] = ()
    tick: int = 0


@dataclass(frozen=True)
class Draws:
    """Per-tick random inputs, drawn independently of the path."""

    value_shock: float = 0.0
    noise_order: float = 0.0


@dataclass(frozen=True)
class PublicRow:
    tick: int
    mark: float
    volume: float
    signed_volume: float


@dataclass(frozen=True)
class TickRecord:
    public: PublicRow
    mark_before: float
    buyer_purchase: float
    noise_trade: float
    dump_sale: float
    trader_trade: float
    holder_sales: tuple[float, ...]
    value: float
    anchor: float


def _local_law(world: World, law: WorldLaw) -> Parameters:
    return law.base if law.base.value == world.anchor else replace(law.base, value=world.anchor)


def effective_inventory(world: World, law: WorldLaw) -> float:
    return world.dealer.units - law.reference_inventory


def mark(world: World, law: WorldLaw) -> float:
    base = law.base
    inventory = effective_inventory(world, law)
    if base.impact_curve == "exponential":
        value = world.anchor * exp(-base.impact * inventory)
    else:
        value = world.anchor / (1 + base.impact * inventory)
    if not isfinite(value) or value <= 0:
        raise ValueError("mark outside floating-point domain")
    return value


def holder_headroom(holder: Holder, price: float, law: WorldLaw) -> float:
    return (holder.account.cash + (1 - law.base.maintenance) * price
            * holder.account.units - holder.debt)


def holder_equity(holder: Holder, price: float) -> float:
    return holder.account.cash + price * holder.account.units - holder.debt


def _dislocation(world: World, law: WorldLaw, price: float) -> float:
    base = law.base
    if world.anchor == world.value:
        raw = (1 - price / world.value if base.impact_curve == "hyperbolic"
               else -expm1(-base.impact * effective_inventory(world, law)))
    else:
        raw = 1 - price / world.value
    # Signed: negative when the mark is above value (never in the RE-1 limit).
    return raw


def _delayed_signal(world: World, law: WorldLaw, current: float) -> float:
    lag = law.base.delay
    return (current if lag == 0 else
            world.signals[-lag] if len(world.signals) >= lag else 0.0)


def _buy_from_dealer(world, law, buyer: Account, desired: float):
    """Fill a purchase of up to ``desired`` units; return (world, buyer, units, cash)."""
    if desired <= 0:
        return world, buyer, 0.0, 0.0
    price = mark(world, law)
    local = _local_law(world, law)
    inventory = effective_inventory(world, law)
    bought = min(desired, world.dealer.units,
                 _buy_limit(buyer.cash, price, local, inventory))
    paid = min(buyer.cash, _buy_cost(price, bought, local, inventory))
    world = replace(world, dealer=Account(world.dealer.cash + paid,
                                          world.dealer.units - bought))
    return world, Account(buyer.cash - paid, buyer.units + bought), bought, paid


def _sell_to_dealer(world, law, seller: Account, desired: float):
    """Fill a sale of up to ``desired`` units; return (world, seller, units, cash)."""
    if desired <= 0:
        return world, seller, 0.0, 0.0
    price = mark(world, law)
    local = _local_law(world, law)
    inventory = effective_inventory(world, law)
    room = max(0.0, law.base.inventory_limit - world.dealer.units)
    sold = min(desired, seller.units, room,
               _sell_limit(world.dealer.cash, price, local, inventory, room))
    proceeds = min(world.dealer.cash, _sell_proceeds(price, sold, local, inventory))
    world = replace(world, dealer=Account(world.dealer.cash - proceeds,
                                          world.dealer.units + sold))
    return world, Account(seller.cash + proceeds, seller.units - sold), sold, proceeds


def _restore_request(holder: Holder, price: float, law: WorldLaw) -> float:
    base = law.base
    if base.liquidation_rule == "fixed_lot":
        return min(holder.account.units, base.lot_units)
    gap = (holder.debt - holder.account.cash
           - (1 - base.restore) * price * holder.account.units)
    return min(holder.account.units, max(0.0, gap) / (base.restore * price))


def step(world: World, law: WorldLaw, draws: Draws = Draws(),
         trader_order: float = 0.0) -> tuple[World, TickRecord]:
    """Advance one tick. ``trader_order`` > 0 buys, < 0 sells, in asset units."""
    base = law.base
    tolerance = base.currency_tolerance
    if world.dealer.units > base.inventory_limit:
        raise ValueError("dealer inventory exceeds its limit")
    if len(world.signals) > base.delay:
        raise ValueError("signal history exceeds the declared delay")
    mark_before = mark(world, law)

    # 1. Start-of-tick default checks, per holder (MFSM-RE-1 step 1).
    holders = tuple(
        replace(h, mode="DEFAULT")
        if h.mode not in TERMINAL_MODES and holder_equity(h, mark_before) < -tolerance
        else h
        for h in world.holders)
    if law.freeze_when_all_terminal and all(h.mode in TERMINAL_MODES for h in holders):
        frozen = replace(world, holders=holders)
        return frozen, TickRecord(
            PublicRow(world.tick, mark_before, 0.0, 0.0), mark_before, 0.0, 0.0,
            0.0, 0.0, tuple(0.0 for _ in holders), world.value, world.anchor)
    world = replace(world, holders=holders)

    # 2. Hidden value and dealer quote anchor.
    value = world.value
    if law.value_volatility:
        value *= exp(law.value_volatility * draws.value_shock)
    shock_now = law.shock_tick is not None and world.tick == law.shock_tick
    if shock_now and law.news_size:
        if law.news_size >= value:
            raise ValueError("news size would make value nonpositive")
        value -= law.news_size
    anchor = (value if law.anchor_speed == 1
              else world.anchor + law.anchor_speed * (value - world.anchor))
    world = replace(world, value=value, anchor=anchor)

    volume = signed = 0.0

    # 3. Scheduled exogenous dump (value unchanged).
    dumped = 0.0
    if shock_now and law.dump_units:
        world, dumper, dumped, _ = _sell_to_dealer(world, law, world.dumper, law.dump_units)
        world = replace(world, dumper=dumper)
        volume += dumped
        signed -= dumped

    # 4. Outside trader, decided from the tape up to the previous tick.
    traded = 0.0
    if trader_order > 0:
        world, trader, traded, _ = _buy_from_dealer(world, law, world.trader, trader_order)
    elif trader_order < 0:
        world, trader, sold, _ = _sell_to_dealer(world, law, world.trader, -trader_order)
        traded = -sold
    if trader_order:
        world = replace(world, trader=trader)
        volume += abs(traded)
        signed += traded

    # 5. Delayed informed trader (MFSM-RE-1 steps 2-3). It buys below value
    # and, outside the RE-1 limit, sells inventory it holds above value.
    signal = _dislocation(world, law, mark(world, law))
    desired = base.buyer_speed * _delayed_signal(world, law, signal)
    if desired >= 0:
        world, buyer, bought, _ = _buy_from_dealer(world, law, world.buyer, desired)
    else:
        world, buyer, sold, _ = _sell_to_dealer(world, law, world.buyer, -desired)
        bought = -sold
    world = replace(world, buyer=buyer)
    volume += abs(bought)
    signed += bought

    # 6. Two-sided noise flow.
    noise_trade = 0.0
    order = law.noise_scale * draws.noise_order
    if order > 0:
        world, noise, noise_trade, _ = _buy_from_dealer(world, law, world.noise, order)
    elif order < 0:
        world, noise, sold, _ = _sell_to_dealer(world, law, world.noise, -order)
        noise_trade = -sold
    if order:
        world = replace(world, noise=noise)
        volume += abs(noise_trade)
        signed += noise_trade

    # 7. Holder margin processing in fixed index order (MFSM-RE-1 steps 4-6).
    updated = []
    sales = []
    for holder in world.holders:
        price = mark(world, law)
        if holder.mode in TERMINAL_MODES:
            request = holder.account.units if law.terminal_liquidation else 0.0
        elif holder_headroom(holder, price, law) < -tolerance:
            request = _restore_request(holder, price, law)
        else:
            request = 0.0
        world, account, sold, _ = _sell_to_dealer(world, law, holder.account, request)
        holder = replace(holder, account=account)
        sales.append(sold)
        volume += sold
        signed -= sold
        if holder.mode not in TERMINAL_MODES:
            price = mark(world, law)
            breach = (holder.breach_ticks + 1
                      if holder_headroom(holder, price, law) < -tolerance else 0)
            if holder_equity(holder, price) < -tolerance:
                mode = "DEFAULT"
            elif breach >= base.deadline:
                mode = "MARGIN_FAILURE"
            else:
                mode = "MARGIN" if breach else "NORMAL"
            holder = replace(holder, breach_ticks=breach, mode=mode)
        updated.append(holder)

    # 8. Publish, remember the start-of-buyer dislocation, advance.
    history = (world.signals + (signal,))[-base.delay:] if base.delay else ()
    world = replace(world, holders=tuple(updated), signals=history, tick=world.tick + 1)
    after = mark(world, law)
    record = TickRecord(PublicRow(world.tick, after, volume, signed), mark_before,
                        bought, noise_trade, dumped, traded, tuple(sales),
                        world.value, world.anchor)
    return world, record
