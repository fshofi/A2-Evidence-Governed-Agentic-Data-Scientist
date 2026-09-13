from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from a2.data import fetch_dataset  # noqa: E402


class ProvenanceTests(unittest.TestCase):
    def test_real_cached_source_and_csv_hashes_pass(self) -> None:
        frame, provenance = fetch_dataset(ROOT / "data" / "raw" / "bank_marketing.zip", allow_network=False)
        self.assertEqual(len(frame), 41188)
        self.assertEqual(provenance["uci_dataset_id"], "222")

    def test_tampered_archive_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "bank_marketing.zip"
            target.write_bytes(b"not the pinned archive")
            with self.assertRaises(ValueError):
                fetch_dataset(target, allow_network=False)


if __name__ == "__main__":
    unittest.main()

