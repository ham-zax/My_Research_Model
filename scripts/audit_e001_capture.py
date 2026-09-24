"""Verify one completed live-capture run without fitting or normalizing a model."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from mfsm_e001.capture_store import sha256


def audit(manifest_path):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    run_id = manifest["run_id"]
    if manifest["asset"] != "BTC" or manifest["symbol"] != "BTCUSDT":
        raise ValueError("only BTC captures can be audited")
    if manifest["status"] == "running":
        raise ValueError("stop the run before auditing")
    root = manifest_path.parent
    if list(root.glob(f"{run_id}-*.open")) or list(root.glob(f"{run_id}-*.unclean")):
        raise ValueError("run has unsealed or unclean segments")
    counts = Counter()
    topics = defaultdict(Counter)
    connected, snapshots = set(), set()
    next_id = 0
    rows = total_bytes = 0
    terminal = None
    hashes = {}
    ticker_fields = set()
    for path in sorted(root.glob(f"{run_id}-*.jsonl")):
        metadata = json.loads(path.with_suffix(".meta.json").read_text())
        digest = sha256(path)
        if digest != metadata["sha256"] or path.stat().st_size != metadata["bytes"]:
            raise ValueError(f"segment integrity failure: {path.name}")
        hashes[path.name] = digest
        total_bytes += path.stat().st_size
        segment_rows = 0
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                rows += 1
                segment_rows += 1
                if terminal is not None:
                    raise ValueError("observations after terminal marker")
                if row["kind"] == "run_stopped":
                    terminal = row
                else:
                    if row["record_id"] != next_id:
                        raise ValueError("missing or reordered capture record")
                    next_id += 1
                counts[row["kind"]] += 1
                if row["kind"] == "connected" and row["source"] == "binance_spot":
                    connected.add(row["connection_id"])
                if row["kind"] == "rest_snapshot":
                    snapshots.add(row["connection_id"])
                if row["kind"] == "ws_message":
                    message = json.loads(row["raw"])
                    topic = message.get("topic", message.get("stream", "control"))
                    topics[row["source"]][topic] += 1
                    if topic == "tickers.BTCUSDT":
                        ticker_fields.update(message["data"])
        if segment_rows != metadata["records"]:
            raise ValueError("segment record count mismatch")
    if rows != manifest["records_written"]:
        raise ValueError("run record count mismatch")
    if manifest["status"] == "duration_reached" and (terminal is None or
            next_id != manifest.get("records_emitted", next_id)):
        raise ValueError("completed run missing terminal marker or emitted records")
    missing = {f["name"]: [t for t in f["topics"] if topics[f["name"]][t] == 0]
               for f in manifest["feeds"]}
    return {"provenance": "live_capture_integrity_not_model_validation", "schema": manifest["schema"],
            "run_id": run_id, "status": manifest["status"], "start": manifest["start"],
            "end": manifest["end"], "planned_duration_seconds": manifest["planned_duration_seconds"],
            "manifest_sha256": sha256(manifest_path), "code_sha256": manifest["code_sha256"],
            "segment_sha256": hashes, "records": rows, "raw_bytes_this_run": total_bytes,
            "record_kind_counts": dict(counts), "topics": {k: dict(v) for k, v in topics.items()},
            "topics_without_observations": missing,
            "binance_connections_without_rest_snapshot": sorted(connected - snapshots),
            "ticker_fields_observed": sorted(ticker_fields),
            "integrity_checks_passed": True, "feed_completeness_verified": False,
            "note": "A quiet liquidation channel can have no events. Subscription acknowledgement is separate; "
                    "topic counts, transport heartbeats and hashes do not establish full market coverage."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = audit(args.manifest)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "records", "raw_bytes_this_run",
                                           "record_kind_counts", "topics_without_observations")}, indent=2))


if __name__ == "__main__":
    main()
