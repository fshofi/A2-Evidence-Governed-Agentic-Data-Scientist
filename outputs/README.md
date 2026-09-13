# Reference outputs

- `reference_standard_report.json`: verified normal run ending in `REQUEST_HUMAN_REVIEW`
- `reference_standard_audit.jsonl`: node-by-node audit trail for that run
- `reference_standard_predictions.csv`: ordered holdout predictions for metric reproduction
- `reference_safe_stop_report.json`: unsupported causal-request run ending in `SAFE_STOP`
- `reference_safe_stop_audit.jsonl`: audit evidence for that refusal

New runs receive unique IDs. Their generated report, audit, and prediction files are ignored by Git unless deliberately promoted to reviewed reference evidence.

