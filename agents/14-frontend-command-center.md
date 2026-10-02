# Agent 14 — Frontend / Command Center

## 1. Mission
Build the desktop-first command center: role-specific dashboards, the live operations view (schedule/venue/task/
attendance/transport/crowd/weather with source + timestamp), the dependency-graph / timeline / risk-heatmap
visualizations, the campus map, and the Change-Proposal review + approval UI.

## 2. Jurisdiction
- **OWNS:** `apps/web/` command-center app (React + TS + Vite), dashboards, graph/timeline/map/heatmap
  components, proposal-review + approval UI, SSE client, role-aware route guards.
- **MAY READ:** API contracts (`packages/contracts/`).
- **MUST NOT TOUCH:** backend services, `apps/web/src/participant/` (that is `15`), AI graphs, DB.

## 3. Requirement mandate
FR-LIVE-001…004 (live status, timestamp+source, role-specific views, alert drill-down to object + dependency
chain). NFR-USE-001/002 (top risks in ≤2 views; every alert exposes affected object + next action).
NFR-A11Y-001 (shared with `15`). TAD §7.

## 4. Sprint task assignments
Lead S4 (Command Center v1) and S8 (maps); support S5, S6, S7, S9, S10.

## 5. Tech stack & conventions
React + TypeScript (strict) + Vite; React Router (role guards); TanStack Query (server state, invalidate on
event-stream changes); Zustand (local UI state); Recharts + SVG/Canvas (timeline, risk heatmap, dependency
graph); MapLibre GL JS (venues/shuttles/gates/zones); React Hook Form + Zod (validation mirroring API schemas);
SSE first for dashboard deltas + job progress (TAD §7).

## 6. Non-negotiable guardrails
- **Frontend security boundary (TAD §7):** never store Notion/provider credentials in the browser; receive only
  scoped, opaque identifiers. Hiding a button is **not** an authorization control — mass actions are
  approval-gated server-side.
- AI-generated content is visibly distinguished from verified facts in the UI (NFR-AI-001, BR-014).
- Stale external data is labeled stale, with last-updated time per live category (RULE-08, FR-LIVE-002,
  NFR-PERF-003).

## 7. Interface contracts
- **Consumes:** REST + SSE from `02`, proposal/diff from `05`, AI labels from `06`, signals from `08`/`10`/`11`/`12`/`13`.
- **Produces:** operator actions (approve/reject, trigger simulate) back through `02`'s API.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + `packages/contracts/` + NFR-USE/A11Y.
- [ ] Confirm the proposal-review data shape with `05` and the AI-label flag with `06`.
- [ ] Confirm role→view permissions with `16-security-privacy`.

## 9. Implementation standards
Functional components, strict TypeScript, role-aware guards, cache invalidation on SSE deltas. Every alert
drill-down reaches the affected object + its dependency chain (FR-LIVE-004). Commander sees status + top risks in
≤2 views (NFR-USE-001).

## 10. Domain vulnerability checklist
- [ ] No credentials/secrets in the browser or bundle; only opaque scoped IDs (TAD §7).
- [ ] Role guards are UX only; real authz is server-side (don't rely on hidden buttons).
- [ ] XSS-safe rendering of AI/user text; AI narrative clearly labeled.

## 11. Domain workflow checklist
- [ ] AT-07: AI narrative is rendered with a visible AI-generated label, separate from verified sections.
- [ ] AT-08: operator can reject a proposal; UI confirms no irreversible writes occurred.
- [ ] Live view shows last-updated + source per category (FR-LIVE-002); stale sources marked.

## 12. Definition of Done
Command Center v1 (dashboard + impact graph + proposal review + approval) works against the API; role guards +
AI labeling + stale markers in place; maps render in S8.

## 13. Handoff & escalation protocol
Contract changes requested via `00` to `02`. Shares the a11y/PWA base with `15`. Role matrix with `16`.

## 14. Source references
BRD FR-LIVE, NFR-USE, NFR-AI-001, BR-014, RULE-08; TAD §7. AT-07/08.
