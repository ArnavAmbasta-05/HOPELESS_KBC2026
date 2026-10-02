# Agent 12 — Weather Resilience

## 1. Mission
Treat weather as external, time-varying evidence. Associate outdoor sessions with monitoring profiles, ingest
forecasts/nowcasts/warnings with source/validity/confidence, apply configurable hazard thresholds, and generate
weather-triggered rescheduling/relocation branches — always with uncertainty shown, never silent certainty.

## 2. Jurisdiction
- **OWNS:** Weather Service (`services/workers/weather/`), IMD Met Centre Bhubaneswar + Open-Meteo adapters,
  weather-signal normalization, threshold rule config, exposure evaluation, weather-branch trigger.
- **MAY READ:** sessions/venues (`03`), simulation (`05`), solver (`04`).
- **MUST NOT TOUCH:** DB migrations, AI graphs, Notion adapter, frontend internals.

## 3. Requirement mandate
WX-001…009 (monitoring profile, retrieve by location/time, store source/issue-time/validity, configurable
thresholds, re-evaluate on material change, alternate/postpone/split/cancel proposals, show uncertainty, targeted
notifications, retain branch). AT-02 (weather escalation). TAD §17.

## 4. Sprint task assignments
Lead S9 (with rag-knowledge); post-demo-cut-line extension.

## 5. Tech stack & conventions
Adapters behind a provider abstraction (NFR-EXT-001). Normalize to a common signal: source, validity, confidence,
affected geographic zone (TAD §17). Preferred local warning context = IMD Bhubaneswar where authorized;
Open-Meteo as a structured secondary.

## 6. Non-negotiable guardrails
- Forecasts are evidence, not deterministic truth — show source + age + the rule that triggered a branch; never
  silently claim certainty (WX-007, RULE-08, R-03).
- Low-confidence/conflicting sources → escalate to operator instead of auto-rescheduling (TAD §17).
- No autonomous cancellation; every weather action becomes a simulation branch awaiting approval (RULE-03).

## 7. Interface contracts
- **Consumes:** outdoor session/venue exposure from `03`, weather feeds from adapters.
- **Produces:** normalized weather signals, weather branch (alternate venue/postpone/split), uncertainty
  metadata, targeted notifications — consumed by `05`, `04`, `09`, `14`.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + TAD §17 + golden fixture (Open Air Theatre is outdoor → weather-exposed).
- [ ] Confirm branch contract with `05-simulation-proposal`.
- [ ] Confirm threshold config + notice format with `04` and `09`.

## 9. Implementation standards
Triggers + action branches (TAD §17): heavy rain → covered venue candidates; lightning → suspend outdoor +
shelter flow; extreme heat → shift timing + hydration/cool zones; wind → invalidate stage/tent + re-resolve
venue/equipment; forecast uncertainty → escalate. Thresholds in versioned config.

## 10. Domain vulnerability checklist
- [ ] Weather source freshness enforced; stale forecast marked (RULE-08, TAD §22 freshness SLA).
- [ ] Source failover (IMD → Open-Meteo → operator confirm) without presenting stale as current.
- [ ] Threshold config, not hard-coded (NFR-MNT-001).

## 11. Domain workflow checklist (golden chaining)
- [ ] AT-02: an outdoor session receives lightning/thunderstorm risk → generate alternate indoor/re-timing
      proposals → update participant cohort → require approval.
- [ ] **Chained demo:** after the Main-Auditorium outage moves 3 sessions to the outdoor Open Air Theatre, a
      thunderstorm over OAT triggers a *second* weather branch on top of the approved outage plan.
- [ ] Branch retained so organizers compare original vs weather-adapted plan (WX-009).

## 12. Definition of Done
Weather adapters + thresholds + re-evaluation + weather branch + notifications work; AT-02 passes; uncertainty
shown; chained OAT scenario demonstrated.

## 13. Handoff & escalation protocol
Branch created via `05`; re-resolution via `04`; notices via `09`. Adapter secrets via `01`/`16`.

## 14. Source references
BRD §22 (weather), WX-001…009, AT-02, R-03, RULE-08; TAD §17. IMD Bhubaneswar / Open-Meteo references.
