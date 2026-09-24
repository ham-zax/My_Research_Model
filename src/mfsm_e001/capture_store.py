"""Append-only raw capture segments; restart means a new, explicitly separate run."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import time
import uuid


class StorageLimit(RuntimeError):
    pass


def atomic_json(path, value):
    pending = path.with_suffix(path.suffix + ".tmp")
    with pending.open("w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    pending.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


class CaptureStore:
    """Single writer, byte-bounded raw storage; never deletes or resumes old segments.

    Metadata is outside the raw-byte budget. A crash can leave a truncated .open
    tail: seal it unchanged as .unclean, hash it and record the interruption.
    Consumers must never silently ingest those tails as clean JSONL.
    """

    def __init__(self, root, *, max_bytes, segment_bytes=8 << 20):
        self.root = Path(root)
        if "eth" in str(self.root.resolve()).lower():
            raise ValueError("ETH holdout is sealed")
        if max_bytes <= 0 or segment_bytes <= 0:
            raise ValueError("storage limits must be positive")
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = (self.root / ".writer.lock").open("a")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.lock.close()
            raise RuntimeError("another collector owns this output directory") from None
        self.max_bytes, self.segment_bytes = max_bytes, segment_bytes
        self.run_id = uuid.uuid4().hex
        self.file = None
        self.path = None
        self.segment_size = 0
        self.segment_records = 0
        self.records = 0
        self.segment_number = 0
        self.recovered = []
        self.total_bytes = sum(p.stat().st_size for p in self.root.iterdir()
                               if p.suffix in {".jsonl", ".open", ".unclean"})
        try:
            for path in sorted(self.root.glob("*.open")):
                sealed = path.with_suffix(".unclean")
                path.rename(sealed)
                atomic_json(sealed.with_suffix(".meta.json"), {
                    "path": sealed.name, "status": "unclean_previous_run",
                    "bytes": sealed.stat().st_size, "sha256": sha256(sealed)})
                self.recovered.append(sealed.name)
        except BaseException:
            self.lock.close()
            raise
        self.last_flush = time.monotonic()

    def append(self, record):
        encoded = (json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        if self.total_bytes + len(encoded) > self.max_bytes:
            raise StorageLimit("raw-byte budget reached; no old observations deleted")
        if self.file and self.segment_size + len(encoded) > self.segment_bytes:
            self.seal()
        if self.file is None:
            self.segment_number += 1
            self.path = self.root / f"{self.run_id}-{self.segment_number:06d}.open"
            self.file = self.path.open("xb")
            self.segment_size = self.segment_records = 0
        self.file.write(encoded)
        self.segment_size += len(encoded)
        self.total_bytes += len(encoded)
        self.segment_records += 1
        self.records += 1
        if time.monotonic() - self.last_flush >= 1:
            self.flush()

    def flush(self):
        if self.file:
            self.file.flush()
            os.fsync(self.file.fileno())
            atomic_json(self.root / "checkpoint.json", {
                "run_id": self.run_id, "segment": self.path.name,
                "durable_bytes_in_segment": self.segment_size,
                "records_in_run": self.records, "raw_bytes_in_directory": self.total_bytes,
                "updated_ns": time.time_ns()})
        self.last_flush = time.monotonic()

    def seal(self):
        if self.file is None:
            return
        self.flush()
        self.file.close()
        self.file = None
        sealed = self.path.with_suffix(".jsonl")
        self.path.rename(sealed)
        atomic_json(sealed.with_suffix(".meta.json"), {
            "path": sealed.name, "run_id": self.run_id, "status": "closed",
            "bytes": self.segment_size, "records": self.segment_records,
            "sha256": sha256(sealed)})

    def close(self):
        try:
            self.seal()
        finally:
            if self.file:
                self.file.close()
            self.lock.close()
