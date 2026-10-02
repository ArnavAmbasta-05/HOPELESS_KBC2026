# Agent 11 — Crowd & Safety

## 1. Mission
Provide capacity-aware crowd intelligence (not surveillance): zones, gates, flows, occupancy estimates and
configurable thresholds; raise crowd alerts when load crosses a threshold; and propose gate/route/queue guidance
for operator approval.

## 2. Jurisdiction
- **OWNS:** Crowd Service (`services/workers/crowd/`), zone/gate/flow models, threshold config, occupancy
  estimation, crowd-incident + advisory logic, crowd routing (via dependency engine).
- **MAY READ:** attendance occupancy (`13`), graph (`03`), map (`14`), transport (`10`).
- **MUST NOT TOUCH:** DB migrations, AI graphs, Notion adapter, identity/attendance write path.

## 3. Requirement mandate
CRD-001…007 (estimate load by venue/slot, configurable thresholds, crowd alert on threshold, alternate
gate/route/queue proposal, cross-event conflict, anonymous people-count inputs, operator confirm before major
intervention). AT-04 (crowd pressure), AT-05 (attendance surge). TAD §16.

## 4. Sprint task assignments
Lead S8 (with transport); post-demo-cut-line extension.

## 5. Tech stack & conventions
Zones (`zone_id, capacity, threshold, connected_gates`), gates (`gate_id, open_window, max_flow_rate`), flows
(`source_zone, target_zone, cohort, time_window`), incidents, advisories (TAD §16). Crowd routing reuses the
dependency engine: venue change → cohort → gate/route update → transport adjustment → notification.

## 6. Non-negotiable guardrails
- **Capacity-aware, not surveillance** (TAD §16): baseline uses zones/gates/occupancy estimates + anonymous
  counts; no identity-based crowd tracking. Camera analytics is a future, approval-gated adapter.
- Attendance (identity) and crowd (anonymous counts) are distinct (BRD §21.2 design choice); crowd logic
  consumes occupancy without exposing participant identity (ATT-007).
- Operator confirmation required before major crowd interventions unless a pre-approved rule exists (CRD-007).

## 7. Interface contracts
- **Consumes:** occupancy signal from `13`, cohort/venue impact from `03`, transport from `10`.
- **Produces:** crowd alerts, advisories, reroute/gate proposals — consumed by `09`, `14`, `05` (as proposals),
  `18` (alert metrics).

## 8. Pre-task checklist
- [ ] Read this file + sprint section + TAD §16 + BRD §21.2.
- [ ] Confirm anonymous-occupancy contract with `13-attendance`.
- [ ] Confirm reroute-proposal format with `05` and `09`.

## 9. Implementation standards
Configurable thresholds per zone/gate (NFR-MNT-001). Alerts rate-limited (TAD §6). Advisories carry message,
audience, expiry; mass advisory needs approval unless pre-authorized (CRD-007, RULE-03).

## 10. Domain vulnerability checklist
- [ ] Crowd inputs are anonymous counts only; no identity data in crowd path (CRD-006, ATT-007, NFR-PRIV-001).
- [ ] Alert thresholds are config, not hard-coded; false-alarm mitigation (R-05) via config + human confirm.
- [ ] Advisory dispatch requires authorized actor + audit.

## 11. Domain workflow checklist
- [ ] AT-04: gate/corridor load exceeds threshold → raise alert → show affected sessions/routes → propose reroute.
- [ ] AT-05: attendance at a venue approaches capacity → update occupancy signal → trigger crowd/ops advisory.
- [ ] Cross-event corridor conflict detected when multiple sessions share movement paths (CRD-005).

## 12. Definition of Done
Zone/gate/flow models + thresholds + alerts + reroute proposals work; AT-04 + AT-05 pass; anonymity preserved.

## 13. Handoff & escalation protocol
Reroute proposals go through `05`'s proposal/approval path; advisories dispatched via `09`; map via `14`.

## 14. Source references
BRD CRD-001…007, §21.2, ATT-007, AT-04/05, R-05; TAD §16. 
