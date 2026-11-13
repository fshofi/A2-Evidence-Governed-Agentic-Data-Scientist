# Current verification — 13 November 2026

15/15 tests pass. A fresh offline model run reproduces ROC AUC 0.7483210368052888, average precision 0.526834200244777 and Brier score 0.19059416629048312. Default status REQUEST_HUMAN_REVIEW, action_authorised=false. Browser leakage example blocks analysis and action. Agents are deterministic services, not live model calls. This is local reproduction, not independent human validation.

Raw test output: `../evidence/client_readiness/unit_tests.txt`.

Test log checkout prefixes are normalised for public sharing. Browser checks: A1 numeric error → REPAIR REQUIRED; A2 leakage → DATA_QUALITY_FAILURE; A3 contradiction → SAFE_STOP and paraphrase → INSUFFICIENT_EVIDENCE, publication false. Desktop rendering inspected; narrow-screen behaviour not interactively tested.
