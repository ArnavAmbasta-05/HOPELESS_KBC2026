# KEOCC Agent Roster & Jurisdiction Map

This folder is the **jurisdiction layer** for building the KIIT EventOps AI Command Center (KEOCC).
Each agent has a single reference file (`NN-<slug>.md`) that it **MUST read before performing any task**
assigned to it in [`../SPRINT_IMPLEMENTATION_PLAN.md`](../SPRINT_IMPLEMENTATION_PLAN.md).

> Source of truth: `KIIT_EventOps_AI_Command_Center_BRD_SRS_v1.0.docx` (BRD/SRS) and
> `KIIT_EventOps_AI_Command_Center_TAD_v1.0.docx` (TAD). The golden regression fixture is
> `kbc03_simulation_output.txt` (the Main Auditorium outage scenario).

## How this works
- Every **task** in the sprint plan is tagged `[Agent: NN-slug]`. That tag points to the agent file here.
- Each `agents/NN-*.md` is the human/AI-readable **jurisdiction contract** (mission, OWNS/READ/MUST-NOT-TOUCH,
  requirement mandate, guardrails, checklists, Definition of Done).
- Each matching `.claude/agents/<slug>.md` is the **Claude Code subagent** definition. Its system prompt simply
  says: *read your `agents/NN-slug.md` + the relevant sprint section first, stay inside your OWNS paths, and
  report handoffs.* The reference doc is the single source of truth — the subagent is the launcher.

## Roster
| # | Agent (slug) | Jurisdiction (OWNS) | Primary requirement mandate |
|---|---|---|---|
| 00 | `orchestrator` | Sprint flow, cross-agent integration, ADR log, `docs/`, RTM | Exit gates, traceability |
| 01 | `platform-devops` | `infra/`, Docker Compose, CI, `.github/`, secret mgmt | NFR-SEC-002, TAD §25–26 |
| 02 | `backend-domain` | `services/api/`, `packages/contracts/`, Event Service, API envelope | FR-EVT, TAD §8/§27 |
| 03 | `data-graph` | `packages/domain/`, Alembic, revisions, Dependency Engine | FR-GRAPH, §18, NFR-PERF-001 |
| 04 | `rules-optimization` | Rules Engine, OR-Tools CP-SAT models, task planner/slack | FR-PLAN, FR-TASK, RULE-01/09 |
| 05 | `simulation-proposal` | Simulation Service, branches, diff, ChangeProposal, approve/commit | FR-SIM, RULE-03/05, ADR-006 |
| 06 | `ai-orchestration` | `ai/graphs/`, LangChain tools, LangGraph HITL, checkpointer | AI-001…010, NFR-AI |
| 07 | `rag-knowledge` | RAG Service, pgvector, post-event report, KnowledgeItem | FR-KB, BR-016, RULE-10 |
| 08 | `notion-integration` | `integrations/notion/`, webhooks, schema map, DLQ | INT-NOT-001…009, AT-06 |
| 09 | `notification-comms` | Notification Service, cohorts, drafting, channel adapters | FR-NOTIFY, COM-001…008 |
| 10 | `transport-mobility` | Transport Service, trips/routes/stops, disruption manager | TRN-001…008, AT-03 |
| 11 | `crowd-safety` | Crowd Service, zones/gates/flows, thresholds, advisories | CRD-001…007, AT-04/05 |
| 12 | `weather-resilience` | Weather Service, IMD/Open-Meteo adapters, weather branches | WX-001…009, AT-02 |
| 13 | `attendance` | Attendance Service, QR/NFC tokens, offline replay | ATT-001…009, RULE-07 |
| 14 | `frontend-command-center` | `apps/web/` command center, dashboards, approval UI | FR-LIVE, NFR-USE |
| 15 | `participant-pwa` | `apps/web/src/participant/`, service worker, offline scan queue | NFR-A11Y-001, ATT/COM UX |
| 16 | `security-privacy` | **Every VULNERABILITY CHECK**, RBAC policy, threat model | NFR-SEC/PRIV, TAD §21 |
| 17 | `qa-workflow` | **Every WORKFLOW CHECK**, `tests/`, golden fixture, AT E2E | TAD §30, AT-01…10 |
| 18 | `observability-sre` | OTel, Prometheus/Grafana, LangSmith, perf/load/resilience | NFR-OBS/REL/PERF, TAD §22–24 |

