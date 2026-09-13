#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from a2.models import TaskIntake  # noqa: E402
from a2.orchestrator import run_pipeline  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the A2 governed Data Science V1 pipeline")
    parser.add_argument("--causal", action="store_true", help="Submit an unsupported causal request (adversarial test)")
    parser.add_argument("--approve", action="store_true", help="Record explicit human approval for this bounded demonstration")
    parser.add_argument("--offline", action="store_true", help="Require the pinned dataset cache")
    args = parser.parse_args()

    task = TaskIntake(
        objective="Estimate term-deposit subscription propensity before a call for bounded human review",
        causal_language=args.causal,
    )
    state = run_pipeline(ROOT, task, human_approved=args.approve, allow_network=not args.offline)
    print(json.dumps({
        "run_id": state.run_id,
        "analysis_complete": state.analysis_complete,
        "action_authorised": state.action_authorised,
        "status": state.status.value,
        "excluded_features": state.excluded_features,
        "metrics": state.metrics,
    }, indent=2))
    return 0 if state.analysis_complete or state.status.value == "SAFE_STOP" else 2


if __name__ == "__main__":
    raise SystemExit(main())

