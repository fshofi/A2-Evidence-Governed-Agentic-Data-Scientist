# Evidence Before Action

## A2 — Evidence-Governed Agentic Data Scientist

### Executive summary

A2 is a working, AI-assisted Data Science system built to answer two different questions:

1. Can a model produce a useful statistical result?
2. Is the evidence sufficient and authorised for action?

Using 41,188 historical bank-campaign records, A2 built and tested a pre-contact propensity model. It detected and removed a feature that would have made performance look stronger while answering the wrong operational question. It then found material temporal shift and probability-calibration weakness. The model completed its analysis, but the system correctly withheld authority to act.

**Final disposition:** `REQUEST_HUMAN_REVIEW`  
**Analysis complete:** `TRUE`  
**Action authorised:** `FALSE`

### The problem

A conventional modelling exercise might ask which historical records were most likely to end in a term-deposit subscription. A real decision system must first fix the decision moment. For this demonstration, the question was restricted to information available **before a call** and to bounded human review—not automatic customer contact.

The source contains `duration`, the length of the final call. It is strongly associated with the recorded outcome but is unavailable before the call. Using it for pre-contact selection would be temporal leakage: a technically predictive answer to an inadmissible question.

### What A2 did

- Verified the downloaded archive and analytical CSV against pinned SHA-256 hashes.
- Validated the required schema, target encoding, missing information, duplicates, domains and sample support.
- Detected and excluded post-contact call duration before fitting.
- Preserved the source's stated ordering and evaluated on the final 20% of records.
- Compared an interpretable logistic model with a prior-probability baseline.
- Reported discrimination, probabilistic error, uncertainty, calibration and threshold consequences.
- Examined descriptive error stability across available age bands, occupations and contact channels without claiming fairness certification.
- Required an explicit human-authority state separate from analytical completion.
- Failed closed on unsupported causal language, corrupted outcomes and suspected target proxies.

### Evidence produced

| Measure | Result | Interpretation |
|---|---:|---|
| Records | 41,188 | Full pinned UCI analytical file |
| Ordered holdout | 8,238 | Later 20%; no shuffle |
| ROC AUC | 0.748 | Bounded retrospective ranking value |
| Average precision | 0.527 | More informative than accuracy under imbalance |
| Brier score | 0.191 | Better than 0.273 prior baseline |
| Expected calibration error | 0.093 | Material probability error remains |
| Maximum reliability-bin gap | 0.321 | High-score bands are substantially overconfident |
| Train/holdout prevalence | 6.4% / 30.8% | Severe 24.5-point temporal shift |

The results are exactly reproducible under the pinned reference environment. Fifteen automated tests pass, and the packaged repository was extracted and rerun from a fresh virtual environment.

### The decision

A2 did not convert model output into customer action. The historical shift, poor high-band calibration, missing consent and vulnerability information, illustrative-only error costs and absent accountable operating owner prevent a deployment-readiness claim.

This is the central proof:

> A2 did not merely produce a model; it identified where the model's evidence ceased to justify action.

### Commercial relevance

The same control pattern is relevant wherever predictive output could cross into consequential execution: financial-services triage, fraud operations, insurance, health pathways, public services, safety assurance and autonomous-system review. A client engagement would reconstruct the intended decision moment, permissible evidence, uncertainty, authority boundary, safe-stop conditions and replay record for one bounded workflow.

This repository demonstrates the method. It is not a deployable banking product, causal study, fairness audit, security certification or substitute for legal and accountable-owner review.

### Method and attribution

Dataset: S. Moro, P. Rita and P. Cortez, *Bank Marketing*, UCI Machine Learning Repository, DOI `10.24432/C5K306`, CC BY 4.0. The code is MIT licensed. Development used material generative-AI assistance; Shofi Ahmed Uddin remains responsible for the architecture, statistical judgement, claims and publication.