## RACI by sprint (R = responsible/lead, S = support, A = accountable gate owner)
| Agent \ Sprint | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00 orchestrator | A | A | A | A | A | A | A | A | A | A | A |
| 01 platform-devops | R | S | · | · | · | · | S | · | · | · | S |
| 02 backend-domain | R | R | S | S | R | S | S | S | S | S | S |
| 03 data-graph | S | R | R | R | S | · | · | · | · | S | · |
| 04 rules-optimization | · | · | S | R | S | S | · | · | S | S | · |
| 05 simulation-proposal | · | · | · | S | R | S | R | · | · | S | · |
| 06 ai-orchestration | · | · | · | · | S | R | S | S | · | S | S |
| 07 rag-knowledge | · | · | · | · | · | · | · | · | · | R | S |
| 08 notion-integration | S | · | · | · | · | · | R | · | · | · | S |
| 09 notification-comms | · | · | · | · | · | · | S | R | S | · | · |
| 10 transport-mobility | · | · | · | · | · | · | · | · | R | · | · |
| 11 crowd-safety | · | · | · | · | · | · | · | · | R | · | · |
| 12 weather-resilience | · | · | · | · | · | · | · | · | · | R | · |
| 13 attendance | · | · | · | · | · | · | · | R | S | · | · |
| 14 frontend-command-center | · | · | · | · | R | S | S | S | R | S | S |
| 15 participant-pwa | · | · | · | · | · | · | · | R | S | · | S |
| 16 security-privacy | R | S | S | S | S | R | S | R | S | S | R |
| 17 qa-workflow | S | S | R | S | S | S | S | S | S | S | R |
| 18 observability-sre | R | · | S | · | · | S | · | · | · | · | R |

## Handoff & escalation protocol
1. **Stay in your lane.** An agent edits only files under its OWNS list. A change needed outside your
   jurisdiction is a **handoff**: describe the required change and the target agent, and route it through
   `00-orchestrator`.
2. **Contracts are the seams.** Cross-agent data moves only through the typed contracts in
   `packages/contracts/` (owned by `02-backend-domain`) and the adapter contract in TAD §27.4. Changing a
   shared contract requires orchestrator sign-off and a note to every downstream consumer.
3. **Gates are non-negotiable.** `16-security-privacy` signs every **VULNERABILITY CHECK**; `17-qa-workflow`
   signs every **WORKFLOW CHECK**. A sprint does not exit until both are green and the orchestrator confirms
   the exit gate.
4. **The AI boundary is absolute (RULE-01, RULE-02, ADR-005).** No agent lets an LLM mutate operational state,
   override a hard constraint, or write externally without the human-approval interrupt.

## Global guardrails every agent inherits (BRD §27 / TAD §21, §12)
- **RULE-01** Hard constraints (capacity, time overlap, safety, authorization) cannot be traded away by AI.
- **RULE-02** AI output is non-authoritative until verified/approved; always labeled AI-generated.
- **RULE-03** A simulation branch must exist before any bulk external change (Notion write, mass notify).
- **RULE-04** Rejected alternatives are retained with concrete reasons.
- **RULE-05** Participant impact is evaluated before committing event changes.
- **RULE-07** Attendance never silently changes registration state.
- **RULE-08** Stale external sources are labeled stale, never shown as current.
- **RULE-09** No feasible plan → explicit infeasible state + manual action queue (never a silent failure).
- Every external write is **idempotent, verified, audited, and linked to an approved proposal**.
