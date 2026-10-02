# KIIT EventOps AI Command Center (KEOCC) — Sprint Implementation Plan

> **Problem statement:** KBC-NOTION-03 — an AI-powered event digital twin, operational command center, simulation
> and adaptive-response platform for KIIT.
> **Source baseline:** `KIIT_EventOps_AI_Command_Center_BRD_SRS_v1.0.docx` (BRD/SRS v1.0) and
> `KIIT_EventOps_AI_Command_Center_TAD_v1.0.docx` (TAD v1.0).
> **Golden regression fixture:** `kbc03_simulation_output.txt` (Main Auditorium outage).
> **Agent layer:** see [`agents/`](agents/) — every task below is tagged `[Agent: NN-slug]`; that agent **must
> read its `agents/NN-slug.md` contract and this sprint section before starting**.

---

## 1. Document control
| Item | Value |
|---|---|
| Plan version | 1.0 |
| Date | 2026-10-02 |
| Cadence | Hackathon-compressed, 2–3 working days per sprint (≈29 days total, S0–S10) |
| Standards basis | ISO/IEC/IEEE 29148 (requirements), 42010 (architecture), OWASP ASVS (security) |
| Gate owners | `16-security-privacy` signs every VULNERABILITY CHECK; `17-qa-workflow` signs every WORKFLOW CHECK; `00-orchestrator` signs every exit gate |

---

## 2. Delivery strategy

**The core loop** (every trigger — operator entry, Notion webhook, weather, transport, crowd, attendance — drives
the same engine):

```
detect → impact (blast radius) → simulate (branch) → explain (AI, labeled) → approve (human interrupt)
       → execute (idempotent, verified) → notify (cohort-targeted) → monitor (reconcile + learn)
```

**Golden path first.** The Main Auditorium venue-outage scenario (`kbc03_simulation_output.txt`) is the primary
vertical slice and the primary regression fixture. Weather, transport, crowd and attendance are then added as four
additional signals that independently trigger the same loop.

**Demo cut line.** Sprints **S0–S7 are mandatory** (the complete golden vertical slice + participant ops). Sprints
**S8–S10 are the representative extensions + hardening**; if time runs short they degrade in depth, not in whether
the core loop works.

**Deterministic core, AI-assisted edge.** Hard constraints, state mutation and irreversible external actions are
deterministic, policy-controlled and auditable (RULE-01, ADR-005). The LLM interprets, summarizes and proposes —
labeled AI-generated — and never owns operational truth.

---

## 3. Agent roster & RACI
See [`agents/README.md`](agents/README.md) for the full roster, jurisdiction map, RACI matrix and handoff
protocol. The 19 agents: `00-orchestrator`, `01-platform-devops`, `02-backend-domain`, `03-data-graph`,
`04-rules-optimization`, `05-simulation-proposal`, `06-ai-orchestration`, `07-rag-knowledge`,
`08-notion-integration`, `09-notification-comms`, `10-transport-mobility`, `11-crowd-safety`,
`12-weather-resilience`, `13-attendance`, `14-frontend-command-center`, `15-participant-pwa`,
`16-security-privacy`, `17-qa-workflow`, `18-observability-sre`.

---

## 4. Conventions
- **Task IDs:** `S{n}-T{m}`; **subtasks:** `S{n}-T{m}.{k}`, written as `- [ ]` checkboxes.
- **Agent tag:** every task carries `[Agent: NN-slug]` (lead). Support agents are noted in the task table.
- **Dependencies:** listed per task (`depends: …`).
- **Global Definition of Done (applies to every task):** code + tests merged; CI green (lint, type, unit,
  integration, scans); contracts updated if the seam changed; audit events emitted for mutations; requirement IDs
  traced in the RTM; VULNERABILITY CHECK + WORKFLOW CHECK for the sprint signed.
- **Every sprint section contains:** Goal · Duration · Requirement coverage · Lead/support agents · Task table →
  subtasks · **DELIVERABLES** · **VULNERABILITY CHECK** · **WORKFLOW CHECK** · Exit gate.

---

# Sprints

## Sprint 0 — Foundations
**Goal:** a running skeleton: monorepo, local stack, CI, auth abstraction, RBAC + observability skeleton, and the
KIIT synthetic seed that makes the golden scenario reproducible.
**Duration:** 2 days · **Requirement coverage:** NFR-SEC-002, NFR-EXT-001, NFR-MNT-001, NFR-OBS-001, data seed for
the golden fixture · **Lead:** 01-platform-devops · **Support:** 02-backend-domain, 18-observability-sre,
16-security-privacy, 03-data-graph, 08-notion-integration

| Task | Description | Agent | Depends |
|---|---|---|---|
| S0-T1 | Monorepo + tooling | 01-platform-devops | — |
| S0-T2 | Docker Compose stack | 01-platform-devops | S0-T1 |
| S0-T3 | CI/CD pipeline + scans | 01-platform-devops | S0-T1 |
| S0-T4 | Auth abstraction + RBAC skeleton | 16-security-privacy (+02) | S0-T1 |
| S0-T5 | Observability skeleton | 18-observability-sre | S0-T2 |
| S0-T6 | KIIT synthetic seed + golden fixture | 03-data-graph (+08) | S0-T2 |

- **S0-T1** Monorepo + tooling `[Agent: 01-platform-devops]`
  - [ ] S0-T1.1 Create `apps/web`, `services/api`, `services/workers`, `packages/domain`, `packages/contracts`, `ai/graphs`, `integrations/`, `infra/`, `tests/`, `docs/`.
  - [ ] S0-T1.2 Python 3.12 toolchain: `pyproject.toml`, Ruff, MyPy/Pyright, pre-commit; Node/Vite for `apps/web`.
  - [ ] S0-T1.3 `.gitignore`, `.env.example` (keys, **no values**), `README`, code owners per package.
- **S0-T2** Docker Compose stack `[Agent: 01-platform-devops]`
  - [ ] S0-T2.1 Services: `web`, `api`, `worker`, `postgres` (18 + pgvector), `redis`, `minio`.
  - [ ] S0-T2.2 Health checks, readiness/liveness probes, `make up` / `make down`.
- **S0-T3** CI/CD + scans `[Agent: 01-platform-devops]` (depends S0-T1)
  - [ ] S0-T3.1 GitHub Actions: Ruff → MyPy → pytest → Trivy → secret scan → build.
  - [ ] S0-T3.2 Protected `main`, required checks, Dependabot/Renovate.
- **S0-T4** Auth abstraction + RBAC skeleton `[Agent: 16-security-privacy]` (support 02; depends S0-T1)
  - [ ] S0-T4.1 OIDC/SSO adapter interface + dev login; short-lived tokens.
  - [ ] S0-T4.2 Server-side policy engine stub with the 11 roles (BRD §6); default-deny.
- **S0-T5** Observability skeleton `[Agent: 18-observability-sre]` (depends S0-T2)
  - [ ] S0-T5.1 OpenTelemetry traces/metrics/logs; correlation-ID middleware.
  - [ ] S0-T5.2 Prometheus + Grafana + structured JSON logging wired in Compose.
- **S0-T6** KIIT synthetic seed + golden fixture `[Agent: 03-data-graph]` (support 08; depends S0-T2)
  - [ ] S0-T6.1 Seed venues (Main Auditorium, Open Air Theatre, Seminar Hall cap 250, LH-3 150, LH-5 120), the 4 sessions with times/registrants (380/230/180/390), 16 volunteer assignments (incl. Arjun standby), speakers with arrival buildings, equipment (stage-light rig, projector+screen in Store), tasks and public comms.
  - [ ] S0-T6.2 Copy `kbc03_simulation_output.txt` → `tests/fixtures/golden_main_auditorium/` and record expected values.
  - [ ] S0-T6.3 Stub Notion sandbox workspace config (schema-map placeholder).

