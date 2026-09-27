"""Public-tape strategies for MFSM-SIM-EDGE. None of them can see hidden state."""

from statistics import fmean

from .harness import Strategy, TradeSpec
from .world import PublicRow


def tape_features(tape: tuple[PublicRow, ...], spec: TradeSpec, baseline: int = 40) -> dict:
    """Causal summaries of the tape at the decision row."""
    w = spec.trigger_window
    recent = tape[-w:]
    before = tape[-(w + baseline):-w] or tape[:1]
    base_volume = fmean(row.volume for row in before) or 1e-12
    drop = tape[-1].mark / tape[-1 - w].mark - 1
    sell_flow = -sum(row.signed_volume for row in recent)
    return {
        "drop": drop,
        "volume_ratio": sum(row.volume for row in recent) / (w * base_volume),
        "sell_flow": sell_flow,
        "sell_flow_ratio": sell_flow / (w * base_volume),
        # Units of net selling per 1% of decline: near zero for trade-less repricing.
        "flow_per_drop": sell_flow / max(1e-9, -100 * drop),
        "last_return": tape[-1].mark / tape[-2].mark - 1,
    }


class Flat(Strategy):
    name = "S0_flat"

    def decide(self, tape, spec):
        return 0


class BuyDip(Strategy):
    name = "S1_buy_dip"

    def decide(self, tape, spec):
        return 1


class SellDip(Strategy):
    name = "S2_sell_dip"

    def decide(self, tape, spec):
        return -1


class FlowRule(Strategy):
    """Buy when the decline came with heavy net selling, sell when it came without.

    Heavy net selling suggests forced or exogenous flow (reverting); a decline
    with little net selling suggests repricing on information (persistent).
    Thresholds are tuned on development seeds only.
    """

    name = "S3_flow_rule"

    def __init__(self, buy_above: float = 3.0, sell_below: float | None = 0.5):
        self.buy_above = buy_above
        self.sell_below = sell_below

    def decide(self, tape, spec):
        features = tape_features(tape, spec)
        if features["flow_per_drop"] >= self.buy_above:
            return 1
        if self.sell_below is not None and features["flow_per_drop"] <= self.sell_below:
            return -1
        return 0
