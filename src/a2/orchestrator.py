from __future__ import annotations

import json
import uuid
from pathlib import Path

from .audit import AuditLogger
from .data import fetch_dataset
from .governance import decide
from .modeling import train_and_validate
from .models import DecisionStatus, Finding, RunState, TaskIntake
from .quality import assess_quality


def run_pipeline(project_root: Path, task: TaskIntake, human_approved: bool = False,
                 allow_network: bool = True) -> RunState:
    run_id = uuid.uuid4().hex[:12]
    state = RunState(run_id=run_id)
    state.task = task.__dict__.copy()
    audit = AuditLogger(project_root / "outputs" / f"audit-{run_id}.jsonl", run_id)
    audit.record("orchestrator", "task_received", task.__dict__)

    if task.problem_type not in {"predictive", "descriptive", "exploratory"}:
        state.status = DecisionStatus.SAFE_STOP
        state.limitations.append(f"Problem type '{task.problem_type}' is outside the V1 method boundary.")
        state.conclusion = "No analytical conclusion: the requested problem class is outside the V1 method boundary."
        audit.record("governance_gate", "safe_stop", {"reason": state.limitations[-1]})
        _write_report(project_root, state)
        return state

    try:
        frame, provenance = fetch_dataset(project_root / "data" / "raw" / "bank_marketing.zip", allow_network)
    except Exception as exc:
        state.status = DecisionStatus.DATA_QUALITY_FAILURE
        state.limitations.append(str(exc))
        state.conclusion = "No analytical conclusion: source identity or availability could not be established."
        audit.record("data_intake", "failure", {"error": str(exc)})
        _write_report(project_root, state)
        return state

    state.provenance = provenance
    audit.record("provenance_agent", "verified", provenance)

    findings, excluded = assess_quality(frame, task)
    state.findings.extend(findings)
    state.excluded_features.extend(excluded)
    audit.record("data_quality_agent", "checks_complete", {
        "findings": [f.__dict__ for f in findings], "excluded_features": excluded,
    })

    if task.causal_language:
        state = decide(state, task, human_approved)
        state.conclusion = "No causal conclusion is supported by this observational predictive dataset."
        audit.record("governance_gate", "safe_stop", {"status": state.status.value})
        _write_report(project_root, state)
        return state

    if any(not f.passed and f.severity == "critical" and f.check != "temporal_leakage_duration" for f in findings):
        state = decide(state, task, human_approved)
        state.conclusion = "No model conclusion: an unrepairable critical data-quality condition remains."
        audit.record("governance_gate", "data_quality_failure", {"status": state.status.value})
        _write_report(project_root, state)
        return state

    metrics, uncertainty, predictions = train_and_validate(frame, excluded)
    state.metrics = metrics
    state.uncertainty = uncertainty
    prevalence_shift = abs(metrics["positive_rate_test"] - metrics["positive_rate_train"])
    state.findings.append(Finding(
        "target_prevalence_shift", "high", prevalence_shift <= 0.10,
        f"absolute train/test prevalence difference={prevalence_shift:.4f}",
        "recalibrate and validate prospectively on the intended current population before operational use" if prevalence_shift > 0.10 else None,
    ))
    state.findings.append(Finding(
        "probability_baseline", "high", metrics["brier_score"] < metrics["baseline_brier_score"],
        f"model Brier={metrics['brier_score']:.4f}; prior baseline={metrics['baseline_brier_score']:.4f}",
        "reject or recalibrate the probability model" if metrics["brier_score"] >= metrics["baseline_brier_score"] else None,
    ))
    state.findings.append(Finding(
        "retrospective_calibration", "high",
        metrics["calibration"]["expected_calibration_error"] <= 0.05
        and metrics["calibration"]["maximum_calibration_error"] <= 0.15,
        f"ECE={metrics['calibration']['expected_calibration_error']:.4f}; maximum bin gap={metrics['calibration']['maximum_calibration_error']:.4f}; calibration-in-the-large={metrics['calibration']['calibration_in_the_large']:.4f}",
        "recalibrate on current representative data and validate prospectively"
        if metrics["calibration"]["expected_calibration_error"] > 0.05
        or metrics["calibration"]["maximum_calibration_error"] > 0.15 else None,
    ))
    state.limitations.extend([
        "Historical Portuguese bank-campaign data from 2008-2010 may not transport to another institution, population, channel, or period.",
        "The dataset documents campaign outcomes, not permission, vulnerability, fairness, cost, or customer harm.",
        "Predicted probability is not authority to contact, deny, price, or otherwise act on a person.",
        "The ordered holdout is stronger than a random split for this source but is not a prospective deployment trial.",
        "Illustrative false-positive/false-negative costs are sensitivity inputs, not an operational threshold recommendation.",
        "Subgroup diagnostics are descriptive stability checks and do not establish fairness or legal compliance.",
    ])
    state.evidence_chain = [
        {"stage": "evidence", "result": "source and hashes verified"},
        {"stage": "assumptions", "result": "pre-contact moment fixed; post-contact duration excluded"},
        {"stage": "method", "result": "interpretable logistic regression plus prior baseline"},
        {"stage": "validation", "result": "ordered 80/20 holdout and imbalance-aware metrics"},
        {"stage": "uncertainty", "result": "approximate AUC interval plus shift warning"},
        {"stage": "hardening", "result": "calibration, threshold sensitivity and subgroup stability diagnostics"},
        {"stage": "authority", "result": "human approval required"},
    ]
    state.conclusion = (
        "After excluding post-contact duration, the logistic model shows bounded retrospective "
        f"ranking value on the later ordered holdout (ROC AUC {metrics['roc_auc']:.3f}; average precision "
        f"{metrics['average_precision']:.3f}) and improves Brier score over the training-prior baseline "
        f"({metrics['brier_score']:.3f} versus {metrics['baseline_brier_score']:.3f}). The large target-prevalence "
        "shift and historical source prevent a deployment or causal claim. Analysis may inform human review only; "
        "it does not authorise contact or another action."
    )
    predictions.to_csv(project_root / "outputs" / f"predictions-{run_id}.csv", index=False)
    audit.record("validation_agent", "validation_complete", {
        "metrics": metrics, "uncertainty": uncertainty,
        "post_validation_findings": [f.__dict__ for f in state.findings[-3:]],
    })

    state = decide(state, task, human_approved)
    audit.record("governance_gate", "decision", {
        "analysis_complete": state.analysis_complete,
        "action_authorised": state.action_authorised,
        "status": state.status.value,
    })
    _write_report(project_root, state)
    return state


def _write_report(project_root: Path, state: RunState) -> None:
    output = project_root / "outputs" / f"report-{state.run_id}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
