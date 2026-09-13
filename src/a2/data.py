from __future__ import annotations

import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

UCI_URL = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"
ARCHIVE_SHA256 = "e0bf5f5de5b846e2f18e9d90606637267d46dfa260e0f17bb12e605db5efbeb4"
CSV_MEMBER = "bank-additional/bank-additional-full.csv"
CSV_SHA256 = "74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def fetch_dataset(cache_path: Path, allow_network: bool = True) -> tuple[pd.DataFrame, dict[str, str]]:
    """Fetch the pinned UCI archive, verify both archive and CSV, and return dated full data."""
    if cache_path.exists():
        archive = cache_path.read_bytes()
        source_mode = "cache"
    elif allow_network:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(UCI_URL, timeout=30) as response:
            archive = response.read()
        cache_path.write_bytes(archive)
        source_mode = "network"
    else:
        raise FileNotFoundError(f"Pinned archive is absent and network is disabled: {cache_path}")

    archive_hash = sha256_bytes(archive)
    if archive_hash != ARCHIVE_SHA256:
        raise ValueError(f"Archive hash mismatch: expected {ARCHIVE_SHA256}, got {archive_hash}")

    with zipfile.ZipFile(io.BytesIO(archive)) as outer:
        nested = outer.read("bank-additional.zip")
    with zipfile.ZipFile(io.BytesIO(nested)) as inner:
        csv_bytes = inner.read(CSV_MEMBER)

    csv_hash = sha256_bytes(csv_bytes)
    if csv_hash != CSV_SHA256:
        raise ValueError(f"CSV hash mismatch: expected {CSV_SHA256}, got {csv_hash}")

    frame = pd.read_csv(io.BytesIO(csv_bytes), sep=";")
    provenance = {
        "dataset": "UCI Bank Marketing: bank-additional-full.csv",
        "uci_dataset_id": "222",
        "doi": "10.24432/C5K306",
        "source_url": UCI_URL,
        "license": "CC BY 4.0",
        "archive_sha256": archive_hash,
        "csv_sha256": csv_hash,
        "retrieval_mode": source_mode,
        "record_order": "UCI describes the full additional dataset as ordered by date, May 2008-November 2010",
    }
    return frame, provenance