**DELIVERABLES:** running Compose stack; green CI with scans; auth + RBAC skeleton; OTel/Grafana up; seed dataset +
golden fixture committed; `.env.example`; monorepo scaffold.

**VULNERABILITY CHECK** *(sign-off: 16-security-privacy)*
- [ ] Secret scan enabled and blocking; no real secrets committed; `.env` git-ignored.
- [ ] Dependency + container scanning green (Dependabot/Renovate + Trivy).
- [ ] RBAC skeleton is default-deny; dev login clearly non-production.
- [ ] No credentials in Compose files or frontend bundle.

**WORKFLOW CHECK** *(sign-off: 17-qa-workflow)*
- [ ] `docker compose up` → all services report healthy.
- [ ] CI runs green on a clean checkout; a seeded lint/type/test failure blocks merge.
- [ ] Seed loads; a smoke test confirms the golden entities exist with the exact capacities/registrant counts.

**Exit gate:** all services run locally, CI green, seed + golden fixture present. *(TAD roadmap P0.)*

---

## Sprint 1 — Event Digital Twin (entities, revisions, audit)
**Goal:** the operational system of record — all core entities with revisions/optimistic concurrency, CRUD APIs
with the standard envelope and idempotency, and an append-only Audit Service.
**Duration:** 2 days · **Requirement coverage:** FR-EVT-001…005, §18 data + §18.2 quality rules, BR-015 (audit),
NFR-REL-002, NFR-SEC-001, BR-018 isolation · **Lead:** 03-data-graph, 02-backend-domain · **Support:**
16-security-privacy

| Task | Description | Agent | Depends |
|---|---|---|---|
| S1-T1 | Core entity models + migrations | 03-data-graph | S0-T6 |
| S1-T2 | Revisions + optimistic concurrency | 03-data-graph | S1-T1 |
| S1-T3 | CRUD APIs + envelope + idempotency | 02-backend-domain | S1-T1 |
| S1-T4 | Audit Service (append-only) | 03-data-graph | S1-T1 |
| S1-T5 | RBAC on endpoints | 16-security-privacy | S1-T3 |

- **S1-T1** Core entity models + migrations `[Agent: 03-data-graph]`
  - [ ] S1-T1.1 Model every §18.1 entity (Event, Session, Venue, Participant, Volunteer, Resource, Vehicle, Route, Task, Notification, AttendanceRecord, WeatherSignal, ChangeProposal, DependencyEdge, Incident/Escalation, KnowledgeItem).
  - [ ] S1-T1.2 Canonical IDs (TAD §20.1); timezone-normalized times; numeric validated capacity; source + last-updated metadata fields (§18.2).
  - [ ] S1-T1.3 Alembic migrations, reversible.
- **S1-T2** Revisions + optimistic concurrency `[Agent: 03-data-graph]`
  - [ ] S1-T2.1 `revision_id` per aggregate; bump on write; superseded records retained (§18.2).
  - [ ] S1-T2.2 Event-level tenant scoping on all queries (BR-018).
- **S1-T3** CRUD APIs + envelope + idempotency `[Agent: 02-backend-domain]`
  - [ ] S1-T3.1 `/events /sessions /venues /participants /resources` CRUD; standard envelope (TAD §27.1).
  - [ ] S1-T3.2 `Idempotency-Key` on mutations; `If-Match` revision for updates (409 on stale).
  - [ ] S1-T3.3 Cursor pagination, correlation IDs, structured error envelope, OpenAPI docs.
- **S1-T4** Audit Service `[Agent: 03-data-graph]`
  - [ ] S1-T4.1 Append-only audit table (actor, action, before/after refs, trace id); no UPDATE/DELETE path.
  - [ ] S1-T4.2 Audit hook invoked by every mutation handler.
- **S1-T5** RBAC on endpoints `[Agent: 16-security-privacy]` (depends S1-T3)
  - [ ] S1-T5.1 Policy rules per role × endpoint; default-deny; server-side enforcement.

**DELIVERABLES:** entity models + migrations; revisioned CRUD APIs with envelope/idempotency/ETag; append-only
audit; RBAC policy for S1 endpoints; OpenAPI docs.

**VULNERABILITY CHECK** *(16)*
- [ ] RBAC enforced server-side on every endpoint; default-deny verified by test.
- [ ] Parameterized queries only; no mass-assignment of protected fields.
- [ ] Idempotency keys prevent duplicate mutations/replay (NFR-REL-002).
- [ ] Audit table append-only; participant PII minimized in models/responses (NFR-PRIV-001).

**WORKFLOW CHECK** *(17)*
- [ ] Create → read → update → list for each entity returns the correct envelope + revision.
- [ ] Stale `If-Match` returns 409 (the AT-06 conflict primitive).
- [ ] Every mutation produces exactly one audit record with actor + before/after refs.
- [ ] Two events are fully isolated (BR-018).

**Exit gate:** CRUD + audit pass with revision-conflict handling tested. *(TAD roadmap P1 start.)*

---

## Sprint 2 — Dependency engine & blast radius
**Goal:** the Event Digital Twin becomes dependency-aware — typed edges and a recursive-CTE blast radius that
reproduces golden section [1] within the performance target.
**Duration:** 2 days · **Requirement coverage:** FR-GRAPH-001…005, NFR-PERF-001, BR-002 · **Lead:** 03-data-graph
· **Support:** 17-qa-workflow, 18-observability-sre, 04-rules-optimization

| Task | Description | Agent | Depends |
|---|---|---|---|
| S2-T1 | Typed edge model | 03-data-graph | S1-T1 |
| S2-T2 | Recursive-CTE blast radius | 03-data-graph | S2-T1 |
| S2-T3 | Deferred soft-edge re-eval | 03-data-graph | S2-T2 |
| S2-T4 | Golden regression harness | 17-qa-workflow | S2-T2 |
| S2-T5 | Perf benchmark | 18-observability-sre | S2-T2 |

- **S2-T1** Typed edge model `[Agent: 03-data-graph]`
  - [ ] S2-T1.1 Edge types (TAD §9): `hosts, task_at, mentions, has_registrants, assigned, needs, served_by, occupies, exposed_to`; indexed `source_id, target_id, edge_type, validity_interval`.
  - [ ] S2-T1.2 Build the golden graph from seed (sessions↔venue, tasks↔venue, comms↔venue, cohorts↔sessions).
- **S2-T2** Recursive-CTE blast radius `[Agent: 03-data-graph]`
  - [ ] S2-T2.1 Bounded recursive-CTE traversal from a changed object; mark affected / unaffected / deferred.
  - [ ] S2-T2.2 Return the edge path connecting the change to each impacted object (FR-GRAPH-004).
  - [ ] S2-T2.3 Time-window constraint (session falls inside the unavailability window).
- **S2-T3** Deferred soft-edge re-eval `[Agent: 03-data-graph]`
  - [ ] S2-T3.1 Defer soft edges (speakers, staffing) and re-evaluate after primary resolution (FR-GRAPH-005).
- **S2-T4** Golden regression harness `[Agent: 17-qa-workflow]`
  - [ ] S2-T4.1 Assert exactly 12 hard hits (4 `hosts`, 2 `task_at`, 2 `mentions`, 4 `has_registrants` = 380/230/180/390) + 7 deferred soft edges.
