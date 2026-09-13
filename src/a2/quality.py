from __future__ import annotations

import pandas as pd

from .models import Finding, TaskIntake

REQUIRED = {
    "age", "job", "marital", "education", "default", "housing", "loan",
    "contact", "month", "day_of_week", "duration", "campaign", "pdays",
    "previous", "poutcome", "emp.var.rate", "cons.price.idx", "cons.conf.idx",
    "euribor3m", "nr.employed", "y",
}


def assess_quality(frame: pd.DataFrame, task: TaskIntake) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    missing_columns = sorted(REQUIRED - set(frame.columns))
    findings.append(Finding(
        "required_schema", "critical", not missing_columns,
        "all required columns present" if not missing_columns else f"missing: {missing_columns}",
        "restore the pinned schema or provide a reviewed mapping" if missing_columns else None,
    ))
    if missing_columns:
        return findings, []

    nulls = int(frame.isna().sum().sum())
    findings.append(Finding("machine_nulls", "high", nulls == 0, f"{nulls} null cells",
                            "define an explicit imputation or exclusion policy" if nulls else None))
    missing_fraction = float(frame.isna().mean().max())
    findings.append(Finding(
        "severe_column_missingness", "critical", missing_fraction <= 0.40,
        f"maximum column missingness={missing_fraction:.4f}",
        "stop; establish whether the field or affected records are usable" if missing_fraction > 0.40 else None,
    ))

    findings.append(Finding(
        "minimum_sample_support", "critical", len(frame) >= 200,
        f"n={len(frame)}; V1 minimum=200",
        "stop or use a method and uncertainty analysis designed for the small sample" if len(frame) < 200 else None,
    ))

    duplicate_count = int(frame.duplicated().sum())
    findings.append(Finding("duplicate_rows", "medium", duplicate_count == 0,
                            f"{duplicate_count} exact duplicate rows",
                            "review duplicates; do not silently drop potentially repeated contacts" if duplicate_count else None))

    impossible_ages = int(((frame["age"] < 16) | (frame["age"] > 100)).sum())
    findings.append(Finding("age_domain", "high", impossible_ages == 0,
                            f"{impossible_ages} ages outside 16-100",
                            "quarantine invalid rows and confirm domain bounds" if impossible_ages else None))

    disguised_missing = int((frame.select_dtypes(include="object") == "unknown").sum().sum())
    findings.append(Finding("semantic_missingness", "medium", disguised_missing == 0,
                            f"{disguised_missing} categorical values encoded as 'unknown'",
                            "retain as an explicit category and disclose; do not describe the data as free of missing information" if disguised_missing else None))

    target_values = set(frame["y"].dropna().astype(str).unique())
    findings.append(Finding("binary_target", "critical", target_values == {"yes", "no"},
                            f"target values: {sorted(target_values)}",
                            "stop and review target encoding" if target_values != {"yes", "no"} else None))

    suspected_proxies: list[str] = []
    if target_values == {"yes", "no"} and len(frame) >= 200:
        target = frame["y"].astype(str)
        target_numeric = (target == "yes").astype(float)
        for column in frame.columns:
            if column == "y":
                continue
            feature = frame[column]
            normalized = feature.astype(str).str.strip().str.lower()
            if normalized.equals(target.str.strip().str.lower()):
                suspected_proxies.append(column)
                continue
            cardinality = int(feature.nunique(dropna=True))
            if 2 <= cardinality <= 10:
                mapping_width = frame.groupby(column, dropna=False)["y"].nunique(dropna=False)
                if not mapping_width.empty and int(mapping_width.max()) == 1:
                    suspected_proxies.append(column)
                    continue
            if pd.api.types.is_numeric_dtype(feature) and feature.notna().sum() >= 200 and feature.nunique(dropna=True) > 1:
                correlation = feature.astype(float).corr(target_numeric)
                if pd.notna(correlation) and abs(float(correlation)) >= 0.995:
                    suspected_proxies.append(column)
    findings.append(Finding(
        "target_proxy_contamination", "critical", not suspected_proxies,
        "no deterministic or near-perfect target proxy detected" if not suspected_proxies else f"suspected target proxies: {sorted(set(suspected_proxies))}",
        "stop; remove the proxy only after its provenance and availability at the decision moment are reviewed" if suspected_proxies else None,
    ))

    positive_rate = float((frame["y"] == "yes").mean())
    findings.append(Finding("class_balance", "medium", positive_rate >= 0.20,
                            f"positive class prevalence={positive_rate:.4f}",
                            "use imbalance-aware metrics; accuracy alone is inadmissible" if positive_rate < 0.20 else None))

    excluded: list[str] = []
    if task.deployment_moment == "pre_contact" and "duration" in frame.columns:
        excluded.append("duration")
        findings.append(Finding(
            "temporal_leakage_duration", "critical", False,
            "duration is only known after a call; it cannot support pre-contact selection",
            "exclude duration before training and preserve the exclusion in the audit trail",
        ))
    return findings, excluded
