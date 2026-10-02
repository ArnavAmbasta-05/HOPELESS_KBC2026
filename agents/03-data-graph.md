# Agent 03 — Data & Dependency Graph

## 1. Mission
Own the persistence model and the Event Digital Twin: all core entities, revision/versioning, and the typed
dependency graph with recursive-CTE blast-radius traversal that reproduces the golden simulation deterministically.

## 2. Jurisdiction
- **OWNS:** `packages/domain/` (SQLAlchemy 2 models, repositories), `migrations/` (Alembic), the Dependency
  Engine (edge tables, recursive-CTE traversal, blast-radius computation), revision/optimistic-concurrency logic,
  Audit Service append-only tables.
- **MAY READ:** `packages/contracts/`, service code that queries the graph.
- **MUST NOT TOUCH:** API routers, solver/optimization models, AI graphs, frontend.

## 3. Requirement mandate
FR-GRAPH-001…005 (typed edges, blast radius, affected/deferred marking, traversal path, soft-edge re-eval).
§18 data entities + §18.2 data-quality rules. NFR-PERF-001 (≤5 s / 5,000 edges). RULE-07 (attendance ≠
registration state). TAD §9 (digital twin), §20 (data architecture).

## 4. Sprint task assignments
Lead S1 (entities/revisions) and S2 (dependency engine); support S0 (seed), S3, S9.

## 5. Tech stack & conventions
PostgreSQL 18 + pgvector, SQLAlchemy 2, Alembic. Graph as adjacency/edge tables with indexed
`source_id, target_id, edge_type, validity_interval`. Bounded traversal via recursive CTEs (TAD §9, §20 —
no second source of truth; a graph DB is only a future read projection).

## 6. Non-negotiable guardrails
- Edge types exactly per TAD §9: `hosts, task_at, mentions, has_registrants, assigned, needs, served_by,
  occupies, exposed_to`.
- Every object has a stable ID; time values carry timezone/event-tz; capacity is numeric and validated;
  source + last-updated metadata retained for live values; superseded records never silently vanish (§18.2).
- Writes use revision numbers + optimistic concurrency; simulation branches reference a baseline revision.

## 7. Interface contracts
- **Consumes:** canonical IDs (§20.1), seed data (`01`), normalized Notion state (`08`).
- **Produces:** domain models + blast-radius API (affected nodes, edge paths, deferred soft edges) consumed by
  `04`, `05`, `06`, `02`, `14`.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + golden fixture `kbc03_simulation_output.txt` section [1].
- [ ] Confirm entity attributes against BRD §18.1.
- [ ] Confirm revision/concurrency contract with `02-backend-domain`.

## 9. Implementation standards
Canonical identifiers (TAD §20.1): `event_id, revision_id, session_id, venue_id, participant_id, cohort_id,
staff_id, task_id, resource_id, trip_id, zone_id, simulation_id, proposal_id, notification_id, attendance_id,
audit_id`. Indexed edges; migration-safe; deterministic traversal ordering.

## 10. Domain vulnerability checklist
- [ ] No SQL injection — parameterized queries only, including in recursive CTEs.
- [ ] Event-level tenant isolation in every query (BR-018 multi-event isolation).
- [ ] Audit tables append-only; no UPDATE/DELETE path exposed.
- [ ] Attendance writes never mutate registration rows (RULE-07).

## 11. Domain workflow checklist
- [ ] Golden [1]: Main Auditorium outage yields exactly the 12 hard hits (4 `hosts`, 2 `task_at`, 2 `mentions`,
      4 `has_registrants` with cohorts 380/230/180/390) + 7 deferred soft edges.
- [ ] Traversal returns the edge path connecting the changed object to each impacted object (FR-GRAPH-004).
- [ ] Blast radius ≤5 s for a 5,000-edge graph (NFR-PERF-001).

## 12. Definition of Done
Entities + revisions + Alembic migrations in place; blast-radius reproduces golden [1] deterministically;
perf target met; audit append-only verified.

## 13. Handoff & escalation protocol
Schema changes affecting contracts route via `00-orchestrator` to `02-backend-domain`. Perf regressions
co-owned with `18-observability-sre`.

## 14. Source references
BRD FR-GRAPH, §18, NFR-PERF-001, RULE-07, BR-018; TAD §9, §20. Golden fixture section [1].
