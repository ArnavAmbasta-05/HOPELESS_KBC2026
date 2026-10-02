# Agent 05 — Simulation & Change Proposal

## 1. Mission
Own the product differentiator: what-if simulation. Create branches against a baseline revision, compute the
baseline/proposed diff and risk, assemble the Change Proposal, and run the approve/commit path that only applies
writes after explicit human approval.

## 2. Jurisdiction
- **OWNS:** Simulation Service (`services/workers/simulation/`), branch + diff logic, risk calculation,
  ChangeProposal assembly, approve/reject/commit orchestration (the deterministic commit action).
- **MAY READ:** graph (`03`), solver results (`04`), Notion write plan (`08`), AI state (`06`).
- **MUST NOT TOUCH:** DB migrations, solver internals, Notion adapter internals, AI prompt graphs.

## 3. Requirement mandate
FR-SIM-001…006 (branch, no commit of operational state, baseline/proposed diff, risk + unresolved deps,
Change Proposal with records/tasks/notifications/Notion ops, approval before irreversible writes). RULE-03
(branch before bulk change), RULE-05 (participant impact before commit). ADR-006. TAD §10.

## 4. Sprint task assignments
Lead S4; support S3, S6 (commit to Notion), S9 (weather branch).

## 5. Tech stack & conventions
PostgreSQL simulation tables; branch has a unique id, deterministic input snapshot, impact set, candidate plans,
selected plan, validation results, proposal diff (TAD §10). Baseline is **never** overwritten by a simulation.

## 6. Non-negotiable guardrails
- Simulation changes never modify committed operational state (FR-SIM-002).
- A branch must exist before any bulk external change (RULE-03).
- Participant impact is evaluated before commit (RULE-05).
- Commit is gated by the LangGraph human-approval interrupt (via `06`); approval may arrive from the in-app
  approve endpoint **or** the Notion Change-Proposal Status=Approved — both resume the same workflow thread.

## 7. Interface contracts
- **Consumes:** candidates/tasks (`04`), cohorts (`09`), Notion write plan (`08`), approval signal (`06`/`08`).
- **Produces:** Change Proposal (TAD §10 artifact table), diff, commit result (external IDs, verification) —
  consumed by `14` (review UI), `02` (approve endpoint), `08` (commit).

## 8. Pre-task checklist
- [ ] Read this file + sprint section + golden fixture [6] (Notion write plan) + [7] (AI summary labeling).
- [ ] Confirm proposal/diff schema with `02` and `14`.
- [ ] Confirm approval-interrupt contract with `06-ai-orchestration`.

## 9. Implementation standards
Change Proposal must contain every §10 artifact: baseline snapshot, trigger, blast radius, candidates
(accepted+rejected w/ reasons), optimization result, operational plan, communication plan, risk plan,
proposal diff, approval state, commit result. Versioned branches reference a baseline revision (TAD §20.2).

## 10. Domain vulnerability checklist
- [ ] No commit path bypasses the approval gate (threat: accidental mass mutation, TAD §21).
- [ ] Approval requires an authorized actor (RBAC via `16`); approval action is audited.
- [ ] Commit is idempotent and refuses to re-run a prior external mutation blindly (TAD §22 recovery principle).

## 11. Domain workflow checklist (golden fixture)
- [ ] [6] Write plan assembled branch-only: 4 session venue-relation updates, 5 assignment edits, 17 task pages,
      stale comm/task flags, 1 Impact Report, 1 Change Proposal (≈32 calls).
- [ ] State is **BRANCH ONLY** until Change Proposal Status=Approved; rejecting produces zero writes (AT-08).
- [ ] Diff shows added/removed/changed objects (FR-SIM-003); risk plan flags N08 at-risk + unresolved deps.

## 12. Definition of Done
What-if branch → diff → Change Proposal → approve → commit works end-to-end; reject produces no writes (AT-08);
golden write plan reproduced.

## 13. Handoff & escalation protocol
Commit-to-Notion is executed through `08`'s adapter. Approval-interrupt wiring is co-owned with `06`.

## 14. Source references
BRD FR-SIM, RULE-03/05, AT-08; TAD §10, §20.2, §22, ADR-006. Golden fixture [6], [7].
