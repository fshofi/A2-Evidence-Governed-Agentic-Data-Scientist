# Methodology

## Task

Estimate the probability that a historical campaign record ends in term-deposit subscription using only information admissible before the final call. The result may support bounded human review; it cannot itself authorise contact or another consequential action.

## Data and split

The selected UCI `bank-additional-full.csv` is described as ordered by date. V1 preserves order and uses the first 80% for training and final 20% for holdout evaluation. This reduces the optimism of a random split under temporal change, but is not a full time-series validation because exact timestamps and a prospective sample are unavailable.

## Leakage

Call duration is excluded. It is known only after the call and therefore cannot be used for a pre-contact decision. Retaining it would answer a different, post-contact question.

## Model

Numeric variables receive median imputation and standardisation. Categorical variables receive most-frequent imputation and one-hot encoding with unknown-category tolerance. Logistic regression is unweighted: an initially tested balanced-class-weight specification substantially worsened Brier score and was rejected because the output is presented as a probability. A prior-probability dummy model supplies a calibration baseline. Class imbalance is handled through metric choice rather than a weighting shortcut.

## Metrics

ROC AUC measures ranking across thresholds; average precision is reported because the positive class is a minority; Brier score evaluates probabilistic error; balanced accuracy, precision, recall, and confusion counts are shown at 0.5 only as a transparent reference threshold. No operational threshold is recommended without costs, capacity, consent, and harm criteria.

The 95% ROC AUC interval uses the Hanley-McNeil large-sample approximation. It excludes dataset shift, specification uncertainty, measurement error, and deployment uncertainty.

## V1.1 hardening diagnostics

Calibration is inspected with ten equal-width reliability bins, expected calibration error, maximum bin error and calibration-in-the-large. These summaries are descriptive and bin-dependent. They diagnose, but do not repair, the strong temporal prevalence shift.

Threshold sensitivity is shown at eight thresholds from 0.05 to 0.70. The displayed 1:5 false-positive/false-negative cost ratio is deliberately labelled illustrative. A2 does not choose a threshold because real capacity, consent, harm and accountable-owner criteria are absent.

Subgroup diagnostics report sample size, prevalence, mean predicted probability, Brier score and ROC AUC where estimable for age bands, occupation and contact channel. Groups below 100 holdout observations are suppressed. The fields are incomplete and sometimes proxy-laden; the analysis is not a fairness audit or legal assessment.

The hostile contamination gate detects exact target copies, low-cardinality deterministic proxies and near-perfect numeric proxies. It fails closed before modelling even if human approval is supplied. This is a defensive heuristic, not a substitute for semantic provenance review.