- **S2-T5** Perf benchmark `[Agent: 18-observability-sre]`
  - [ ] S2-T5.1 Synthetic 5,000-edge graph; assert blast radius ≤5 s (NFR-PERF-001); index tuning.

**DELIVERABLES:** typed edge model + indexes; blast-radius engine with traversal paths; deferred soft-edge
re-eval; golden [1] regression test; perf benchmark report.

**VULNERABILITY CHECK** *(16)*
- [ ] Recursive CTEs are parameterized; traversal is depth/row-bounded (no runaway/DoS).
- [ ] Traversal honors event-tenant isolation.
- [ ] Blast-radius API enforces RBAC (read scope).

**WORKFLOW CHECK** *(17)*
- [ ] Golden [1]: Main Auditorium unavailable 08:00–23:59 → the 4 sessions (Opening 10:00, Keynote 11:00, Panel 14:00, Prize 17:00), the 2 `task_at` tasks (AV setup in_progress, Stage décor pending), the 2 `mentions` (Instagram post, Gate 1/Gate 3 boards), and the 4 cohorts are returned — and nothing else as hard hits.
- [ ] 7 soft edges (VC, Dr. Mehra, 3 founders, volunteer staffing) are deferred, not resolved yet.
- [ ] Perf target met on the 5k-edge benchmark.

**Exit gate:** golden affected set reproduced deterministically within ≤5 s. *(TAD roadmap P1 exit.)*

---

## Sprint 3 — Rules, optimization & task planning
**Goal:** deterministic resolution — constraint evaluation, venue resolver with retained rejection reasons, CP-SAT
volunteer reallocation, the 17-task plan with slack, escalations, and the explicit infeasible path.
**Duration:** 3 days · **Requirement coverage:** FR-PLAN-001…005, FR-TASK-001…006, RULE-01/04/09, NFR-AI-003,
AT-09 · **Lead:** 04-rules-optimization · **Support:** 03-data-graph

| Task | Description | Agent | Depends |
|---|---|---|---|
| S3-T1 | Constraint evaluator (Rules Engine) | 04-rules-optimization | S2-T2 |
| S3-T2 | Venue resolver + rejection reasons | 04-rules-optimization | S3-T1 |
| S3-T3 | CP-SAT volunteer reallocation | 04-rules-optimization | S3-T1 |
| S3-T4 | Task planner (slack) + escalations | 04-rules-optimization | S3-T2 |
| S3-T5 | Infeasible state + manual queue | 04-rules-optimization | S3-T2 |

- **S3-T1** Constraint evaluator `[Agent: 04-rules-optimization]`
  - [x] S3-T1.1 Hard constraints: capacity, time overlap, required capability, policy/safety, authorization (RULE-01).
  - [x] S3-T1.2 Versioned rule/threshold config (NFR-MNT-001); state→typed-variables conversion for the solver.
- **S3-T2** Venue resolver + rejection reasons `[Agent: 04-rules-optimization]`
  - [x] S3-T2.1 Candidate generation + scoring (minimize move cost/walking/setup).
  - [x] S3-T2.2 Retain every rejected candidate with a concrete reason string (RULE-04, FR-PLAN-003).
  - [x] S3-T2.3 Soft re-eval of speakers (arrival-building change → escort needed).
- **S3-T3** CP-SAT volunteer reallocation `[Agent: 04-rules-optimization]`
  - [x] S3-T3.1 CP-SAT model: hard (skill/availability/overlap/headcount), objective (minimize changes, then load).
  - [x] S3-T3.2 Standby activation when headcount requires it.
- **S3-T4** Task planner + escalations `[Agent: 04-rules-optimization]`
  - [x] S3-T4.1 Generate follow-up tasks (owner/team, window, deadline, dependency); EDF per team.
  - [x] S3-T4.2 Slack = deadline − finish; flag zero/negative slack AT RISK (FR-TASK-003).
  - [x] S3-T4.3 Escalate at-risk tasks to configured role owners (FR-TASK-006).
- **S3-T5** Infeasible state + manual queue `[Agent: 04-rules-optimization]`
  - [x] S3-T5.1 No candidate satisfies hard constraints → explicit infeasible result + constraint reasons + ranked manual actions (RULE-09, FR-PLAN-005).

**DELIVERABLES:** Rules Engine; venue resolver with rejection trace; CP-SAT volunteer model; task planner with
slack + escalations; infeasible handler; versioned rule config.

**VULNERABILITY CHECK** *(16)*
- [x] No rule/threshold hard-coded where it must be config; no path for free-text to alter constraints.
- [x] Solver inputs typed/validated; infeasible + timeout paths fail closed (never emit an unsafe plan).
- [x] Safety/authorization hard constraints co-reviewed and enforced outside any LLM (NFR-AI-003).

**WORKFLOW CHECK** *(17)* — golden sections [2]–[5]
- [x] [2] Opening→Open Air Theatre (+stage-light rig), Keynote→Seminar Hall, Panel→Open Air Theatre (+projector/screen), Prize→Open Air Theatre (+stage-light rig); rejections retained: Seminar Hall (250), LH-3 (150), LH-5 (120) with `capacity X < N registered`, and Panel's Seminar Hall rejected "already booked in this slot".
- [x] [2] VC (Bldg A→C) + Startup panel (Bldg B→C) → escort needed; Dr. Mehra → no action.
- [x] [3] −Dev off Keynote AV; +Kabir Prize, +Tanya Opening, +Meera Panel (crowd); +Arjun Keynote AV **standby**; **15 of 16 untouched**.
- [x] [4] 17 tasks N01–N17 with slack; **N08 "Opening act rehearsal at OAT" slack 0m → AT RISK**.
- [x] [5] Escalation: N08 → stage lead.
- [x] AT-09: with no venue meeting capacity, returns infeasible + reasons + manual queue.

**Exit gate:** golden [2]–[5] reproduced exactly; AT-09 passes.

---

## Sprint 4 — Simulation, Change Proposal & approval (+ Command Center v1)
**Goal:** what-if before commit — branches, baseline/proposed diff, risk, the assembled Change Proposal, the
approve/reject API, and the first command-center UI to review and approve it.
**Duration:** 3 days · **Requirement coverage:** FR-SIM-001…006, RULE-03/05, FR-LIVE-001…004, NFR-USE, ADR-006,
AT-08 · **Lead:** 05-simulation-proposal, 14-frontend-command-center · **Support:** 02-backend-domain

| Task | Description | Agent | Depends |
|---|---|---|---|
| S4-T1 | Simulation branches + diff | 05-simulation-proposal | S3-T4 |
| S4-T2 | Risk calc + Change Proposal assembly | 05-simulation-proposal | S4-T1 |
| S4-T3 | Approve/reject API | 02-backend-domain | S4-T2 |
| S4-T4 | Command Center dashboard + impact graph | 14-frontend-command-center | S2-T2 |
| S4-T5 | Proposal review + approval UI | 14-frontend-command-center | S4-T2 |

- **S4-T1** Simulation branches + diff `[Agent: 05-simulation-proposal]`
  - [x] S4-T1.1 Branch with unique id + deterministic input snapshot referencing a baseline revision; baseline never overwritten (FR-SIM-001/002).
  - [x] S4-T1.2 Baseline↔proposed diff: added/removed/changed objects (FR-SIM-003).
