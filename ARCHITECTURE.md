# Architecture

## Decision

V1 uses a deterministic, typed workflow rather than an LLM-controlled multi-agent runtime. Each “agent” is a bounded service with inspectable input, output, and failure behaviour. This is the minimum architecture that proves governance without concealing logic inside prompts.

## State model

`RunState` carries provenance, findings, exclusions, metrics, uncertainty, limitations, evidence chain, analytical completion, approval, and final status. The orchestrator alone orders transitions. The governance gate alone assigns an action-facing state.

Valid public states are:

- `PROCEED`
- `PROCEED_WITH_QUALIFICATION`
- `REQUEST_HUMAN_REVIEW`
- `INSUFFICIENT_EVIDENCE`
- `ASSUMPTION_FAILURE`
- `DATA_QUALITY_FAILURE`
- `SAFE_STOP`

V1 never emits `PROCEED` because no unqualified external action is implemented.

## Trust boundaries

- Network input is not trusted until the pinned archive hash passes.
- Parsed data is not trusted until schema and target checks pass.
- Features are not admissible merely because they improve performance.
- A metric is not a conclusion without uncertainty and limitations.
- A conclusion is not authority.
- An approval flag is logged but has no external connector or execution power.

## Extension boundary

LangGraph may be added when branching, checkpoint recovery, tool isolation, and human-resume semantics exceed the clarity of the current state machine. MCP may be added only for a specific external tool whose identity, permissions, inputs, outputs, revocation, and audit behaviour are defined. Neither is required for V1 credibility.

