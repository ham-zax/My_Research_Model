"""Timing checks for the separately versioned free BTC flow screen."""

import json
from pathlib import Path
import sys

from mfsm_free_flow.study import scan_rows, timestamp_second


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_mfsm_free_btc_flow import evaluate


PROTOCOL = json.loads((ROOT / "experiments/mfsm_free_btc_flow_001_protocol.json").read_text())


def _bars(*, future_price=97.0, missing_second=None):
    for second in range(2117):
        if second == missing_second:
            continue
        close = 100.0 if second < 301 else 98.9
        if second >= 317:
            close = future_price
        yield second, close, 100.0, 40.0, 10


def test_future_outcome_cannot_change_decision_features():
    downside, _ = scan_rows(_bars(future_price=97.0), PROTOCOL)
    recovery, _ = scan_rows(_bars(future_price=100.0), PROTOCOL)
    assert len(downside) == len(recovery) == 1
    assert downside[0]["trigger_s"] == 301
    assert downside[0]["decision_available_s"] == 317
    assert downside[0]["x_flow"] == recovery[0]["x_flow"]
    assert downside[0]["x_flow"][-1] == 0.6
    assert downside[0]["y"] == 1
    assert recovery[0]["y"] == 0
    assert downside[0]["maturity_s"] == recovery[0]["maturity_s"] == 318


def test_missing_future_bar_invalidates_episode():
    episodes, counts = scan_rows(_bars(future_price=98.9, missing_second=321), PROTOCOL)
    assert len(episodes) == 1
    assert episodes[0]["exclusion_reason"] == "source_gap"
    assert "y" not in episodes[0]
    assert counts["gaps"] == 1


def test_binance_millisecond_and_microsecond_eras():
    assert timestamp_second("1709251200000") == 1709251200
    assert timestamp_second("1790211686000000") == 1790211686


def test_label_maturing_in_test_period_cannot_enter_fit():
    episodes = [
        {"month": "2025-12", "y": 1, "maturity_s": 1767312000},
        {"month": "2026-01", "y": 0, "maturity_s": 1767315600},
    ]
    result, predictions = evaluate(episodes, PROTOCOL)
    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["fit_episodes"] == 0
    assert result["test_episodes"] == 1
    assert predictions == []
