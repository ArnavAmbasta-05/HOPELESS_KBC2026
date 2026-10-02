# Agent 09 — Notification & Communication

## 1. Mission
Own cohort-targeted participant and stakeholder communication: derive impacted cohorts, draft fact-grounded
messages, enforce approval before mass dispatch, dispatch through channel adapters with delivery status, and flag
stale public communications that reference superseded venues/schedules.

## 2. Jurisdiction
- **OWNS:** Notification Service (`services/workers/notifications/`), cohort/audience derivation, message
  templates, channel adapters (email/SMS/push/WhatsApp), delivery-status tracking, stale-comm detector.
- **MAY READ:** proposal/communication plan (`05`), graph cohorts (`03`), AI drafts (`06`).
- **MUST NOT TOUCH:** DB migrations, solver, Notion write adapter, approval logic internals.

## 3. Requirement mandate
FR-NOTIFY-001…005, COM-001…008 (cohorts, fact-grounded drafts w/ old/new/effective/action, approval before
dispatch, delivery status, stale-comm flagging, dedup, channel adapters, mass-notify approval gate). RULE-05.
TAD §19.

## 4. Sprint task assignments
Lead S7 (participant ops); support S6, S8 (transport notices).

## 5. Tech stack & conventions
Provider adapters behind a channel abstraction (NFR-EXT-001). Message lifecycle (TAD §19): audience derivation →
draft → grounding check → policy check → operator approval (if required) → dispatch → delivery status → audit →
retry/dead-letter. At-least-once with idempotency key.

## 6. Non-negotiable guardrails
- Drafts contain **only approved facts** (FR-NOTIFY-002); each message includes old state, new state, effective
  time, action required (COM-003). AI drafts are labeled until approved (RULE-02).
- Mass notification requires explicit approval unless a pre-approved policy exists (COM-008, RULE-03).
- Dedup prevents duplicate notifications per change+cohort (COM-005). Each message links back to the proposal +
  affected nodes that caused it (TAD §19).

## 7. Interface contracts
- **Consumes:** communication plan + cohorts from `05`/`03`, grounded drafts from `06`.
- **Produces:** approved dispatches + delivery status + stale-comm flags — consumed by `15` (participant), `14`,
  `18` (delivery metrics), audit.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + golden fixture [1] cohorts + [4] notify tasks.
- [ ] Confirm cohort derivation with `03` and the approval gate with `05`.
- [ ] Confirm channel-adapter secrets with `16` + `01`.

## 9. Implementation standards
Cohorts by impacted session/venue/route/volunteer role/organizer (COM-001). Channel adapters return delivery
status (sent/delivered/failed/pending) where provider permits. Stale-comm detector scans public messages that
`mentions` a changed venue/session (FR-NOTIFY-005, COM-007).

## 10. Domain vulnerability checklist
- [ ] Mass-notify abuse prevented: approval gate + rate limits + audience preview + send window (TAD §21).
- [ ] No participant PII beyond what the channel needs (NFR-PRIV-001); contact data minimized.
- [ ] Channel credentials in secret manager, never client-side.
- [ ] Dedup/idempotency prevents duplicate blasts on retry.

## 11. Domain workflow checklist (golden fixture)
- [ ] [1]/[4] Cohorts 380 (Opening), 230 (Keynote), 180 (Panel), 390 (Prize) are derived and each gets a draft
      naming old→new venue + effective time (N11–N14).
- [ ] [1] Stale comms flagged: Instagram post "Opening at Main Auditorium" + printed boards (Gate 1/Gate 3).
- [ ] Mass dispatch blocked until approval (AT-08 path); AT-02/03 notifications generated on approval.

## 12. Definition of Done
Cohort derivation + grounded drafts + approval gate + channel dispatch + delivery status + stale-comm flagging
work; golden cohorts/drafts reproduced; dedup verified.

## 13. Handoff & escalation protocol
Drafting node lives in `06`; dispatch tool is called only post-approval from `05`. Channel secrets via `01`/`16`.

## 14. Source references
BRD FR-NOTIFY, COM-001…008, RULE-05, NFR-PRIV-001; TAD §19. Golden fixture [1], [4].
