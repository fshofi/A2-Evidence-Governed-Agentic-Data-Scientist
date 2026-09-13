# A2 Day 3 Publication Audit

## Disposition

**PASS WITH DECLARED BOUNDARIES**

## Checks completed

| Gate | Result | Evidence |
|---|---|---|
| Secrets and credentials | Pass | No private-key, credential, API-key, token or user-directory pattern found in the publication set |
| Private paths | Pass | No workspace, home-directory or Windows user path found |
| Markdown integrity | Pass | All relative Markdown link targets resolve |
| Python syntax | Pass | Source, runners and dashboard generator compile |
| Automated tests | Pass | 15/15 tests pass |
| Reference run | Pass | 41,188-record offline run reproduces the governed disposition |
| Hostile fixtures | Pass | Target-copy and corrupted-label cases remain non-authorising even with approval |
| Visual inspection | Pass | Architecture plate and static dashboard preview inspected at full resolution |
| Claim boundary | Pass | Production, causal, fairness, legal, security and independent-validation claims are explicitly excluded |
| AI-assistance disclosure | Pass | Material assistance and human responsibility are stated |

## Publication cautions

- The interactive dashboard requires network access to Plotly's public CDN; a static preview is included for offline review.
- The public dataset is separately licensed CC BY 4.0 and must retain creator, DOI and licence attribution.
- “Agentic” refers to bounded coordinated workflow services, not general autonomous reasoning.
- Clean-environment reproduction is not independent human validation.
- The `--approve` flag records a bounded demonstration state; it grants no operational authority and invokes no external action.
