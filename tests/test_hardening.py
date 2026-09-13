from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from a2.modeling import calibration_diagnostics, subgroup_diagnostics, threshold_cost_analysis  # noqa: E402
from a2.governance import decide  # noqa: E402
from a2.models import DecisionStatus, RunState, TaskIntake  # noqa: E402
from a2.quality import REQUIRED, assess_quality  # noqa: E402


def robust_frame(n: int = 300) -> pd.DataFrame:
    rows = []
    for index in range(n):
        row = {column: 1 for column in REQUIRED}
        row.update({
            "age": 25 + index % 50,
            "job": ["admin", "services", "technical"][index % 3],
            "marital": "married",
            "education": "secondary",
            "default": "no",
            "housing": "yes" if index % 2 else "no",
            "loan": "no",
            "contact": "cellular" if index % 2 else "telephone",
            "month": "may",
            "day_of_week": "mon",
            "duration": 30 + index,
            "poutcome": "nonexistent",
            "y": "yes" if index % 5 == 0 else "no",
        })
        rows.append(row)
    return pd.DataFrame(rows)


class HardeningTests(unittest.TestCase):
    def test_exact_target_proxy_fails_closed(self) -> None:
        frame = robust_frame()
        frame["outcome_copy"] = frame["y"]
        findings, _ = assess_quality(frame, TaskIntake("hostile proxy"))
        proxy = next(f for f in findings if f.check == "target_proxy_contamination")
        self.assertFalse(proxy.passed)
        self.assertEqual(proxy.severity, "critical")
        self.assertIn("outcome_copy", proxy.evidence)
        state = RunState("hostile", findings=findings)
        decided = decide(state, TaskIntake("hostile proxy"), human_approved=True)
        self.assertEqual(decided.status, DecisionStatus.DATA_QUALITY_FAILURE)
        self.assertFalse(decided.action_authorised)

    def test_corrupted_target_encoding_fails_closed(self) -> None:
        frame = robust_frame()
        frame.loc[0, "y"] = "maybe"
        findings, _ = assess_quality(frame, TaskIntake("corrupt outcome"))
        target = next(f for f in findings if f.check == "binary_target")
        self.assertFalse(target.passed)
        self.assertEqual(target.severity, "critical")
        state = RunState("corrupt", findings=findings)
        decided = decide(state, TaskIntake("corrupt outcome"), human_approved=True)
        self.assertEqual(decided.status, DecisionStatus.DATA_QUALITY_FAILURE)
        self.assertFalse(decided.action_authorised)

    def test_calibration_diagnostics_are_reconstructable(self) -> None:
        result = calibration_diagnostics(np.array([0, 0, 1, 1]), np.array([0.1, 0.1, 0.9, 0.9]), n_bins=5)
        self.assertAlmostEqual(result["expected_calibration_error"], 0.1)
        self.assertEqual(sum(row["count"] for row in result["bins"]), 4)

    def test_threshold_costs_declare_no_selected_threshold(self) -> None:
        result = threshold_cost_analysis(np.array([0, 1]), np.array([0.2, 0.8]))
        self.assertIsNone(result["selected_threshold"])
        self.assertEqual(result["assumptions"]["false_negative_cost_units"], 5.0)

    def test_subgroup_diagnostics_suppress_tiny_groups(self) -> None:
        frame = pd.DataFrame({"age": [25, 35, 45, 65], "job": ["a", "a", "b", "b"], "contact": ["c"] * 4})
        result = subgroup_diagnostics(frame, np.array([0, 0, 1, 1]), np.array([0.1, 0.2, 0.8, 0.9]), minimum_group_size=3)
        self.assertTrue(all(row["n"] >= 3 for row in result["rows"]))
        self.assertTrue(any(row["field"] == "contact" for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
