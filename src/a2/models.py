from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DecisionStatus(str, Enum):
    PROCEED = "PROCEED"
    PROCEED_WITH_QUALIFICATION = "PROCEED_WITH_QUALIFICATION"
    REQUEST_HUMAN_REVIEW = "REQUEST_HUMAN_REVIEW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ASSUMPTION_FAILURE = "ASSUMPTION_FAILURE"
    DATA_QUALITY_FAILURE = "DATA_QUALITY_FAILURE"
    SAFE_STOP = "SAFE_STOP"


@dataclass(frozen=True)
class TaskIntake:
    objective: str
    problem_type: str = "predictive"
    deployment_moment: str = "pre_contact"
    requested_action: str = "prioritise records for human review"
    consequence: str = "moderate"
    causal_language: bool = False


@dataclass
class Finding:
    check: str
    severity: str
    passed: bool
    evidence: str
    minimum_repair: str | None = None


@dataclass
class RunState:
    run_id: str
    status: DecisionStatus = DecisionStatus.INSUFFICIENT_EVIDENCE
    analysis_complete: bool = False
    action_authorised: bool = False
    task: dict[str, Any] = field(default_factory=dict)
    conclusion: str = "No evidence-qualified conclusion has been produced."
    findings: list[Finding] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    uncertainty: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    excluded_features: list[str] = field(default_factory=list)
    evidence_chain: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        return value
