"""Fetch the bounded, BTC-only public spot sample used by the E001 data audit."""

import hashlib
from pathlib import Path
import tempfile
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "raw" / "2023-10-01"
FILES = (
    ("binance-btcusdt-spot-trades.zip",
     "https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2023-10-01.zip",
     "afcd135830251d10117343740f7a87134cd3f84bc81ef858468cc84cd9609710"),
    ("bybit-btcusdt-spot.csv.gz",
     "https://public.bybit.com/spot/BTCUSDT/BTCUSDT_2023-10-01.csv.gz",
     "1839e975392b13b9cb4ab7a95464adfef7c9b763d12aefc9fcb6c5c91c35789c"),
)


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            sha.update(block)
    return sha.hexdigest()


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for name, url, expected in FILES:
        target = TARGET / name
        if target.exists():
            actual = digest(target)
            if actual != expected:
                raise RuntimeError(f"existing {target} has unexpected SHA-256: {actual}")
            print(f"verified {target}: {actual}")
            continue
        with tempfile.NamedTemporaryFile(dir=TARGET, prefix=".e001-", delete=False) as temp:
            pending = Path(temp.name)
            try:
                with urlopen(url, timeout=60) as source:
                    for block in iter(lambda: source.read(1 << 20), b""):
                        temp.write(block)
            except BaseException:
                pending.unlink(missing_ok=True)
                raise
        actual = digest(pending)
        if actual != expected:
            pending.unlink()
            raise RuntimeError(f"downloaded {name} has unexpected SHA-256: {actual}")
        pending.replace(target)
        print(f"downloaded {target}: {actual}")


if __name__ == "__main__":
    main()
