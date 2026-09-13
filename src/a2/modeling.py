from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, balanced_accuracy_score, brier_score_loss,
    confusion_matrix, precision_score, recall_score, roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _auc_ci(auc: float, positives: int, negatives: int) -> tuple[float, float]:
    """Hanley-McNeil large-sample 95% CI; labelled approximate in output."""
    q1 = auc / (2 - auc)
    q2 = 2 * auc * auc / (1 + auc)
    variance = (
        auc * (1 - auc)
        + (positives - 1) * (q1 - auc * auc)
        + (negatives - 1) * (q2 - auc * auc)
    ) / (positives * negatives)
    se = math.sqrt(max(variance, 0.0))
    return max(0.0, auc - 1.96 * se), min(1.0, auc + 1.96 * se)


def calibration_diagnostics(y_true: pd.Series | np.ndarray,
                            probabilities: np.ndarray,
                            n_bins: int = 10) -> dict[str, Any]:
    """Return transparent equal-width reliability bins and bounded summary errors."""
    actual = np.asarray(y_true, dtype=int)
    predicted = np.asarray(probabilities, dtype=float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.clip(np.digitize(predicted, edges[1:-1], right=False), 0, n_bins - 1)
    bins: list[dict[str, Any]] = []
    weighted_gap = 0.0
    maximum_gap = 0.0
    for index in range(n_bins):
        mask = bin_ids == index
        if not mask.any():
            continue
        mean_prediction = float(predicted[mask].mean())
        observed_rate = float(actual[mask].mean())
        gap = abs(mean_prediction - observed_rate)
        count = int(mask.sum())
        weighted_gap += gap * count
        maximum_gap = max(maximum_gap, gap)
        bins.append({
            "lower": float(edges[index]),
            "upper": float(edges[index + 1]),
            "count": count,
            "mean_prediction": mean_prediction,
            "observed_rate": observed_rate,
            "absolute_gap": float(gap),
        })
    return {
        "method": f"equal-width reliability diagram ({n_bins} bins)",
        "expected_calibration_error": float(weighted_gap / len(actual)),
        "maximum_calibration_error": float(maximum_gap),
        "mean_predicted_probability": float(predicted.mean()),
        "observed_prevalence": float(actual.mean()),
        "calibration_in_the_large": float(predicted.mean() - actual.mean()),
        "bins": bins,
        "warning": "These are retrospective diagnostics on one shifted holdout, not evidence of prospective calibration.",
    }


def threshold_cost_analysis(y_true: pd.Series | np.ndarray,
                            probabilities: np.ndarray,
                            false_positive_cost: float = 1.0,
                            false_negative_cost: float = 5.0) -> dict[str, Any]:
    """Expose threshold consequences under declared illustrative costs; never select an action threshold."""
    actual = np.asarray(y_true, dtype=int)
    rows: list[dict[str, Any]] = []
    for threshold in (0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70):
        predicted = (probabilities >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
        rows.append({
            "threshold": threshold,
            "flagged_count": int(predicted.sum()),
            "flagged_rate": float(predicted.mean()),
            "precision": float(precision_score(actual, predicted, zero_division=0)),
            "recall": float(recall_score(actual, predicted, zero_division=0)),
            "specificity": float(tn / (tn + fp)) if (tn + fp) else 0.0,
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
            "illustrative_cost": float(fp * false_positive_cost + fn * false_negative_cost),
        })
    return {
        "assumptions": {
            "false_positive_cost_units": false_positive_cost,
            "false_negative_cost_units": false_negative_cost,
        },
        "rows": rows,
        "selected_threshold": None,
        "warning": "Costs are illustrative sensitivity inputs. No threshold is authorised without real capacity, consent, harm and accountable-owner criteria.",
    }


def subgroup_diagnostics(X_test: pd.DataFrame, y_true: pd.Series | np.ndarray,
                         probabilities: np.ndarray, minimum_group_size: int = 100) -> dict[str, Any]:
    """Describe error stability across available fields without asserting legal or fairness adequacy."""
    actual = np.asarray(y_true, dtype=int)
    diagnostic_frame = X_test.reset_index(drop=True).copy()
    diagnostic_frame["_actual"] = actual
    diagnostic_frame["_probability"] = probabilities
    diagnostic_frame["age_band"] = pd.cut(
        diagnostic_frame["age"], bins=[0, 29, 39, 49, 59, np.inf],
        labels=["under 30", "30-39", "40-49", "50-59", "60+"], right=True,
    ).astype(str)
    rows: list[dict[str, Any]] = []
    for field in ("age_band", "job", "contact"):
        for group, part in diagnostic_frame.groupby(field, observed=True, dropna=False):
            if len(part) < minimum_group_size:
                continue
            group_actual = part["_actual"].to_numpy(dtype=int)
            group_probability = part["_probability"].to_numpy(dtype=float)
            auc = None
            if len(np.unique(group_actual)) == 2:
                auc = float(roc_auc_score(group_actual, group_probability))
            rows.append({
                "field": field,
                "group": str(group),
                "n": int(len(part)),
                "positive_rate": float(group_actual.mean()),
                "mean_probability": float(group_probability.mean()),
                "brier_score": float(brier_score_loss(group_actual, group_probability)),
                "roc_auc": auc,
            })
    return {
        "minimum_group_size": minimum_group_size,
        "rows": rows,
        "warning": "Descriptive error diagnostics only. Available fields are incomplete proxies and do not support a fairness, equality or legal-compliance conclusion.",
    }


def train_and_validate(frame: pd.DataFrame, excluded: list[str], seed: int = 20260913) -> tuple[dict[str, Any], dict[str, Any], Any]:
    usable = frame.drop(columns=excluded)
    X = usable.drop(columns=["y"])
    y = (usable["y"] == "yes").astype(int)

    split = int(len(frame) * 0.80)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    categorical = X_train.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric = [c for c in X_train.columns if c not in categorical]
    preprocess = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                          ("encode", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    model = Pipeline([
        ("preprocess", preprocess),
        # Preserve probability interpretation. Class imbalance is handled through
        # metric selection, not class weights that distorted calibration in V1 testing.
        ("classifier", LogisticRegression(max_iter=1500, random_state=seed)),
    ])
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    dummy = DummyClassifier(strategy="prior", random_state=seed).fit(np.zeros((len(y_train), 1)), y_train)
    dummy_prob = dummy.predict_proba(np.zeros((len(y_test), 1)))[:, 1]

    auc = float(roc_auc_score(y_test, probabilities))
    positives, negatives = int(y_test.sum()), int((1 - y_test).sum())
    low, high = _auc_ci(auc, positives, negatives)
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    metrics = {
        "n_total": int(len(frame)), "n_train": int(len(y_train)), "n_test": int(len(y_test)),
        "split": "ordered 80/20 holdout; no shuffle",
        "positive_rate_train": float(y_train.mean()), "positive_rate_test": float(y_test.mean()),
        "roc_auc": auc,
        "average_precision": float(average_precision_score(y_test, probabilities)),
        "brier_score": float(brier_score_loss(y_test, probabilities)),
        "balanced_accuracy_at_0_5": float(balanced_accuracy_score(y_test, predictions)),
        "precision_at_0_5": float(precision_score(y_test, predictions, zero_division=0)),
        "recall_at_0_5": float(recall_score(y_test, predictions, zero_division=0)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "baseline_brier_score": float(brier_score_loss(y_test, dummy_prob)),
        "seed": seed,
    }
    metrics["calibration"] = calibration_diagnostics(y_test, probabilities)
    metrics["threshold_analysis"] = threshold_cost_analysis(y_test, probabilities)
    metrics["subgroup_diagnostics"] = subgroup_diagnostics(X_test, y_test, probabilities)
    uncertainty = {
        "roc_auc_95_ci": [low, high],
        "method": "Hanley-McNeil large-sample approximation",
        "warning": "This interval reflects sampling uncertainty under assumptions, not dataset shift or deployment uncertainty.",
    }
    predictions_frame = X_test.copy()
    predictions_frame["actual"] = y_test.values
    predictions_frame["probability"] = probabilities
    return metrics, uncertainty, predictions_frame
