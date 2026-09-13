from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from a2.models import TaskIntake  # noqa: E402
from a2.quality import REQUIRED, assess_quality  # noqa: E402


def valid_frame() -> pd.DataFrame:
    row = {column: 1 for column in REQUIRED}
    for key in ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "day_of_week", "poutcome"]:
        row[key] = "known"
    row.update({"age": 42, "duration": 120, "y": "yes"})
    other = dict(row)
    other.update({"age": 43, "duration": 60, "y": "no"})
    return pd.DataFrame([row, other])


class QualityTests(unittest.TestCase):
    def test_pre_contact_duration_is_excluded(self) -> None:
        findings, excluded = assess_quality(valid_frame(), TaskIntake("test"))
        self.assertIn("duration", excluded)
        leakage = next(f for f in findings if f.check == "temporal_leakage_duration")
        self.assertFalse(leakage.passed)
        self.assertEqual(leakage.severity, "critical")

    def test_missing_target_is_critical(self) -> None:
        frame = valid_frame().drop(columns=["y"])
        findings, _ = assess_quality(frame, TaskIntake("test"))
        schema = next(f for f in findings if f.check == "required_schema")
        self.assertFalse(schema.passed)
        self.assertEqual(schema.severity, "critical")

    def test_unknown_is_not_treated_as_clean(self) -> None:
        frame = valid_frame()
        frame.loc[0, "education"] = "unknown"
        findings, _ = assess_quality(frame, TaskIntake("test"))
        semantic = next(f for f in findings if f.check == "semantic_missingness")
        self.assertFalse(semantic.passed)

    def test_severe_missingness_is_critical(self) -> None:
        frame = pd.concat([valid_frame()] * 120, ignore_index=True)
        frame.loc[:150, "education"] = None
        findings, _ = assess_quality(frame, TaskIntake("test"))
        severe = next(f for f in findings if f.check == "severe_column_missingness")
        self.assertFalse(severe.passed)
        self.assertEqual(severe.severity, "critical")

    def test_tiny_sample_is_critical(self) -> None:
        findings, _ = assess_quality(valid_frame(), TaskIntake("test"))
        support = next(f for f in findings if f.check == "minimum_sample_support")
        self.assertFalse(support.passed)
        self.assertEqual(support.severity, "critical")


if __name__ == "__main__":
    unittest.main()
