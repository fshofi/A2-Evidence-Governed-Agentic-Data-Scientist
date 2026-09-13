# A2 Day 2 Hardening Report — V1.1

## Disposition

**HARDENED FOR PORTFOLIO DEMONSTRATION; NOT AUTHORISED FOR OPERATIONAL DEPLOYMENT.**

## What changed

- Added reconstructable calibration bins, expected calibration error, maximum bin error and calibration-in-the-large.
- Added eight-threshold precision, recall, specificity, flagged-volume and illustrative cost sensitivity.
- Added age-band, occupation and contact-channel error diagnostics with minimum-group suppression.
- Added fail-closed target-proxy detection and hostile corrupted-label tests.
- Locked the exact tested Python dependency versions.
- Expanded the evidence dashboard while retaining the human-authority boundary.

## Reference result

The 41,188-record pinned UCI run retains ROC AUC 0.748 and average precision 0.527. Brier score is 0.191 against a 0.273 training-prior baseline. The model's expected calibration error is 0.093 and its worst reliability-bin gap is 0.321. Training prevalence is 6.4% versus 30.8% in the later holdout, an absolute shift of 24.5 percentage points.

These results support bounded retrospective ranking value. They do not support a claim that the probabilities are prospectively calibrated or that the system is ready to select or contact people.

## Adversarial disposition

Target copies, deterministic low-cardinality proxies, near-perfect numeric proxies, invalid target values, missing targets, severe missingness, small samples, tampered source bytes, temporal call-duration leakage and unsupported causal requests are covered by regression tests. Critical contamination remains non-authorising even when the approval flag is supplied.

## Remaining boundary

V1.1 is a defensible, evidence-governed demonstration. It is not an independent validation, fairness audit, causal system, production MLOps implementation, security certification or customer-contact engine. Prospective recalibration and independent human reproduction remain future gates.