- **S4-T2** Risk + Change Proposal `[Agent: 05-simulation-proposal]`
  - [x] S4-T2.1 Risk plan: at-risk tasks + unresolved dependencies (FR-SIM-004).
  - [x] S4-T2.2 Assemble Change Proposal with every TAD §10 artifact (baseline, trigger, blast radius, candidates ±reasons, optimization result, operational plan, communication plan, risk plan, diff, approval state, commit result).
- **S4-T3** Approve/reject API `[Agent: 02-backend-domain]`
  - [x] S4-T3.1 `POST /proposals/{id}/approve|reject` with `Idempotency-Key` + `If-Match`; RBAC authorized actor; audited.
  - [x] S4-T3.2 Behavior (TAD §27.2): validate permissions → validate proposal → execute plan → verify → audit.
- **S4-T4** Command Center dashboard + impact graph `[Agent: 14-frontend-command-center]`
  - [x] S4-T4.1 Role-aware dashboard; live status tiles with last-updated + source (FR-LIVE-002).
  - [x] S4-T4.2 Dependency-graph + timeline + risk-heatmap views; alert drill-down to object + chain (FR-LIVE-004).
- **S4-T5** Proposal review + approval UI `[Agent: 14-frontend-command-center]`
  - [x] S4-T5.1 Render diff + candidates (incl. rejected w/ reasons) + risk; approve/reject actions.
  - [x] S4-T5.2 Commander sees status + top risks in ≤2 views (NFR-USE-001); every alert shows next action (NFR-USE-002).

**DELIVERABLES:** simulation branch + diff + risk; Change Proposal assembler; approve/reject API; Command Center
v1 (dashboard, impact graph, proposal review, approval).

**VULNERABILITY CHECK** *(16)*
- [x] No commit path bypasses the approval gate; approval requires an authorized actor and is audited.
- [x] Commit is idempotent and refuses to blindly re-run a prior external mutation (TAD §22).
- [x] Frontend stores no credentials; approval is enforced server-side (hidden buttons are not authz).

**WORKFLOW CHECK** *(17)*
- [x] What-if end-to-end: trigger → branch → diff → Change Proposal with golden candidates/tasks/risk.
- [x] AT-08: rejecting the proposal produces **zero** writes and leaves baseline untouched.
- [x] The proposal UI shows the rejected venue options with their concrete reasons (explainability).

**Exit gate:** what-if works end-to-end; AT-08 passes (without Notion yet). *(TAD roadmap P2 exit.)*

---

## Sprint 5 — AI orchestration (LangChain + LangGraph, HITL)
**Goal:** the Intelligence Plane — LangChain tools, the LangGraph supervisor graph with EventRunState, the
human-approval interrupt with durable checkpointing, AI explanation/drafting (labeled + traced), and outage
fallback.
**Duration:** 3 days · **Requirement coverage:** AI-001…010, NFR-AI-001/002/003, BR-014, AT-07 · **Lead:**
06-ai-orchestration · **Support:** 16-security-privacy, 18-observability-sre

| Task | Description | Agent | Depends |
|---|---|---|---|
| S5-T1 | LangChain tool set | 06-ai-orchestration | S3-T2, S4-T2 |
| S5-T2 | LangGraph supervisor + EventRunState | 06-ai-orchestration | S5-T1 |
| S5-T3 | HITL interrupt + checkpointer | 06-ai-orchestration | S5-T2, S4-T3 |
| S5-T4 | AI explainer/drafter (labeled, traced) | 06-ai-orchestration | S5-T2 |
| S5-T5 | Prompt-injection guard + tool allow-list | 16-security-privacy | S5-T1 |
| S5-T6 | AI tracing + outage fallback | 18-observability-sre (+06) | S5-T2 |

- **S5-T1** LangChain tool set `[Agent: 06-ai-orchestration]`
  - [x] S5-T1.1 Implement the §19.3 minimum tools, each wrapping a real authorized endpoint (notion_*, impact_graph_query/dependency_traversal/constraint_check, venue_resolver/staff_optimizer/task_planner, weather_*, transport_*, attendance_*, notification_draft/send, audit_log_write/proposal_diff/approval_check).
  - [x] S5-T1.2 Structured outputs with schema validation (AI-002).
- **S5-T2** LangGraph supervisor + state `[Agent: 06-ai-orchestration]`
  - [x] S5-T2.1 `EventRunState` (TAD §12.1); supervisor routes the request; deterministic nodes for hard constraints/actions, AI nodes for explain/draft.
  - [x] S5-T2.2 No free-form agent loop for mutations (graph controls transitions).
- **S5-T3** HITL interrupt + checkpointer `[Agent: 06-ai-orchestration]`
  - [x] S5-T3.1 Postgres checkpointer; approval modeled as a LangGraph interrupt (TAD §12.2).
  - [x] S5-T3.2 Resume the same thread on approve/reject — from the in-app endpoint (S4-T3) and later Notion status (S6).
- **S5-T4** AI explainer/drafter `[Agent: 06-ai-orchestration]`
  - [x] S5-T4.1 Impact explainer + plan analyst + communications drafter grounded only in tool output (never invents candidates).
  - [x] S5-T4.2 Label every AI output AI-generated; store model metadata, prompt version, tool calls, evidence, grounding status (AI-003/004/005).
  - [x] S5-T4.3 Reject AI plans that fail deterministic hard-constraint validation (AI-009).
- **S5-T5** Prompt-injection guard + allow-list `[Agent: 16-security-privacy]`
  - [x] S5-T5.1 Tool allow-list; isolate user/participant text; no arbitrary tool execution; tenant/event scoping (TAD §21).
  - [x] S5-T5.2 Prompt-injection + mutating-tool-requires-approval test suite (AI-006).
- **S5-T6** AI tracing + outage fallback `[Agent: 18-observability-sre]` (support 06)
  - [x] S5-T6.1 LangSmith + OTel trace per run (`trace_id, proposal_id, run_id`); 100% AI outputs tied to a trace (AI-003).
  - [x] S5-T6.2 LLM outage → deterministic plan + templated explanation (TAD §22); retry/recovery (AI-007).

**DELIVERABLES:** LangChain tool set; LangGraph supervisor + EventRunState; HITL interrupt + checkpointer; labeled
+ traced AI explanation/drafts; prompt-injection guard; outage fallback.

**VULNERABILITY CHECK** *(16)* — **sprint focus: prompt injection & AI boundary**
- [x] Tool allow-list enforced; user text cannot trigger an unauthorized tool call or state mutation.
- [x] Mutating tools require the human-review interrupt; AI never writes external state outside an approved proposal.
- [x] Retrieval/tools scoped by tenant/event; no cross-event leakage.
- [x] AI output never presented as verified truth (RULE-02); hard constraints enforced outside the LLM (NFR-AI-003).

**WORKFLOW CHECK** *(17)*
- [x] AT-07: the AI summary is emitted with the exact label `AI-GENERATED, unverified narrative; facts above are the source of truth`, grounded only in golden [1]–[5] tool output.
- [x] Kill the process mid-run → resume from checkpoint with no lost state (AI-008).
- [x] An AI plan violating a hard constraint is rejected (AI-009); LLM-down path yields the deterministic + templated result.

**Exit gate:** AT-07 passes; resume-after-kill verified. *(TAD roadmap P3 exit.)*

---

## Sprint 6 — Notion live integration (golden vertical slice complete)
**Goal:** close the loop to Notion — the adapter contract, webhook-driven inbound sync, idempotent verified
outbound writes, refresh-before-commit conflict detection, DLQ, and the Impact Report page. After this sprint the
full golden slice (detect→…→commit) runs against a live sandbox workspace.
**Duration:** 3 days · **Requirement coverage:** INT-NOT-001…009, AT-01, AT-06, AT-08, BR-012 · **Lead:**
08-notion-integration · **Support:** 05-simulation-proposal, 02-backend-domain, 06-ai-orchestration

