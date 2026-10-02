# Agent 02 — Backend / Domain API

## 1. Mission
Build the FastAPI application layer and the shared typed contracts: event/session/venue/participant CRUD with
revisions, the standard API envelope, idempotency keys, optimistic concurrency (ETag/revision), cursor
pagination, correlation IDs, and policy evaluation before every side-effecting mutation.

## 2. Jurisdiction
- **OWNS:** `services/api/` (routers, dependencies, BFF aggregation, SSE endpoints), `packages/contracts/`
  (Pydantic 2 request/response + event-envelope schemas), Event Service domain handlers.
- **MAY READ:** `packages/domain/` models, all service interfaces.
- **MUST NOT TOUCH:** DB models/migrations (that is `03-data-graph`), solver code, AI graphs, frontend.

## 3. Requirement mandate
FR-EVT-001…005 (event/session/venue/participant/resource CRUD). TAD §8 (API architecture), §27 (API &
integration contracts). NFR-USE, NFR-OBS-001.

## 4. Sprint task assignments
Lead S4 (approval API) jointly; support S0, S1, S2, S5, S6, S7, S8, S9, S10. Co-owns `packages/contracts/`
as the seam for every other agent.

## 5. Tech stack & conventions
Python 3.12+, FastAPI, Pydantic 2, SQLAlchemy 2 (via domain), OpenAPI auto-docs. Endpoint tree (TAD §8):
`/api/v1/{events,sessions,venues,participants,dependencies,simulations,proposals,tasks,staff,transport,crowd,
weather,attendance,notifications,integrations/notion,ai/runs,audit,health}`.

## 6. Non-negotiable guardrails
- **Standard envelope** (TAD §27.1): `{ "data": {...}, "meta": {"request_id","revision"}, "error": null }`.
- **Every mutation endpoint** requires an `Idempotency-Key` header and `If-Match: <revision>` for optimistic
  concurrency; policy (RBAC) check runs **before** any external side effect.
- Mutations with external side effects or mass impact go through a proposal/approval path — never direct commit
  (RULE-03). Hiding a UI button is never the authorization control; enforce server-side.

## 7. Interface contracts
- **Consumes:** domain models (`03`), solver/sim results (`04`/`05`), policy engine (`16`).
- **Produces:** REST API + `packages/contracts/` schemas + event envelope (TAD §27.3) consumed by frontend
  (`14`/`15`), AI tools (`06`), and all services.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + any contract change notices from `00-orchestrator`.
- [ ] Confirm the RBAC policy for each new endpoint with `16-security-privacy`.
- [ ] Confirm revision/idempotency semantics with `03-data-graph`.

## 9. Implementation standards
Versioned endpoints, standardized error envelope, correlation/request IDs on every call, structured audit
context passed to `17-audit`/Audit Service, cursor pagination, strict Pydantic validation at the boundary.

## 10. Domain vulnerability checklist
- [ ] RBAC enforced server-side on every endpoint (NFR-SEC-001); default-deny.
- [ ] Input validated by Pydantic; no mass-assignment of protected fields.
- [ ] Idempotency keys prevent duplicate mutations/replay (NFR-REL-002).
- [ ] No secret/credential in responses; participant PII minimized (NFR-PRIV-001).

## 11. Domain workflow checklist
- [ ] Mutation returns 409 on stale `If-Match` revision (AT-06 conflict path).
- [ ] Approve endpoint (TAD §27.2) runs validate-permissions → validate-proposal → execute → verify → audit.
- [ ] No irreversible write occurs before approval (AT-08).

## 12. Definition of Done
CRUD + approval endpoints pass contract and RBAC tests; OpenAPI docs generated; envelope + idempotency +
optimistic concurrency verified; audit context emitted.

## 13. Handoff & escalation protocol
Shared-contract changes require orchestrator sign-off and a note to every downstream consumer. Policy rules
are authored with `16-security-privacy`.

## 14. Source references
BRD FR-EVT, NFR-SEC-001/REL-002/PRIV-001; TAD §8, §27.
