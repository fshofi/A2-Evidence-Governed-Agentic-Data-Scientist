# A2 Demonstration Script

## 90-second version

**0:00–0:15 — The distinction**

“A2 is an evidence-governed Data Science system. It separates three things that ordinary demos often collapse: model performance, evidence sufficiency and authority to act.”

**0:15–0:35 — The trap**

“The public bank dataset contains call duration. It is highly predictive, but only known after the call. A pre-contact model that uses it is answering the wrong question. A2 detects and removes that leakage before fitting, and records the exclusion.”

**0:35–0:55 — The evidence**

“On 41,188 pinned records, the admissible model achieved ROC AUC 0.748 and improved Brier score from 0.273 to 0.191. But the later holdout prevalence rose from 6.4% to 30.8%, and the worst calibration-bin error reached 0.321.”

**0:55–1:15 — The governance**

“So A2 finishes the analysis but does not authorise action. It exposes threshold consequences, subgroup stability, uncertainty and limitations, then ends at `REQUEST_HUMAN_REVIEW`. Even an approval flag cannot override corrupted labels or a copied target.”

**1:15–1:30 — The value**

“The value is not another model dashboard. It is a reconstructable boundary showing where evidence stops supporting execution. That pattern can be applied to one bounded workflow in finance, health, public services or autonomous operations.”

## Five-minute walkthrough

1. Open `dashboard/index.html` and identify the three decision cards.
2. Show `duration` in the exclusions and explain the pre-contact decision moment.
3. Compare discrimination with calibration; do not describe AUC as probability accuracy.
4. Show the 24.5-point prevalence shift and the 0.321 maximum calibration-bin gap.
5. Move through the threshold table and state that its 1:5 costs are illustrative.
6. Show subgroup variation, especially that diagnostic variation is not fairness certification.
7. Open `outputs/reference_v1_1_hostile_report.json`: approval is supplied, yet contaminated inputs still fail closed.
8. Finish on `analysis_complete=true` and `action_authorised=false`.

## Questions to invite

- What information is actually available at the intended decision moment?
- Which errors create operational, legal or human harm?
- Who has authority to approve, pause, reverse or retire the workflow?
- What evidence must be preserved so the decision can be reconstructed later?
