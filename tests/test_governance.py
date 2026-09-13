from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from a2.governance import decide  # noqa: E402
from a2.models import DecisionStatus, RunState, TaskIntake  # noqa: E402


class GovernanceTests(unittest.TestCase):
    def test_analysis_does_not_authorise_action(self) -> None:
        state = RunState("run", metrics={"roc_auc": 0.7})
        decided = decide(state, TaskIntake("test"), human_approved=False)
        self.assertTrue(decided.analysis_complete)
        self.assertFalse(decided.action_authorised)
        self.assertEqual(decided.status, DecisionStatus.REQUEST_HUMAN_REVIEW)

    def test_explicit_approval_is_visible(self) -> None:
        state = RunState("run", metrics={"roc_auc": 0.7})
        decided = decide(state, TaskIntake("test"), human_approved=True)
        self.assertTrue(decided.action_authorised)
        self.assertEqual(decided.status, DecisionStatus.PROCEED_WITH_QUALIFICATION)

    def test_causal_request_safe_stops(self) -> None:
        state = RunState("run", metrics={"roc_auc": 0.7})
        decided = decide(state, TaskIntake("test", causal_language=True))
        self.assertEqual(decided.status, DecisionStatus.SAFE_STOP)
        self.assertFalse(decided.action_authorised)


if __name__ == "__main__":
    unittest.main()

