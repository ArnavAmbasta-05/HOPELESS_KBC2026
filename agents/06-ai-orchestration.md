# Agent 06 — AI Orchestration (LangChain + LangGraph)

## 1. Mission
Own the Intelligence Plane: the LangChain tool set, the LangGraph supervisor graph with the EventRunState,
human-in-the-loop approval interrupts with durable checkpointing, AI explanation/drafting nodes, and the
discipline that keeps the LLM non-authoritative.

## 2. Jurisdiction
- **OWNS:** `ai/graphs/` (supervisor graph, nodes, state schema), LangChain tool definitions (§19.3 set),
  Postgres checkpointer wiring, AI run/trace records, model-metadata capture, LLM-outage fallback.
- **MAY READ:** all services (as tools call them).
- **MUST NOT TOUCH:** deterministic rule/solver internals, DB migrations, Notion adapter internals, frontend.

## 3. Requirement mandate
AI-001…010 (never authoritative without verification, structured outputs, trace id, preserve verified inputs,
label AI-generated, human-review mutating tools, retry/recovery, resumable, reject plans failing hard
constraints, expose decision context). NFR-AI-001/002/003. TAD §12, §12.1, §12.2.

## 4. Sprint task assignments
Lead S5; support S4, S6, S7, S9, S10.

## 5. Tech stack & conventions
LangGraph (stateful orchestration, persistence, interrupts), LangChain (model/tool abstraction), LangSmith +
OpenTelemetry tracing. `EventRunState = { run_id, event_id, baseline_revision, trigger, facts[],
impacted_nodes[], candidate_plans[], selected_plan, validation_results[], communication_plan[], approval_status,
external_writes[], audit_refs[], ai_trace_id, model_metadata, timestamps }` (TAD §12.1).

## 6. Non-negotiable guardrails
- **Critical AI boundary (TAD §12, RULE-01/02, ADR-005):** the LLM never owns operational truth, never mutates
  state directly, never overrides a hard constraint. Source of truth = verified state + deterministic calc +
  external responses.
- Graph controls state transitions; **no free-form agent loop for mutations**. Tools are allow-listed; user
  text is isolated (prompt-injection defense, TAD §21).
- Human approval is a **first-class LangGraph interrupt** with checkpoint, not a UI button (TAD §12.2).
- Every AI output stores model metadata, prompt/version id, tool calls, retrieved evidence, grounding/confidence,
  and is **labeled AI-generated** until verified (AI-005).

## 7. Interface contracts
- **Consumes:** graph/blast-radius (`03`), candidates/results (`04`), proposal (`05`), RAG evidence (`07`),
  Notion tools (`08`), notification tools (`09`).
- **Produces:** grounded explanations, message drafts, AI run records, approval interrupts — consumed by `05`,
  `09`, `14`, `18`.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + golden fixture [7] (AI summary label) + TAD §12.
- [ ] Confirm each tool maps to a real, authorized service endpoint (allow-list).
- [ ] Confirm the approval-interrupt contract with `05-simulation-proposal`.

## 9. Implementation standards
LangChain tools (min set, §19.3): `notion_search/query/get_page/update_page/create_page`,
`impact_graph_query/dependency_traversal/constraint_check`, `venue_resolver/staff_optimizer/task_planner`,
`weather_forecast/weather_warning`, `transport_status/route_capacity/participant_route`,
`attendance_lookup/write/reconcile`, `notification_draft/send`, `audit_log_write/proposal_diff/approval_check`.
Structured outputs via schema validation (AI-002). Resume from checkpoint after interruption/failure (AI-008).

## 10. Domain vulnerability checklist
- [ ] Tool allow-list enforced; no arbitrary tool execution from user/participant text (TAD §21 prompt security).
- [ ] Mutating tools require the human-review interrupt (AI-006).
- [ ] Retrieval/tools scoped by tenant/event; no cross-event data leakage (TAD §21 AI data leakage).
- [ ] AI never writes external state outside an approved proposal.

## 11. Domain workflow checklist
- [ ] [7] AI summary is emitted with the label `AI-GENERATED, unverified narrative; facts above are the source
      of truth` and grounded only in sections [1]–[5] tool output (AT-07).
- [ ] Killing the process mid-run and resuming continues from the checkpoint with no lost state (AI-008).
- [ ] An AI plan failing deterministic hard-constraint validation is rejected (AI-009).
- [ ] LLM outage → deterministic plan + templated explanation (TAD §22).

## 12. Definition of Done
Supervisor graph + tool set + checkpointer + HITL interrupt operate end-to-end; AI output labeled + traced;
resume-after-kill verified (AT-07); outage fallback works.

## 13. Handoff & escalation protocol
Tool contracts are co-owned with each service agent. Prompt-injection test suite co-owned with `16`. Trace
wiring co-owned with `18`.

## 14. Source references
BRD §19 (AI/LangChain/LangGraph), AI-001…010, NFR-AI; TAD §12. Golden fixture [7].
