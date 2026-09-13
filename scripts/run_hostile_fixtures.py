#!/usr/bin/env python3
"""Execute bounded hostile data fixtures without touching the pinned source."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from a2.governance import decide  # noqa: E402
from a2.models import RunState, TaskIntake  # noqa: E402
from a2.quality import REQUIRED, assess_quality  # noqa: E402


def base_frame(n: int = 300) -> pd.DataFrame:
    rows = []
    for index in range(n):
        row = {column: 1 for column in REQUIRED}
        row.update({
            "age": 25 + index % 50, "job": ["admin", "services", "technical"][index % 3],
            "marital": "married", "education": "secondary", "default": "no",
            "housing": "yes" if index % 2 else "no", "loan": "no",
            "contact": "cellular" if index % 2 else "telephone", "month": "may",
            "day_of_week": "mon", "duration": 30 + index, "poutcome": "nonexistent",
            "y": "yes" if index % 5 == 0 else "no",
        })
        rows.append(row)
    return pd.DataFrame(rows)


def disposition(name: str, frame: pd.DataFrame) -> dict[str, object]:
    task = TaskIntake(f"hostile fixture: {name}")
    findings, excluded = assess_quality(frame, task)
    state = decide(RunState(name, findings=findings, excluded_features=excluded), task, human_approved=True)
    return {
        "fixture": name,
        "approval_supplied": True,
        "status": state.status.value,
        "analysis_complete": state.analysis_complete,
        "action_authorised": state.action_authorised,
        "critical_failures": [f.__dict__ for f in findings if not f.passed and f.severity == "critical"],
    }


def main() -> int:
    target_copy = base_frame()
    target_copy["outcome_copy"] = target_copy["y"]
    corrupt_label = base_frame()
    corrupt_label.loc[0, "y"] = "maybe"
    report = {
        "suite": "A2 V1.1 hostile data fixtures",
        "purpose": "verify that human approval cannot override critical evidence failure",
        "results": [disposition("exact_target_proxy", target_copy), disposition("corrupted_target_label", corrupt_label)],
    }
    destination = ROOT / "outputs" / "reference_v1_1_hostile_report.json"
    destination.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all(not item["action_authorised"] for item in report["results"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