| Task | Description | Agent | Depends |
|---|---|---|---|
| S6-T1 | Notion adapter contract | 08-notion-integration | S0-T6 |
| S6-T2 | Inbound webhook sync + re-fetch | 08-notion-integration | S6-T1 |
| S6-T3 | Outbound idempotent writes + verify | 08-notion-integration | S6-T1, S5-T3 |
| S6-T4 | Refresh-before-commit + conflict | 08-notion-integration | S6-T3 |
| S6-T5 | DLQ + Impact Report page | 08-notion-integration | S6-T3 |
| S6-T6 | Commit wiring (proposal → Notion) | 05-simulation-proposal | S6-T3 |

- **S6-T1** Adapter contract `[Agent: 08-notion-integration]`
  - [x] S6-T1.1 Implement TAD §27.4: `connect/pull_changes(cursor)/push(plan)/verify(ids)/health/translate_error`.
  - [x] S6-T1.2 Configurable property map versioned per workspace/data source; database-vs-data-source object model (TAD §14).
  - [x] S6-T1.3 Least-privilege scoped token in secret manager (INT-NOT-001).
- **S6-T2** Inbound webhook sync `[Agent: 08-notion-integration]`
  - [x] S6-T2.1 Webhook receiver → signature verify → queue → **re-fetch authoritative page/data-source state** → normalize → state revision (TAD §14; INT-NOT-004).
  - [x] S6-T2.2 Sync cursor persistence.
- **S6-T3** Outbound writes + verify `[Agent: 08-notion-integration]`
  - [x] S6-T3.1 Approved proposal → write plan → idempotent adapter (external IDs) → verify() post-write → mark committed (INT-NOT-003/008).
  - [x] S6-T3.2 Token-bucket rate limiter (~3 req/s) + exponential backoff + retry-after (INT-NOT-009).
- **S6-T4** Refresh-before-commit + conflict `[Agent: 08-notion-integration]`
  - [x] S6-T4.1 Compare `source_revision`/`last_synced_at`; block commit on stale/conflict (INT-NOT-005).
- **S6-T5** DLQ + Impact Report `[Agent: 08-notion-integration]`
  - [x] S6-T5.1 Dead-letter queue + operator-visible integration incident on failure.
  - [x] S6-T5.2 Write the Impact Report + change summary page after approval (INT-NOT-007).
- **S6-T6** Commit wiring `[Agent: 05-simulation-proposal]`
  - [x] S6-T6.1 On approval (in-app endpoint **or** Notion Change-Proposal Status=Approved) resume the LangGraph thread and execute the Notion write plan.

**DELIVERABLES:** Notion adapter (full contract); webhook inbound sync; idempotent verified outbound; conflict
detection; DLQ; Impact Report writer; end-to-end commit from an approved proposal.

**VULNERABILITY CHECK** *(sign-off: 16-security-privacy)* — **sprint focus: webhook signature & token scope**
- [x] Webhook authenticity/signature verified before processing (no spoofed-webhook mirroring).
- [x] Token least-privilege, in secret manager, never client-exposed.
- [x] Idempotency keys + external IDs prevent duplicate writes on retry.
- [x] Stale-proposal detection blocks commit on conflict; all write attempts audited.

**WORKFLOW CHECK** *(sign-off: 17-qa-workflow)* — golden section [6]; AT-01/06/08
- [x] AT-01: ops-lead marks Main Auditorium unavailable via Notion (08:00) → webhook → re-fetch → core loop runs to a Change Proposal.
- [x] [6] On approval the write plan applies exactly: 4 session venue-relation updates, 5 assignment edits, 17 task pages, stale comm/task flags, 1 Impact Report, 1 Change Proposal (≈32 calls, ~3 req/s); **nothing writes while branch-only**.
- [x] AT-08: reject → zero Notion writes. AT-06: a direct Notion session-venue edit → re-sync + conflict highlight.

**Exit gate:** **golden vertical slice complete** — AT-01, AT-06, AT-08 all green against the sandbox workspace.
*(TAD roadmap P4 exit; the mandatory demo path is now whole.)*

---

## Sprint 7 — Participant operations (notifications + attendance + PWA)
**Goal:** reach the participant — cohort-targeted grounded notifications with an approval gate and delivery status,
QR/NFC attendance with offline replay, and the participant PWA.
**Duration:** 3 days · **Requirement coverage:** FR-NOTIFY-001…005, COM-001…008, ATT-001…009, RULE-05/07,
NFR-A11Y-001, AT-05 (attendance part) · **Lead:** 09-notification-comms, 13-attendance, 15-participant-pwa ·
**Support:** 16-security-privacy, 06-ai-orchestration

| Task | Description | Agent | Depends |
|---|---|---|---|
| S7-T1 | Cohort derivation + grounded drafts | 09-notification-comms | S4-T2 |
| S7-T2 | Approval gate + channel adapters + status | 09-notification-comms | S7-T1 |
| S7-T3 | Stale-comm detector | 09-notification-comms | S2-T2 |
| S7-T4 | Attendance credentials + idempotent ingest | 13-attendance | S1-T1 |
| S7-T5 | Offline replay + reconciliation | 13-attendance | S7-T4 |
| S7-T6 | Participant PWA | 15-participant-pwa | S7-T2, S7-T4 |

- **S7-T1** Cohort derivation + drafts `[Agent: 09-notification-comms]`
  - [x] S7-T1.1 Cohorts by impacted session/venue/route/volunteer-role/organizer (COM-001).
  - [x] S7-T1.2 Drafts contain only approved facts: old state, new state, effective time, action required (COM-002/003); AI draft labeled until approved.
- **S7-T2** Approval gate + channels `[Agent: 09-notification-comms]`
  - [x] S7-T2.1 Mass dispatch blocked until approval unless pre-approved policy (COM-008, RULE-03).
  - [x] S7-T2.2 Channel adapters (email/SMS/push/WhatsApp) behind abstraction; delivery status (sent/delivered/failed/pending); dedup per change+cohort (COM-005/006); at-least-once + idempotency key.
- **S7-T3** Stale-comm detector `[Agent: 09-notification-comms]`
  - [x] S7-T3.1 Flag public comms that `mentions` a superseded venue/session (FR-NOTIFY-005, COM-007).
- **S7-T4** Attendance credentials + ingest `[Agent: 13-attendance]`
  - [x] S7-T4.1 Roster from approved registration (ATT-001); signed opaque QR/NFC token, short-lived, server-validated.
  - [x] S7-T4.2 Scan ingest API; idempotency key = credential+session+scan-window; reject expired/mismatched (ATT-002/003/004).
  - [x] S7-T4.3 Near-real-time session counts; occupancy signal exposed without identity (ATT-006/007).
- **S7-T5** Offline replay + reconciliation `[Agent: 13-attendance]`
  - [x] S7-T5.1 Reconcile registration vs scans; late correction requires authorized operator action + audit (ATT-005); never mutate registration state (RULE-07).
- **S7-T6** Participant PWA `[Agent: 15-participant-pwa]`
  - [x] S7-T6.1 Personal schedule, change notices (old/new/effective/action), navigation/pickup, check-in/out.
  - [x] S7-T6.2 Service worker + manifest + push; encrypted offline scan queue with idempotent replay; a11y (NFR-A11Y-001).

