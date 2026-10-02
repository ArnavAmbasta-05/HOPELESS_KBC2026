# Agent 15 — Participant PWA

## 1. Mission
Build the participant mobile-web/PWA experience: personal schedule, change notifications, navigation/pickup
points, and credential scanning with an offline attendance queue — accessible and privacy-conscious.

## 2. Jurisdiction
- **OWNS:** `apps/web/src/participant/`, service worker, Web App Manifest, push subscription, offline scan queue
  (encrypted), participant-facing views (schedule, notices, route/pickup, check-in/out).
- **MAY READ:** API contracts (`packages/contracts/`), shared UI base from `14`.
- **MUST NOT TOUCH:** command-center app internals, backend services, DB, AI graphs.

## 3. Requirement mandate
NFR-A11Y-001 (accessible text, keyboard support, semantic labels). Participant UX for ATT-002/004 (scan), COM-003
(old/new/effective/action messages), FR-LIVE (personal view). TAD §7 (PWA), §18 (offline attendance).

## 4. Sprint task assignments
Lead S7 (participant ops); support S8, S10.

## 5. Tech stack & conventions
React + TS + Vite PWA; Service Worker + Web App Manifest; push provider for alerts; local encrypted queue for
offline scans with replay + duplicate suppression (TAD §7, §18).

## 6. Non-negotiable guardrails
- **Participant pages receive only scoped, opaque event/credential identifiers** — never Notion/provider
  credentials (TAD §7 frontend boundary).
- Offline scan queue is encrypted; replay uses the attendance idempotency key so it cannot create duplicates
  (TAD §18, `13`).
- Participant-facing screens meet accessibility (NFR-A11Y-001). Change messages show old/new/effective/action
  (COM-003).

## 7. Interface contracts
- **Consumes:** personal schedule + notices from `02`/`09`, credential tokens from `13`, pickup info from `10`.
- **Produces:** scan events (online + queued) to `13`'s ingest API.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + TAD §7/§18 + `13-attendance` offline-queue contract.
- [ ] Confirm the opaque-token model with `13` and `16`.
- [ ] Confirm message format with `09`.

## 9. Implementation standards
Service worker caches shell + personal data for offline; background sync replays the scan queue on reconnect.
Semantic HTML, ARIA labels, keyboard navigation, sufficient contrast.

## 10. Domain vulnerability checklist
- [ ] No credentials/PII beyond the scoped opaque token stored client-side (TAD §7, NFR-PRIV-001).
- [ ] Offline queue encrypted at rest in the browser; cleared per retention policy.
- [ ] Scan replay idempotent (no duplicate attendance on reconnect).

## 11. Domain workflow checklist
- [ ] Participant receives a venue-change notice (old→new→effective→action) for their session (COM-003).
- [ ] Credential scan records attendance online; offline scans queue and replay without duplicates.
- [ ] a11y check passes (keyboard + screen-reader labels) (NFR-A11Y-001).

## 12. Definition of Done
PWA with schedule + notices + scan + offline queue + a11y works; replay idempotent; only opaque tokens stored.

## 13. Handoff & escalation protocol
Shares UI base + a11y conventions with `14`. Scan contract owned by `13`. Token/secret questions to `16`.

## 14. Source references
BRD NFR-A11Y-001, ATT-002/004, COM-003, NFR-PRIV-001; TAD §7, §18.
