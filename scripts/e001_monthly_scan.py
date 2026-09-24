"""Reproducible fixed-calendar BTC feasibility scan, with per-day checkpoints."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from e001_quote_audit import audit_day, file_sha256


ROOT = Path(__file__).resolve().parents[1]
DATES = [f"{year}-{month:02d}-01" for year in (2025, 2026) for month in range(1, 13)
         if "2025-03-01" <= f"{year}-{month:02d}-01" <= "2026-09-01"]


def pipeline_digest():
    digest = hashlib.sha256()
    for name in ("scripts/e001_quote_audit.py", "src/mfsm_e001/events.py",
                 "src/mfsm_e001/labels.py", "src/mfsm_e001/spot_quotes.py"):
        digest.update(name.encode())
        digest.update((ROOT / name).read_bytes())
    return digest.hexdigest()


def valid_checkpoint(path, date, pipeline_sha):
    if not path.exists():
        return None
    saved = json.loads(path.read_text())
    if saved["pipeline_sha256"] != pipeline_sha:
        return None
    result = saved["result"]
    folder = ROOT / "data/raw/tardis" / date
    for venue, exchange in (("binance", "binance"), ("bybit", "bybit-spot")):
        source = folder / f"{exchange}_quotes_{date}_BTCUSDT.csv.gz"
        if not source.exists() or file_sha256(source) != result["spot_source_sha256"][venue]:
            return None
    if not (ROOT / result["grid_file"]).exists():
        return None
    return result


def save_report(output, results, failures, pipeline_sha):
    report = {"provenance": "fixed_monthly_btc_spot_feasibility_no_model_scoring",
              "dates_requested": DATES, "dates_completed": sorted(results),
              "experiment_candidate": "e001-v1.2", "raw_schema": "E001-raw-candidate-2",
              "label_schema": "E001-label-v3", "pipeline_sha256": pipeline_sha,
              "feed_liveness_verified": False, "failures": failures,
              "status": "complete" if len(results) == len(DATES) else "incomplete",
              "days": [results[date] for date in sorted(results)]}
    pending = output.with_suffix(".tmp")
    pending.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    pending.replace(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Fetch/verify all fixed BTC quote samples first")
    parser.add_argument("--workers", type=int, choices=(1, 2, 3), default=2)
    args = parser.parse_args()
    directory = ROOT / "data/derived/e001_monthly_scan"
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "audit.json"
    results, failures = {}, {}
    pipeline_sha = pipeline_digest()
    pending = []
    for date in DATES:
        if args.download:
            download = subprocess.run([sys.executable, str(ROOT / "scripts/fetch_e001_tardis_sample.py"),
                                       "--date", date, "--profile", "spot-quotes"],
                                      capture_output=True, text=True)
            (directory / f"{date}-download.log").write_text(download.stdout + download.stderr)
            if download.returncode:
                failures[date] = {"stage": "download", "reason": "see date-download.log",
                                  "returncode": download.returncode}
                continue
        checkpoint = directory / f"{date}.json"
        cached = valid_checkpoint(checkpoint, date, pipeline_sha)
        if cached:
            results[date] = cached
            print(f"{date}: reused verified checkpoint", flush=True)
        else:
            pending.append(date)
    save_report(output, results, failures, pipeline_sha)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(audit_day, date): date for date in pending}
        for future in as_completed(futures):
            date = futures[future]
            try:
                result = future.result()
                results[date] = result
                (directory / f"{date}.json").write_text(json.dumps(
                    {"pipeline_sha256": pipeline_sha, "result": result}, indent=2, sort_keys=True) + "\n")
                print(f"{date}: {result['accepted_events']} nominal episodes; "
                      f"{result['primary_label_counts']}; "
                      f"{result['sensitivity'][5]['valid_seconds']}/86400 valid seconds", flush=True)
            except Exception as exc:
                failures[date] = {"stage": "audit", "reason": f"{type(exc).__name__}: {exc}"}
                print(f"{date}: audit failed: {exc}", flush=True)
            save_report(output, results, failures, pipeline_sha)
    print(output, flush=True)
    return 0 if not failures and len(results) == len(DATES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