**DELIVERABLES:** cohort engine + grounded drafts + approval gate + channel adapters + delivery status +
stale-comm flagging; signed-token QR/NFC attendance + offline replay + reconciliation; participant PWA.

**VULNERABILITY CHECK** *(sign-off: 16-security-privacy)* — **sprint focus: mass-notify abuse & token forgery**
- [x] Mass-notify abuse prevented: approval gate + rate limits + audience preview + send window.
- [x] Credential tokens signed + short-lived; forged/expired scans rejected; duplicate attendance suppressed.
- [x] Offline queue encrypted in-browser; replay idempotent; only opaque scoped tokens stored client-side.
- [x] Participant PII minimized (channels + attendance); retention configurable (NFR-PRIV-001/002).

**WORKFLOW CHECK** *(sign-off: 17-qa-workflow)* — golden [1]/[4]; AT-05 (attendance)
- [x] Cohorts 380/230/180/390 derived; each gets a draft naming old→new venue + effective time (N11–N14).
- [x] Stale comms flagged: Instagram "Opening at Main Auditorium" + Gate 1/Gate 3 boards.
- [x] Mass dispatch blocked until approval; a QR scan creates exactly one record; offline scans replay with no duplicates; AT-05 occupancy feed produced.

**Exit gate:** participant notifications approval-gated end-to-end; attendance ingest + offline replay verified.
*(TAD roadmap P4/P6 participant slice.)* **— DEMO CUT LINE: everything above is mandatory.**

---

## Sprint 8 — Mobility & crowd control
**Goal:** add two KIIT-scale signals on the same loop — transport disruption → reallocation, and crowd pressure →
reroute — plus the campus map.
**Duration:** 3 days · **Requirement coverage:** TRN-001…008, CRD-001…007, AT-03, AT-04, AT-05 · **Lead:**
10-transport-mobility, 11-crowd-safety · **Support:** 14-frontend-command-center, 04-rules-optimization

| Task | Description | Agent | Depends |
|---|---|---|---|
| S8-T1 | Transport models + trip planner | 10-transport-mobility | S1-T1 |
| S8-T2 | Disruption → CP-SAT reallocation + notices | 10-transport-mobility | S8-T1, S3-T3 |
| S8-T3 | Crowd zones/gates/flows + thresholds | 11-crowd-safety | S1-T1 |
| S8-T4 | Crowd alerts + reroute proposals | 11-crowd-safety | S8-T3, S7-T4 |
| S8-T5 | MapLibre campus layer | 14-frontend-command-center | S8-T1, S8-T3 |

- **S8-T1** Transport models + planner `[Agent: 10-transport-mobility]`
  - [x] S8-T1.1 Vehicles/routes/trips/stops with capacity + operating windows (TRN-001); curated KIIT route/stop dataset; every trip has source/timestamp/capacity/route/status.
  - [x] S8-T1.2 Cohort→route/stop mapping (TRN-002); route engine ETAs (walking + shuttle).
- **S8-T2** Disruption → reallocation `[Agent: 10-transport-mobility]`
  - [x] S8-T2.1 Detect venue/schedule change altering travel demand (TRN-003); re-estimate capacity (TRN-004).
  - [x] S8-T2.2 Transport CP-SAT (via 04): hard (capacity/route windows/driver availability), objective (min empty seats/travel/trips); propose reallocation (TRN-005); driver/vehicle tasks (TRN-007); pickup-change notices (TRN-006).
- **S8-T3** Crowd zones/gates/flows `[Agent: 11-crowd-safety]`
  - [x] S8-T3.1 Zones (capacity/threshold/connected gates), gates (open window/max flow), flows (source/target/cohort/window); configurable thresholds (CRD-001/002).
  - [x] S8-T3.2 Anonymous people-count inputs (CRD-006); consume attendance occupancy without identity.
- **S8-T4** Crowd alerts + reroute `[Agent: 11-crowd-safety]`
  - [x] S8-T4.1 Alert when measured/estimated load crosses threshold (CRD-003); cross-event corridor conflict (CRD-005).
  - [x] S8-T4.2 Propose alternate gate/route/queue guidance via the proposal path; operator confirm before major intervention (CRD-004/007).
- **S8-T5** MapLibre campus layer `[Agent: 14-frontend-command-center]`
  - [x] S8-T5.1 Venues, shuttles, gates, crowd zones on MapLibre; source/timestamp on transport + crowd signals (TRN-008).

**DELIVERABLES:** transport service + disruption reallocation + notices; crowd service + thresholds + alerts +
reroute proposals; campus map layer.

**VULNERABILITY CHECK** *(sign-off: 16-security-privacy)* — **sprint focus: crowd data anonymity**
- [x] Crowd path uses anonymous counts only; no identity data (CRD-006, ATT-007).
- [x] Transport/crowd status source authenticity + freshness labeled (RULE-08).
- [x] Dispatch + advisory changes require authorized actor + audit; thresholds are config not code.

**WORKFLOW CHECK** *(sign-off: 17-qa-workflow)* — AT-03/04/05
- [x] AT-03: assigned shuttle unavailable → recalc capacity → propose alternate allocation → notify affected participants.
- [x] AT-04: gate/corridor load exceeds threshold → alert → show affected sessions/routes → propose reroute.
- [x] AT-05: attendance approaching venue capacity → occupancy update → crowd/ops advisory.

**Exit gate:** AT-03, AT-04, AT-05 pass; transport + crowd render on the map. *(TAD roadmap P5 exit.)*

---

## Sprint 9 — Weather resilience & institutional memory
**Goal:** the last two signals — weather-triggered rescheduling branches (chained onto the golden outage) — plus
RAG knowledge, the post-event report and reusable KnowledgeItems, and multi-event isolation.
**Duration:** 3 days · **Requirement coverage:** WX-001…009, FR-KB-001…003, BR-016, BR-018, RULE-10, AT-02, AT-10
· **Lead:** 12-weather-resilience, 07-rag-knowledge · **Support:** 05-simulation-proposal, 06-ai-orchestration

| Task | Description | Agent | Depends |
|---|---|---|---|
| S9-T1 | Weather adapters + normalization | 12-weather-resilience | S1-T1 |
| S9-T2 | Thresholds + re-eval → weather branch | 12-weather-resilience | S9-T1, S4-T1 |
| S9-T3 | RAG ingestion + retrieval (citations) | 07-rag-knowledge | S0-T2 |
| S9-T4 | Post-event report + KnowledgeItem | 07-rag-knowledge | S9-T3 |
| S9-T5 | Multi-event isolation hardening | 03-data-graph | S1-T2 |

- **S9-T1** Weather adapters `[Agent: 12-weather-resilience]`
  - [x] S9-T1.1 IMD Bhubaneswar + Open-Meteo adapters behind abstraction; monitoring profiles for outdoor sessions/venues (WX-001/002).
  - [x] S9-T1.2 Normalize signals with source, issue time, validity, confidence, affected zone (WX-003).
- **S9-T2** Thresholds + weather branch `[Agent: 12-weather-resilience]`
  - [x] S9-T2.1 Configurable thresholds (rain/lightning/wind/heat) (WX-004); re-evaluate affected outdoor sessions on material change (WX-005).
  - [x] S9-T2.2 Generate alternate-venue/postpone/split/cancel proposals as a simulation branch (WX-006); low confidence → escalate, not auto-reschedule; show uncertainty (WX-007).
  - [x] S9-T2.3 Targeted notifications on approval (WX-008); retain branch for compare (WX-009).
