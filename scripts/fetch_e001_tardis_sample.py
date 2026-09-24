"""Download one BTC-only, receipt-timestamped Tardis sample day for E001 audit.

This is a data acquisition tool. It does not approve the sample for model fitting.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ("bybit-spot", "trades"),
    ("binance", "trades"),
    ("bybit-spot", "quotes"),
    ("binance", "quotes"),
    ("bybit", "trades"),
    ("bybit", "incremental_book_L2"),
    ("bybit", "liquidations"),
    ("bybit", "derivative_ticker"),
)
MAX_BYTES = 250_000_000


def digest(path: Path) -> tuple[str, str, int]:
    sha = hashlib.sha256()
    md5 = hashlib.md5(usedforsecurity=False)
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            sha.update(block)
            md5.update(block)
            size += len(block)
    return sha.hexdigest(), md5.hexdigest(), size


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch fixed BTCUSDT Tardis CSV sample feeds")
    parser.add_argument("--date", default="2025-03-01", help="UTC first day of month, YYYY-MM-01")
    parser.add_argument("--profile", choices=("all", "spot-quotes"), default="all",
                        help="Use spot-quotes for a bounded two-file coverage audit")
    args = parser.parse_args()
    day = datetime.strptime(args.date, "%Y-%m-%d").date()
    if day.day != 1 or not (datetime(2023, 4, 1).date() <= day <= datetime.now(timezone.utc).date()):
        parser.error("date must be a past UTC first-of-month on or after 2023-04-01")
    target = ROOT / "data" / "raw" / "tardis" / args.date
    target.mkdir(parents=True, exist_ok=True)
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for exchange, kind in SOURCES:
        if args.profile == "spot-quotes" and kind != "quotes":
            continue
        name = f"{exchange}_{kind}_{args.date}_BTCUSDT.csv.gz"
        output = target / name
        url = (f"https://datasets.tardis.dev/v1/{exchange}/{kind}/"
               f"{day:%Y/%m/%d}/BTCUSDT.csv.gz")
        if output.exists():
            sha, md5, size = digest(output)
            prior = manifest.get(name)
            if prior is None or prior["sha256"] != sha:
                raise RuntimeError(f"existing {output} has no matching manifest entry")
            print(f"verified {name}: {size} bytes, sha256={sha}", flush=True)
            continue
        request = Request(url, headers={"User-Agent": "Mozilla/5.0 (MFSM E001 BTC research)"})
        with urlopen(request, timeout=90) as response:
            reported_md5 = (response.headers.get("x-md5") or "").strip('"')
            reported_length = response.headers.get("Content-Length")
            with tempfile.NamedTemporaryFile(dir=target, prefix=".e001-", delete=False) as temp:
                pending = Path(temp.name)
                try:
                    size = 0
                    for block in iter(lambda: response.read(1 << 20), b""):
                        size += len(block)
                        if size > MAX_BYTES:
                            raise RuntimeError(f"{name} exceeds {MAX_BYTES} byte safety limit")
                        temp.write(block)
                except BaseException:
                    pending.unlink(missing_ok=True)
                    raise
        sha, md5, size = digest(pending)
        if (reported_md5 and reported_md5 != md5) or (
                reported_length and int(reported_length) != size):
            pending.unlink()
            raise RuntimeError(f"integrity mismatch for {name}")
        pending.replace(output)
        manifest[name] = {
            "url": url,
            "source": "Tardis normalized CSV",
            "symbol": "BTCUSDT",
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": sha,
            "md5": md5,
            "source_md5": reported_md5 or None,
            "bytes": size,
            "has_local_timestamp_column": None,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(f"downloaded {name}: {size} bytes, sha256={sha}", flush=True)


if __name__ == "__main__":
    main()
