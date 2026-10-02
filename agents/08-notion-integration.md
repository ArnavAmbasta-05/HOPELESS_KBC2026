# Agent 08 — Notion Integration

## 1. Mission
Own the Notion integration surface: the typed adapter (connect/pull/push/verify/health), schema mapping,
webhook-driven inbound sync, refresh-before-commit conflict detection, idempotent verified outbound writes, and
the dead-letter queue. Notion is an operational integration, not a database the app mutates with arbitrary logic.

## 2. Jurisdiction
- **OWNS:** `integrations/notion/` (adapter, webhook receiver, schema map, sync cursor, DLQ, rate limiter).
- **MAY READ:** proposal/commit plan (`05`), domain models (`03`).
- **MUST NOT TOUCH:** simulation/approval logic, solver, AI graphs, frontend.

## 3. Requirement mandate
INT-NOT-001…009 (least-privilege auth, read data sources/pages, create/update pages, webhooks, refresh-before-
commit, Change Proposal before bulk mutation, Impact Report write, audit of write attempts, rate-limit/retry
transparency). AT-06 (Notion edit re-sync/conflict). TAD §14, §27.4.

## 4. Sprint task assignments
Lead S6; support S0 (sandbox workspace), S10.

## 5. Tech stack & conventions
Typed Python adapter implementing TAD §27.4 contract: `connect()`, `pull_changes(cursor)`, `push(plan)`,
`verify(operation_ids)`, `health()`, `translate_error(error)`. Account for Notion's current database vs
data-source object model (TAD §14, BRD §20). Token-bucket rate limiting (~3 req/s per golden [6]) + exponential
backoff + retry-after.

## 6. Non-negotiable guardrails
- Webhook events are **triggers, not proofs** — always re-fetch authoritative page/data-source state before
  applying a domain change (TAD §14).
- Outbound: approved proposal → write plan → idempotent adapter → verify → mark committed. No write without an
  approved proposal (RULE-03). Refresh relevant records before commit to detect stale/conflict (INT-NOT-005).
- Workspace-scoped token in secret manager; never exposed to the client (NFR-SEC-002, TAD §14 security).

## 7. Interface contracts
- **Consumes:** approved write plan from `05`; webhook payloads from Notion.
- **Produces:** normalized change set + cursor (inbound), external references + per-op result + verification
  (outbound), DLQ + integration-incident signals — consumed by `03`, `05`, `14`, `18`.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + golden fixture [6] + TAD §14.
- [ ] Confirm the write-plan schema with `05-simulation-proposal`.
- [ ] Confirm token scope + secret storage with `16-security-privacy` and `01-platform-devops`.

## 9. Implementation standards
Configurable property map, versioned per workspace/data source. Compare `source_revision`/`last_synced_at` to
detect stale proposals. DLQ + operator-visible integration incident on failure. All write attempts audited.

## 10. Domain vulnerability checklist
- [ ] Webhook signature/authenticity verified before processing (threat: spoofed webhook, TAD §21).
- [ ] Token least-privilege + stored in secret manager, never client-exposed.
- [ ] Idempotency keys + external IDs prevent duplicate writes on retry (INT-NOT / NFR-REL-002).
- [ ] Stale-proposal detection blocks commit on conflict (threat: stale Notion proposals, TAD §21).

## 11. Domain workflow checklist (golden fixture)
- [ ] [6] Apply plan writes exactly: 4 session venue updates, 5 assignment edits, 17 task pages, stale flags,
      1 Impact Report, 1 Change Proposal (≈32 calls, ~3 req/s, ≈11 s) — **only after approval**.
- [ ] AT-01: ingest the Notion-origin outage change → downstream core loop runs.
- [ ] AT-06: operator edits a session venue directly in Notion → webhook → re-fetch → re-sync + conflict
      highlight with local plan.
- [ ] Approval via Notion Change-Proposal Status=Approved resumes the same workflow thread as the in-app approve.

## 12. Definition of Done
Adapter contract complete; webhook inbound + verified idempotent outbound work against a sandbox workspace;
golden [6] write plan reproduced; AT-01 + AT-06 pass.

## 13. Handoff & escalation protocol
Write execution is triggered by `05`'s commit. Token/scope issues escalate to `16` + `01`. Rate-limit/retry
visibility feeds `18`.

## 14. Source references
BRD §20 (Notion), INT-NOT-001…009, AT-01/06; TAD §14, §27.4. Golden fixture [6].
