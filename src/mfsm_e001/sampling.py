"""Conservative episode eligibility when a sample lacks preceding trigger history."""

from collections import deque
from decimal import Decimal

from .events import CompositePoint


def audit_episode_history(points: list[CompositePoint]) -> dict:
    """Track possible lockout states without asserting that unseen history was quiet.

    Each missing comparison may or may not hide a crossing. Possible active last
    accepted times are retained; expired times collapse to one ready state. This
    overapproximates physically possible price paths, so an 'ambiguous' result is
    conservative. An accepted result is valid under every retained history.
    """
    if not points:
        return {"unknown_crossing_seconds": 0, "crossings": []}
    prices = {point.second: point.price for point in points}
    if len(prices) != len(points):
        raise ValueError("duplicate grid second")
    start, end = min(prices), max(prices)
    active = deque(range(start - 7199, start))
    ready = True  # There may also have been no recent accepted episode.
    crossings = []
    unknown = 0

    def falling(second):
        current, earlier = prices.get(second), prices.get(second - 300)
        if current is None or earlier is None:
            return None
        return current / earlier - 1 <= Decimal("-0.0100")

    before = falling(start - 1)
    for second in range(start, end + 1):
        while active and active[0] <= second - 7200:
            active.popleft()
            ready = True
        now = falling(second)
        if now is False or before is True:
            crossing = False
        elif now is True and before is False:
            crossing = True
        else:
            crossing = None
        before = now
        if crossing is True:
            status = ("accepted_with_observed_lockout" if ready and not active else
                      "ambiguous_lockout_history" if ready else "locked_out")
            crossings.append({"trigger_s": second, "status": status,
                              "possible_prior_lockout_states": len(active) + int(ready)})
            if ready:
                active.append(second)
                ready = False
        elif crossing is None:
            unknown += 1
            if ready:
                # A crossing could start an episode, or there could be no crossing.
                active.append(second)
    return {"unknown_crossing_seconds": unknown, "crossings": crossings}
