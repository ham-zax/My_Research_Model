"""Run the frozen public Binance BTC spot flow screen without trading P&L."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from mfsm_free_flow.study import read_month, scan_rows


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/mfsm_free_btc_flow_001_protocol.json"
MANIFEST = ROOT / "artifacts/e001_historical_spot_acquisition_manifest.json"
SOURCE_DIR = ROOT / "data/raw/binance_1s"
CODE = ROOT / "src/mfsm_free_flow/study.py"


def file_sha256(path):
    digest = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def months(first, last):
    year, month = map(int, first.split("-"))
    end_year, end_month = map(int, last.split("-"))
    while (year, month) <= (end_year, end_month):
        yield f"{year:04d}-{month:02d}"
        month += 1
        if month == 13:
            year += 1
            month = 1


def verified_rows(protocol):
    manifest = json.loads(MANIFEST.read_text())
    expected = {row["month"]: row["binance_sha256"]
                for row in manifest["free_sources"]}
    receipts = []
    for month in months(protocol["period_first_month"], protocol["period_last_month"]):
        path = SOURCE_DIR / f"BTCUSDT-1s-{month}.zip"
        if month not in expected or not path.is_file():
            raise FileNotFoundError(f"missing pinned BTC source for {month}")
        actual = file_sha256(path)
        if actual != expected[month]:
            raise ValueError(f"source SHA-256 mismatch for {month}")
        receipts.append({"month": month, "path": str(path.relative_to(ROOT)),
                         "sha256": actual})
        yield month, path, receipts


def _brier(rows, predictions):
    return sum((prediction - row["y"]) ** 2
               for row, prediction in zip(rows, predictions)) / len(rows)


def _interval_by_month(rows, baseline, flow, *, draws=5000, seed=1001):
    by_month = defaultdict(list)
    for row, b, f in zip(rows, baseline, flow):
        by_month[row["month"]].append((b - row["y"]) ** 2 - (f - row["y"]) ** 2)
    month_keys = sorted(by_month)
    rng = random.Random(seed)
    samples = []
    for _ in range(draws):
        selected = [rng.choice(month_keys) for _ in month_keys]
        values = [value for month in selected for value in by_month[month]]
        samples.append(sum(values) / len(values))
    samples.sort()
    return [samples[int(0.025 * draws)], samples[int(0.975 * draws)]]


def evaluate(episodes, protocol):
    split = protocol["split"]
    test_start = split["test_first_month"]
    test_start_s = int(datetime.strptime(test_start + "-01", "%Y-%m-%d")
                       .replace(tzinfo=timezone.utc).timestamp())
    eligible = [row for row in episodes if "y" in row]
    fit = [row for row in eligible if row["month"] <= split["fit_last_month"]
           and row["maturity_s"] <= test_start_s]
    test = [row for row in eligible if test_start <= row["month"] <= split["test_last_month"]]
    counts = {"fit": dict(sorted(Counter(row["y"] for row in fit).items())),
              "test": dict(sorted(Counter(row["y"] for row in test).items()))}
    summary = {"fit_episodes": len(fit), "test_episodes": len(test),
               "class_counts": counts,
               "monthly_test_counts": {
                   month: dict(sorted(Counter(row["y"] for row in test
                                              if row["month"] == month).items()))
                   for month in months(test_start, split["test_last_month"])
               }}
    if (len(fit) < split["minimum_fit_episodes"]
            or len(test) < split["minimum_test_episodes"]
            or any(counts["fit"].get(k, 0) < split["minimum_fit_each_class"] for k in (0, 1))
            or any(counts["test"].get(k, 0) < split["minimum_test_each_class"] for k in (0, 1))):
        return {**summary, "status": "INSUFFICIENT_DATA", "model_fitted": False}, []

    fit_y = [row["y"] for row in fit]
    baseline = make_pipeline(StandardScaler(), LogisticRegression(C=1, max_iter=1000))
    flow = make_pipeline(StandardScaler(), LogisticRegression(C=1, max_iter=1000))
    flexible = HistGradientBoostingClassifier(
        loss="log_loss", max_iter=40, max_leaf_nodes=7, min_samples_leaf=20,
        l2_regularization=0.1, early_stopping=False, random_state=1001)
    baseline.fit([row["x_baseline"] for row in fit], fit_y)
    flow.fit([row["x_flow"] for row in fit], fit_y)
    flexible.fit([row["x_flow"] for row in fit], fit_y)
    rates = [sum(fit_y) / len(fit_y)] * len(test)
    b_probs = baseline.predict_proba([row["x_baseline"] for row in test])[:, 1].tolist()
    f_probs = flow.predict_proba([row["x_flow"] for row in test])[:, 1].tolist()
    h_probs = flexible.predict_proba([row["x_flow"] for row in test])[:, 1].tolist()
    scores = {"historical_rate": _brier(test, rates),
              "price_volume_baseline": _brier(test, b_probs),
              "price_volume_plus_flow": _brier(test, f_probs),
              "same_information_flexible": _brier(test, h_probs)}
    predictions = [{"trigger_s": row["trigger_s"], "month": row["month"],
                    "y": row["y"], "historical_rate": rate,
                    "price_volume_baseline": b,
                    "price_volume_plus_flow": f,
                    "same_information_flexible": h}
                   for row, rate, b, f, h in zip(test, rates, b_probs, f_probs, h_probs)]
    return {
        **summary, "status": "RETROSPECTIVE_FLOW_SCORED", "model_fitted": True,
        "test_brier": scores,
        "primary_improvement": scores["price_volume_baseline"] - scores["price_volume_plus_flow"],
        "primary_month_block_bootstrap_95pct": _interval_by_month(test, b_probs, f_probs),
        "interpretation": "spot_taker_flow_screen_only_no_L2_or_trading_edge_claim",
    }, predictions


def run(output):
    protocol = json.loads(PROTOCOL.read_text())
    if protocol["schema"] != "MFSM-FREE-BTC-FLOW-001-protocol-1":
        raise ValueError("unexpected protocol")
    source_receipts = []
    def all_rows():
        for month, path, receipts in verified_rows(protocol):
            source_receipts[:] = receipts
            yield from read_month(path)
            print(f"{month}: verified and scanned", flush=True)
    episodes, scan_counts = scan_rows(all_rows(), protocol)
    score, predictions = evaluate(episodes, protocol)
    output.mkdir(parents=True, exist_ok=False)
    ledger = output / "episodes.jsonl"
    with ledger.open("x", encoding="utf-8") as stream:
        for row in episodes:
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    predictions_path = output / "test_predictions.jsonl"
    with predictions_path.open("x", encoding="utf-8") as stream:
        for row in predictions:
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    report = {
        "schema": "MFSM-FREE-BTC-FLOW-001-result-1", "score": score,
        "scan_counts": scan_counts,
        "episode_count": len(episodes),
        "exclusion_counts": dict(sorted(Counter(
            row["exclusion_reason"] for row in episodes
            if "exclusion_reason" in row).items())),
        "source_receipts": source_receipts,
        "protocol_sha256": file_sha256(PROTOCOL),
        "source_manifest_sha256": file_sha256(MANIFEST),
        "study_code_sha256": file_sha256(CODE),
        "runner_sha256": file_sha256(Path(__file__)),
        "episode_ledger_sha256": file_sha256(ledger),
        "predictions_sha256": file_sha256(predictions_path),
        "python_version": sys.version.split()[0],
        "sklearn_version": sklearn.__version__,
        "eth_accessed": False,
        "trading_edge_claim": False,
    }
    (output / "result.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({"status": result["score"]["status"],
                      "episode_count": result["episode_count"],
                      "score": result["score"].get("test_brier"),
                      "result": str(args.output / "result.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
