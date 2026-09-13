# Dataset Decision Record

**Decision:** UCI Bank Marketing, `bank-additional-full.csv`.

**Decision moment:** before the next call.  
**Target:** recorded term-deposit subscription outcome.  
**Permitted V1 output:** retrospective probability estimates and analytical QA for human review.  
**Forbidden inference:** that contact causes subscription.  
**Forbidden action:** automatic contact, eligibility, pricing, credit, or treatment of any person.

The selected source wins by one point over the credit-default candidate because it exposes a crisp, teachable temporal-leakage defect while reducing the likelihood that the demo itself is read as a credit-denial engine. Its temporal ordering, mixed data types, imbalance, disguised missingness, and familiar business question provide enough statistical and governance depth for a 24–48 hour build.

