# Agent 13 — Attendance

## 1. Mission
Turn participant presence into a live operational signal using privacy-conscious event credentials (signed QR /
NFC). Provide idempotent scan ingest, offline queue + replay, reconciliation and near-real-time counts — feeding
occupancy to crowd logic without exposing unnecessary identity. Facial recognition is excluded from the baseline.

## 2. Jurisdiction
- **OWNS:** Attendance Service (`services/workers/attendance/`), credential issuance (signed opaque tokens),
  scan ingest API, idempotency rule, offline replay, reconciliation, attendance metrics/export.
- **MAY READ:** rosters/registration (`03`), crowd service (`11`).
- **MUST NOT TOUCH:** registration state writes (RULE-07), DB migrations, AI graphs, Notion adapter.

## 3. Requirement mandate
ATT-001…009 (roster from registration, record via QR/NFC, dedup/idempotency, timestamp+source attribution, late
arrival/correction w/ audit, near-real-time counts, expose to crowd without identity, export, optional future
proximity). RULE-07 (attendance ≠ registration). AT-05 (surge). TAD §18.

## 4. Sprint task assignments
Lead S7 (with notification-comms + participant-pwa); support S8 (occupancy to crowd).

## 5. Tech stack & conventions
Signed opaque participant/session token, short-lived, server-validated. Idempotency key = credential + session +
scan window (TAD §18). Offline encrypted queue in the PWA, replay with duplicate suppression.

## 6. Non-negotiable guardrails
- Baseline = QR/NFC; **no facial recognition** (ADR-007, BRD §23/§26). Minimize participant data; opaque IDs
  where possible; configurable retention (NFR-PRIV-001/002).
- Attendance records are idempotent per participant/session/time-window (§18.2); attendance never silently
  changes registration state (RULE-07). Late corrections require authorized operator action + audit (ATT-005).
- Expose occupancy to crowd logic without unnecessary identity data (ATT-007).

## 7. Interface contracts
- **Consumes:** roster from `03`, scans from participant PWA (`15`) / scanner.
- **Produces:** timestamped attendance records, near-real-time counts, occupancy signal, reconciliation report —
  consumed by `11` (occupancy), `14`, `09`, `18`.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + TAD §18 + BRD §23.
- [ ] Confirm token signing/secret with `16` + `01`.
- [ ] Confirm offline-queue contract with `15-participant-pwa`.

## 9. Implementation standards
Stages (TAD §18): credential (signed token) → scan (idempotency key) → offline mode (local encrypted queue +
replay) → validation (event/session/time/credential state; reject expired/mismatched) → reconciliation
(registration vs scans) → metrics (attendance/no-show/entry-exit/occupancy, aggregated where identity not needed).

## 10. Domain vulnerability checklist
- [ ] Credential tokens signed + short-lived; forged/expired scans rejected (threat: token forgery, TAD §21).
- [ ] Duplicate attendance writes suppressed via idempotency key (threat: duplicate attendance, TAD §21).
- [ ] Offline queue encrypted; replay cannot create duplicates.
- [ ] Attendance path exposes no PII to crowd logic beyond counts (ATT-007); retention configurable.

## 11. Domain workflow checklist
- [ ] Attendance roster built from approved registration data (ATT-001); a scan creates exactly one record.
- [ ] AT-05: attendance approaching venue capacity updates the occupancy signal consumed by crowd logic.
- [ ] Offline scans replay on reconnect without duplicates; late correction is audited (ATT-005).

## 12. Definition of Done
Signed-token QR/NFC ingest + idempotency + offline replay + reconciliation + counts work; AT-05 occupancy feed
verified; no registration-state mutation.

## 13. Handoff & escalation protocol
Scan UI + offline queue live in `15`; occupancy consumed by `11`. Token secrets via `01`/`16`.

## 14. Source references
BRD §23 (attendance), ATT-001…009, RULE-07, NFR-PRIV-001/002, AT-05; TAD §18, ADR-007.
