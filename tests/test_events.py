from decimal import Decimal

from mfsm_e001.events import CompositePoint, SpotTick, build_composite, detect_events


def point(second, price):
    return CompositePoint(second, None if price is None else Decimal(str(price)), second * 1000)


def test_two_constituents_required_and_late_trade_cannot_change_history():
    ticks = [
        SpotTick("bybit", 1000, 1000, Decimal("100")),
        SpotTick("binance", 1000, 1000, Decimal("102")),
        SpotTick("bybit", 2000, 3000, Decimal("90")),
        SpotTick("binance", 2000, 2000, Decimal("104")),
    ]
    rows = build_composite(ticks, start_s=1, end_s=3)
    assert [x.price for x in rows] == [Decimal("101"), Decimal("102"), Decimal("97")]


def test_missing_second_constituent_invalidates_composite():
    rows = build_composite([SpotTick("bybit", 1000, 1000, Decimal("100"))], start_s=1, end_s=3)
    assert [x.price for x in rows] == [None, None, None]


def test_crossing_lockout_and_exact_two_hour_boundary():
    prices = [point(s, 100) for s in range(0, 7602)]
    prices[300] = point(300, 99.5)
    prices[301] = point(301, 99)
    prices[400] = point(400, 100)
    prices[401] = point(401, 98.5)
    prices[7500] = point(7500, 100)
    prices[7501] = point(7501, 98.5)
    events = detect_events(prices)
    assert [(x.trigger_s, x.accepted, x.reason) for x in events] == [
        (301, True, "accepted"),
        (401, False, "episode_lockout"),
        (7501, True, "accepted"),
    ]
    assert events[0].decision_s == 316


def test_invalid_return_endpoint_does_not_create_crossing():
    prices = [point(s, 100) for s in range(0, 303)]
    prices[0] = point(0, None)
    prices[301] = point(301, 98)
    assert detect_events(prices) == []


def test_outcomes_after_decision_do_not_change_event_history():
    prices = [point(s, 100) for s in range(0, 330)]
    prices[301] = point(301, 98)
    first = [x for x in detect_events(prices) if x.accepted]
    prices[320] = point(320, 70)
    assert [x for x in detect_events(prices) if x.accepted] == first