- **S9-T3** RAG ingestion + retrieval `[Agent: 07-rag-knowledge]`
  - [x] S9-T3.1 Ingest authorized docs (source/owner/timestamp/version); chunk + embed (pgvector); hybrid retrieval filtered by event/school/policy scope (TAD §13).
  - [x] S9-T3.2 Grounding returns evidence snippets/record IDs; not authoritative for live operational facts.
- **S9-T4** Post-event report + KnowledgeItem `[Agent: 07-rag-knowledge]`
  - [x] S9-T4.1 Post-event operational report (FR-KB-001); KnowledgeItem with evidence links (FR-KB-002, RULE-10); searchable by event/issue/venue/response (FR-KB-003).
- **S9-T5** Multi-event isolation `[Agent: 03-data-graph]`
  - [x] S9-T5.1 Verify + harden event-scoped isolation across all services (BR-018).

**DELIVERABLES:** weather adapters + thresholds + weather branch + notices; RAG retrieval with citations;
post-event report + KnowledgeItem; multi-event isolation checks.

**VULNERABILITY CHECK** *(sign-off: 16-security-privacy)* — **sprint focus: RAG tenant filtering**
- [x] Retrieval filtered by tenant/event/policy scope; no cross-event leakage.
- [x] Only authorized documents ingested; provenance recorded; generated narrative never shown as verified fact.
- [x] Weather source freshness + failover (IMD→Open-Meteo→operator) without presenting stale as current.

**WORKFLOW CHECK** *(sign-off: 17-qa-workflow)* — AT-02/10
- [x] AT-02: outdoor session gets lightning/thunderstorm risk → alternate indoor/re-timing proposals → cohort update → approval required; uncertainty shown.
- [x] **Chained demo:** after the outage moves 3 sessions to the outdoor Open Air Theatre, a thunderstorm over OAT triggers a second weather branch on top of the approved plan.
- [x] AT-10: on event close, produce attendance/report/lessons + a KnowledgeItem linked to evidence.

**Exit gate:** AT-02, AT-10 pass; weather branch chains onto the golden plan. *(TAD roadmap P5/P6 exit.)*


---

## Sprint 10 — Hardening, evaluation & demo
**Goal:** prove the KPIs, the resilience, the security and the AI quality; pass the TAD architecture checklist; and
rehearse the demo.
**Duration:** 2–3 days · **Requirement coverage:** all NFR-PERF/REL/OBS, NFR-AI, §5.1 KPIs, TAD §22/23/24.1,
Appendix A; final pass over AT-01…10 · **Lead:** 18-observability-sre, 16-security-privacy, 17-qa-workflow,
00-orchestrator

| Task | Description | Agent | Depends |
|---|---|---|---|
| S10-T1 | Performance benchmarks vs KPIs | 18-observability-sre | S9 |
| S10-T2 | Load + resilience drills | 18-observability-sre | S10-T1 |
| S10-T3 | AI evaluation suite | 18-observability-sre | S9 |
| S10-T4 | Full security review + scans | 16-security-privacy | S9 |
| S10-T5 | Full AT-01…10 regression | 17-qa-workflow | S9 |
| S10-T6 | Architecture checklist gate + demo + docs | 00-orchestrator | S10-T1…T5 |

- **S10-T1** Performance benchmarks `[Agent: 18-observability-sre]`
  - [x] S10-T1.1 Benchmark impact ≤5 s/5k edges, first plan ≤15 s, dashboard p95 <500 ms, sim branch <10 s, audience build <2 s/5k, realtime <2 s (TAD §23, §5.1); log gaps as ADRs.
- **S10-T2** Load + resilience `[Agent: 18-observability-sre]`
  - [x] S10-T2.1 Attendance load ≥50 scans/s; dashboard fan-out within target.
  - [x] S10-T2.2 Drills: Notion outage (queue + stale banner), LLM outage (deterministic + templated), Redis outage (DB-backed queue), solver timeout (best feasible + escalate), partial commit (block + reconcile).
- **S10-T3** AI evaluation suite `[Agent: 18-observability-sre]` (support 06, 07)
  - [x] S10-T3.1 TAD §24.1: replay golden outputs vs expected facts; selected venue/resource satisfies all hard constraints; unsupported-claim rate; correct tool selection/args; no mutation before approval; stale-data/freshness labeling.
- **S10-T4** Full security review `[Agent: 16-security-privacy]`
  - [x] S10-T4.1 Threat-model walkthrough (TAD §21); prompt-injection, token-compromise, mass-notify-abuse suites; dependency + container scan; secrets audit.
- **S10-T5** Full AT regression `[Agent: 17-qa-workflow]`
  - [x] S10-T5.1 AT-01…10 green; golden [1]–[7] regression stable in CI.
- **S10-T6** Checklist gate + demo + docs `[Agent: 00-orchestrator]`
  - [x] S10-T6.1 Sign TAD Appendix A architecture checklist (see Appendix below); confirm RTM 100%.
  - [x] S10-T6.2 Rehearse the demo script (golden outage → chained weather → transport/crowd/attendance); finalize `docs/`.

**DELIVERABLES:** KPI benchmark report; load + resilience-drill results; AI-eval report; security review report +
clean scans; AT-01…10 green; signed architecture checklist; demo script; docs.

**VULNERABILITY CHECK** *(sign-off: 16-security-privacy)* — **final full review**
- [x] All TAD §21 threat priorities have a control + a passing test.
- [x] Dependency + container scans clean; no secrets in source/logs/traces; observability endpoints access-controlled.
- [x] Every mutating endpoint/tool has an enforced RBAC rule; approval gate holds under adversarial tests.

**WORKFLOW CHECK** *(sign-off: 17-qa-workflow)* — **final end-to-end**
- [x] AT-01…10 all green; golden regression deterministic.
- [x] Core-loop invariants hold everywhere: no mutation before approval; 0 hard-constraint violations committed; 100% AI outputs trace-id-ed + labeled; stale sources marked.
- [x] Resilience drills recover without losing approved state and never double-apply an external write.

**Exit gate:** all AT-01…10 green; KPIs met or gaps ADR-logged; TAD architecture checklist signed; demo rehearsed.
*(TAD roadmap P7 exit.)*


---

## 6. Requirements Traceability Matrix (requirement → sprint/task → acceptance)
> Maintained by `00-orchestrator`. Every BRD/SRS id maps to at least one sprint task and an AT/test.

