"""Causal one-second BTC event and label construction from public spot bars."""

from collections import Counter, deque
from datetime import datetime, timezone
from math import isfinite, log, log1p, sqrt
from pathlib import Path
from zipfile import ZipFile


def timestamp_second(raw: str) -> int:
    value = int(raw)
    if value >= 10**15:
        return value // 1_000_000
    if value >= 10**12:
        return value // 1_000
    raise ValueError(f"unexpected Binance timestamp scale: {value}")


def read_month(path: Path):
    """Yield (UTC second, close, quote volume, taker-buy quote, trade count)."""
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != 1 or names[0] != path.stem + ".csv":
            raise ValueError(f"unexpected archive member in {path}")
        with archive.open(names[0]) as stream:
            for line_number, raw in enumerate(stream, 1):
                fields = raw.decode("ascii").rstrip("\r\n").split(",")
                if len(fields) != 12:
                    raise ValueError(f"{path}:{line_number}: expected 12 kline columns")
                second = timestamp_second(fields[0])
                close = float(fields[4])
                quote = float(fields[7])
                trades = int(fields[8])
                taker_buy = float(fields[10])
                if (not all(isfinite(x) for x in (close, quote, taker_buy))
                        or close <= 0 or quote < 0 or trades < 0
                        or taker_buy < 0 or taker_buy > quote + max(1e-8, quote * 1e-10)):
                    raise ValueError(f"{path}:{line_number}: invalid price or flow")
                yield second, close, quote, min(taker_buy, quote), trades


def _features(history, trigger_return):
    if len(history) != 301 or history[-1][0] - history[0][0] != 300:
        return None
    flow = list(history)[-30:]
    total_quote = sum(row[2] for row in flow)
    if total_quote <= 0:
        return None
    total_buy = sum(row[3] for row in flow)
    closes = [row[1] for row in history]
    log_returns = [log(closes[i] / closes[i - 1]) for i in range(1, 301)]
    mean = sum(log_returns) / 300
    vol = sqrt(sum((value - mean) ** 2 for value in log_returns) / 300)
    common = [
        trigger_return,
        closes[-1] / closes[-31] - 1,
        vol,
        log1p(total_quote),
        log1p(sum(row[4] for row in flow)),
    ]
    return common, common + [(total_quote - total_buy) / total_quote]


def scan_rows(rows, protocol):
    """Build episodes in source order; never use a bar beyond the feature cutoff."""
    event = protocol["event"]
    decision = protocol["decision"]
    label = protocol["label"]
    if (event["return_seconds"] != 300
            or decision["flow_window_completed_bars"] != 30
            or decision["volatility_window_returns"] != 300
            or decision["last_completed_bar_offset_seconds"] != 15
            or label["first_future_bar_offset_seconds"] != 16):
        raise ValueError("unsupported free-flow timing contract")
    history = deque(maxlen=301)
    pending = []
    episodes = []
    previous_second = None
    previous_falling = None
    last_accepted = None
    counts = Counter()

    def exclude_open(reason):
        for episode in pending:
            episode["exclusion_reason"] = reason
            episodes.append(episode)
        pending.clear()

    for second, close, quote, taker_buy, trades in rows:
        if previous_second is not None:
            if second <= previous_second:
                raise ValueError("source rows must be strictly increasing")
            if second != previous_second + 1:
                counts["gaps"] += 1
                exclude_open("source_gap")
                history.clear()
                previous_falling = None
        previous_second = second
        counts["bars"] += 1
        history.append((second, close, quote, taker_buy, trades))

        for episode in pending[:]:
            offset = second - episode["trigger_s"]
            if offset == decision["last_completed_bar_offset_seconds"]:
                features = _features(history, episode["trigger_return_300s"])
                if features is None:
                    episode["exclusion_reason"] = "feature_unavailable"
                    episodes.append(episode)
                    pending.remove(episode)
                else:
                    episode["decision_available_s"] = second + 1
                    episode["reference_close"] = close
                    episode["x_baseline"], episode["x_flow"] = features
            elif (episode.get("reference_close") is not None
                  and label["first_future_bar_offset_seconds"] <= offset
                  < label["first_future_bar_offset_seconds"] + label["horizon_seconds"]):
                change = close / episode["reference_close"] - 1
                if change <= label["downside_close_return_lte"]:
                    episode.update(y=1, outcome="downside_first", maturity_s=second + 1)
                elif change >= label["upside_close_return_gte"]:
                    episode.update(y=0, outcome="upside_first", maturity_s=second + 1)
                elif offset == (label["first_future_bar_offset_seconds"]
                                + label["horizon_seconds"] - 1):
                    episode.update(y=0, outcome="neither", maturity_s=second + 1)
                if "y" in episode:
                    episodes.append(episode)
                    pending.remove(episode)

        falling = None
        if len(history) == 301 and history[0][0] == second - 300:
            change = close / history[0][1] - 1
            falling = change <= event["return_lte"]
            if falling and previous_falling is False:
                counts["raw_crossings"] += 1
                if last_accepted is None or second >= last_accepted + event["lockout_seconds"]:
                    last_accepted = second
                    counts["accepted_crossings"] += 1
                    pending.append({
                        "trigger_s": second,
                        "trigger_utc": datetime.fromtimestamp(
                            second, timezone.utc).isoformat(),
                        "month": datetime.fromtimestamp(second, timezone.utc).strftime("%Y-%m"),
                        "trigger_return_300s": change,
                    })
        previous_falling = falling

    exclude_open("incomplete_future")
    episodes.sort(key=lambda row: row["trigger_s"])
    return episodes, dict(counts)
