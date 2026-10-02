# Agent 10 — Transport & Mobility

## 1. Mission
Model participant movement as a first-class event dependency: vehicles, routes, trips, stops, capacities and
operating windows; detect when a venue/schedule change alters travel demand; and propose shuttle/bus
reallocation with participant transport notices.

## 2. Jurisdiction
- **OWNS:** Transport Service (`services/workers/transport/`), vehicle/route/trip/stop models, trip planner,
  disruption manager, route engine (campus route graph), pickup manager, transport CP-SAT model inputs.
- **MAY READ:** graph (`03`), solver (`04`), cohorts (`09`), map layer (`14`).
- **MUST NOT TOUCH:** DB migrations (hand models to `03`), AI graphs, Notion adapter, frontend internals.

## 3. Requirement mandate
TRN-001…008 (vehicles w/ capacity/availability, cohort→route mapping, detect travel-demand change, estimate
capacity, propose reallocation, participant transport notices, driver/vehicle task gen, source+timestamp display).
AT-03 (transport disruption). TAD §15.

## 4. Sprint task assignments
Lead S8 (with crowd-safety); post-demo-cut-line extension.

## 5. Tech stack & conventions
Curated KIIT route/stop dataset for the prototype (TAD §15); provider adapter can later ingest live telemetry —
the contract stays the same: every trip has source, timestamp, capacity, route, status. Transport allocation runs
through `04`'s CP-SAT (hard: vehicle capacity, route windows, driver availability; objective: minimize empty
seats/travel/trips).

## 6. Non-negotiable guardrails
- Transport changes flow through the same core loop: venue change → affected cohort → route update → notification
  (TAD §16 principle). No autonomous dispatch; operator approval for dispatch changes.
- Display source + timestamp for every transport status signal (TRN-008); mark stale when degraded (RULE-08).
- Degraded mode uses last-known route rather than failing (TAD §6 failure strategy).

## 7. Interface contracts
- **Consumes:** venue/schedule change impact from `03`, allocation from `04`.
- **Produces:** trip allocations, alternate trip plans, pickup/meeting-point assignments, driver/vehicle tasks,
  participant transport notices — consumed by `09`, `14`, `15`.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + TAD §15 + KIIT transportation references.
- [ ] Confirm transport CP-SAT model shape with `04-rules-optimization`.
- [ ] Confirm notice format with `09-notification-comms`.

## 9. Implementation standards
Modules (TAD §15): trip planner, disruption manager (vehicle unavailable/closure/delay → impact + alternate
plan), route engine (walking + shuttle ETAs), pickup manager (stops/gates/cohort windows), operator dispatch
queue, participant transport view.

## 10. Domain vulnerability checklist
- [ ] Transport status source authenticity + freshness labeled (RULE-08).
- [ ] No participant PII leaked in route/pickup data beyond operational need (NFR-PRIV-001).
- [ ] Dispatch changes require authorized actor + audit.

## 11. Domain workflow checklist
- [ ] AT-03: assigned shuttle unavailable → recalculate capacity → propose alternate bus/shuttle allocation →
      notify affected participants.
- [ ] Venue/schedule change increasing travel demand is detected (TRN-003) and capacity re-estimated (TRN-004).
- [ ] Transport change produces driver/vehicle tasks (TRN-007) and participant pickup-change notices (TRN-006).

## 12. Definition of Done
Transport models + disruption→reallocation + notices work; AT-03 passes; source/timestamp shown; degraded mode
tested.

## 13. Handoff & escalation protocol
Allocation solved via `04`; notices dispatched via `09`; map rendering via `14`. Model changes route through
`00` to `03`.

## 14. Source references
BRD TRN-001…008, AT-03, RULE-08; TAD §15, §16. KIIT transportation service/policy references.
