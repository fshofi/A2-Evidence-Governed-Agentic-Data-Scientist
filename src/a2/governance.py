from __future__ import annotations

from .models import DecisionStatus, Finding, RunState, TaskIntake


def decide(state: RunState, task: TaskIntake, human_approved: bool = False) -> RunState:
    critical_failures = [f for f in state.findings if not f.passed and f.severity == "critical"]
    unrepairable = [f for f in critical_failures if f.check != "temporal_leakage_duration"]

    if task.causal_language:
        state.status = DecisionStatus.SAFE_STOP
        state.analysis_complete = False
        state.limitations.append("Predictive observational data cannot establish a causal effect of contacting a client.")
    elif unrepairable:
        state.status = DecisionStatus.DATA_QUALITY_FAILURE
        state.analysis_complete = False
    elif not state.metrics:
        state.status = DecisionStatus.INSUFFICIENT_EVIDENCE
        state.analysis_complete = False
    else:
        state.analysis_complete = True
        state.status = DecisionStatus.REQUEST_HUMAN_REVIEW

    if human_approved and state.analysis_complete:
        state.action_authorised = True
        state.status = DecisionStatus.PROCEED_WITH_QUALIFICATION
    else:
        state.action_authorised = False
    return state