| Requirement group | IDs | Sprint(s) → task(s) | Acceptance / test |
|---|---|---|---|
| Business requirements | BR-001 | S1-T3, S4-T4 | AT-01/06 |
| | BR-002 | S2-T2 | AT-01/09 |
| | BR-003 | S4-T1 | AT-08 |
| | BR-004 | S3-T2 | AT-01/09 |
| | BR-005 | S3-T3 | AT-01 |
| | BR-006 | S3-T4 | AT-01 |
| | BR-007 | S7-T1 | AT-01/02/03 |
| | BR-008 | S8-T1/T2 | AT-03 |
| | BR-009 | S8-T3/T4 | AT-04/05 |
| | BR-010 | S9-T1/T2 | AT-02 |
| | BR-011 | S7-T4 | AT-05 |
| | BR-012 | S6-T3 | AT-01/06/08 |
| | BR-013 | S4-T3, S7-T2 | AT-08 |
| | BR-014 | S5-T4 | AT-07 |
| | BR-015 | S1-T4 | AT-06/07 |
| | BR-016 | S9-T4 | AT-10 |
| | BR-017 | S3-T1 (config) | AT-02/03 |
| | BR-018 | S1-T2, S9-T5 | Multi-event test |
| Event/schedule | FR-EVT-001…005 | S1-T1/T3 | AT-01 |
| Dependency engine | FR-GRAPH-001…005 | S2-T1/T2/T3 | AT-01/09 |
| Planning/optimization | FR-PLAN-001…005 | S3-T2/T5 | AT-01/09 |
| Simulation/approval | FR-SIM-001…006 | S4-T1/T2/T3 | AT-08 |
| Tasks/staffing | FR-TASK-001…006 | S3-T3/T4 | AT-01 |
| Notifications | FR-NOTIFY-001…005 | S7-T1/T2/T3 | AT-01/02/03 |
| Live dashboard | FR-LIVE-001…004 | S4-T4/T5 | AT-01 |
| Knowledge | FR-KB-001…003 | S9-T4 | AT-10 |
| AI | AI-001…010 | S5-T1…T6 | AT-07 |
| Notion | INT-NOT-001…009 | S6-T1…T6 | AT-01/06 |
| Transport | TRN-001…008 | S8-T1/T2 | AT-03 |
| Crowd | CRD-001…007 | S8-T3/T4 | AT-04/05 |
| Weather | WX-001…009 | S9-T1/T2 | AT-02 |
| Attendance | ATT-001…009 | S7-T4/T5 | AT-05 |
| Communication | COM-001…008 | S7-T1/T2/T3 | AT-01/02/03 |
| NFR — performance | NFR-PERF-001/002/003 | S2-T5, S10-T1 | KPI bench |
| NFR — reliability | NFR-REL-001/002/003 | S1-T3, S6-T3, S10-T2 | Drills |
| NFR — security | NFR-SEC-001/002/003 | S0-T4, S1-T5, S10-T4 | Sec suite |
| NFR — privacy | NFR-PRIV-001/002 | S7, S8, S9 | Sec suite |
| NFR — AI governance | NFR-AI-001/002/003 | S5-T4/T5, S10-T3 | AT-07 |
| NFR — usability | NFR-USE-001/002 | S4-T5 | UAT |
| NFR — maintainability | NFR-EXT-001, NFR-MNT-001 | S0, S3-T1 | Config test |
| NFR — observability | NFR-OBS-001 | S0-T5, S5-T6 | Trace check |
| NFR — accessibility | NFR-A11Y-001 | S7-T6 | a11y check |
| Business rules | RULE-01…10 | enforced across S3–S9; gated by 16/17 | AT-07/08/09/10 |
| Acceptance scenarios | AT-01…10 | S3/S4/S5/S6/S7/S8/S9; final S10-T5 | — |

---

## 7. Global vulnerability baseline (TAD §21 threat priorities × OWASP ASVS)
Enforced by `16-security-privacy`; every sprint VULNERABILITY CHECK draws from this.

| Threat priority (TAD §21) | Control | Owning agent(s) | Verified in |
|---|---|---|---|
| Unauthorized venue/session mutation | Server-side RBAC, default-deny, audit | 16, 02 | S1, S4 |
| Accidental mass notification | Approval gate + rate limit + audience preview | 16, 09, 05 | S4, S7 |
| Prompt injection → unsafe tool call | Tool allow-list, user-text isolation, no free-form mutation loop | 16, 06 | S5 |
| Stale Notion proposals | Refresh-before-commit, revision compare, conflict block | 08, 05 | S6 |
| Duplicate attendance writes | Idempotency key (credential+session+window) | 13 | S7 |
| Compromised integration tokens | Scoped least-privilege tokens in secret manager | 16, 01, 08 | S0, S6 |
| Participant/transport data exposure | Data minimization, opaque IDs, retention, tenant scoping | 16, 13, 10, 07 | S7, S8, S9 |
| Secrets in source/browser | Secret scanning in CI; nothing client-side | 01, 16 | S0 |
| External-write double-apply on retry | Idempotency + external ref + reconciliation | 18, 08, 05 | S6, S10 |

---

## 8. Global workflow matrix (acceptance scenarios AT-01…10)
Owned by `17-qa-workflow`; green by S10.

| AT | Scenario | Trigger | Expected outcome | Proven in |
|---|---|---|---|---|
| AT-01 | Venue outage | Main Auditorium unavailable | Blast radius, 4 sessions re-homed, tasks/volunteer changes, at-risk flag, Notion branch | S6 |
| AT-02 | Weather escalation | Outdoor session lightning risk | Alternate indoor/re-time proposals, cohort update, approval required | S9 |
| AT-03 | Transport disruption | Shuttle unavailable | Recalc capacity, alternate allocation, notify participants | S8 |
| AT-04 | Crowd pressure | Gate/corridor over threshold | Alert, affected sessions/routes, reroute proposal | S8 |
| AT-05 | Attendance surge | Venue near capacity | Occupancy update, crowd/ops advisory | S7/S8 |
| AT-06 | Notion edit | Operator edits venue in Notion | Webhook re-sync, conflict highlight | S6 |
| AT-07 | AI summary | System generates narrative | Labeled AI-generated, grounded in verified sections | S5 |
| AT-08 | Approval gate | Operator rejects proposal | No irreversible writes / mass notifications | S4/S6 |
| AT-09 | Infeasible plan | No venue meets capacity | Infeasible state + constraint reasons + manual actions | S3 |
| AT-10 | Post-event | Event closes | Attendance/report/lessons + reusable KnowledgeItem | S9 |

---

## 9. Risks & open issues (from TAD §32 / BRD §12)
| Topic | Assumption / risk | Resolution path | Owner |
|---|---|---|---|
| Notion schema | Real KIIT workspace schema may differ | Discovery workshop + versioned schema-map config | 08 |
| University SSO | Provider unconfirmed | OIDC abstraction; validate in pilot | 16, 01 |
| Transport telemetry | Live data may be unavailable | Curated route/trip dataset; adapter later | 10 |
| Weather API | Source/licensing/availability to verify | Provider adapter + freshness policy | 12 |
| Attendance policy | Credential policy not set | Agree QR/NFC flow before deployment | 13 |
| Participant messaging | Approved channels unknown | Channel abstraction + staged rollout | 09 |
| Campus map | Authoritative GIS unconfirmed | Curated map layer for prototype | 14, 10 |
| Scale | Real event volume unmeasured | Synthetic load test before pilot | 18 |
| AI model selection | Provider/cost not finalized | Model gateway/abstraction | 06 |
| Golden fixture | Simulation details are the contract | `tests/fixtures/golden_main_auditorium/` kept in sync with any sim change | 17 |

---

## 10. Appendix — TAD architecture checklist (final implementation gate, S10)
Signed by `00-orchestrator` with the owning agents:
- [x] Every operational mutation has an authenticated actor, revision and audit record. *(02, 03, 16)*
- [x] Every simulation run has a baseline revision and proposal diff. *(05)*
- [x] Every AI workflow is resumable and approval-gated before irreversible action. *(06)*
- [x] Hard constraints are checked independently of the LLM. *(04, 16)*
- [x] Notion writes are idempotent and verified after execution. *(08)*
- [x] Participant notifications are derived from impact cohorts and trace to the triggering change. *(09)*
- [x] Transport, weather, crowd and attendance are dependencies on the same event graph. *(03, 10, 11, 12, 13)*
- [x] Attendance events are idempotent and support offline replay. *(13)*
- [x] Forecasts and external signals carry source and freshness metadata. *(12, 10, 08)*
- [x] Performance, security and restore procedures are tested before pilot release. *(18, 16, 01)*

