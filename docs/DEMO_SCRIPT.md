# KoreX — KIIT EventOps AI Command Center
## Master Live Demonstration & Evaluation Script

**Product Name:** KoreX  
**Institution:** Kalinga Institute of Industrial Technology (KIIT)  
**Target Event Scenario:** KBC 2026 / KIIT Mega Fest (Multi-track 5,000+ attendee event)  
**Compliance Baseline:** BRD/SRS v1.0, TAD v1.0, Acceptance Scenarios AT-01…AT-10  

---

### Act 1: Digital Twin & Command Center Overview
1. **Operator Login & RBAC Verification**:
   - Access the KoreX Command Center (`http://localhost:5173`).
   - Authenticate via Dev / University OIDC provider (`ops_lead`, `event_commander`, `volunteer`).
   - View the live 2.5D Campus Digital Twin featuring all 16 domain entities (Venues, Sessions, Resources, Shuttles, Gates).
2. **Authoritative State Synchronization**:
   - Verify zero-latency sync with Notion operational databases.
   - Real-time Prometheus metrics & OpenTelemetry traces active at `/metrics`.

---

### Act 2: Main Auditorium Power Grid Disruption (AT-01)
1. **Disruption Trigger**:
   - 14:00 hrs: Substation failure triggers total blackout at **Campus 6 Main Auditorium** (`ven_main_aud`).
   - Disruption injected via Notion webhook or Command Center API.
2. **Instant Blast Radius Computation**:
   - Graph engine traverses 5,000+ dependency edges in **< 15ms** (Threshold: $\le 5$s).
   - Identifies 4 disrupted multi-speaker sessions (Opening Ceremony, Keynote AI in FinTech, Hackathon Briefing, Panel: NextGen Cloud).
   - Identifies 12 downstream resource conflicts (AV rigs, stage lighting, volunteer stations).

---

### Act 3: CP-SAT Optimization, AI Explanation & HITL Approval (AT-07, AT-08)
1. **Automated Multi-Constraint Solver**:
   - Evaluates candidate venues (`Open Air Theatre`, `Seminar Hall`, `LH-3`, `LH-5`) against capacity, distance, and equipment constraints.
   - Generates mathematically optimal re-homing schedule without violating hard constraints.
2. **AI Supervisor Narrative (`AIExplainer`)**:
   - Synthesizes clear, watermarked operator summary: `[AI-GENERATED SUMMARY — HUMAN VERIFICATION REQUIRED]`.
   - Explicitly cites rejected candidate venues and capacity differentials.
3. **Simulation Branch & Approval Gate**:
   - Baseline state remains immutable while proposal branch `prop_kbc_disruption_001` is evaluated.
   - Operator reviews the full diff and signs off via one-click HITL approval.

---

### Act 4: Bidirectional Notion Outbound Commit (Golden Slice)
1. **Deterministic Execution**:
   - Exactly **32 Notion write operations** executed idempotently via rate-limited adapter.
   - Updates session venues, times, task reassignments, volunteer rosters, and equipment transports.
2. **Post-Commit Verification**:
   - Reads back modified pages with HMAC verification to ensure 100% data consistency.

---

### Act 5: Weather Escalation & Chained Outdoor Branch (AT-02)
1. **Severe Weather Ingestion**:
   - 15:30 hrs: IMD Met Centre Bhubaneswar issues Red Alert: 90% lightning probability, 25mm/hr rain over Campus 6 Open Air Theatre.
2. **Chained Disruption Proposal**:
   - System recognizes sessions relocated to OAT are now compromised.
   - Generates secondary simulation branch `br_wx_chained_002` re-routing sessions to indoor **Campus 6 Multipurpose Hall**.
   - Triggers targeted SMS / Push notifications to affected attendees and volunteers.

---

### Act 6: Mobility, Shuttle Reallocation & Crowd Surges (AT-03, AT-04, AT-05)
1. **Shuttle Breakdown Reallocation (AT-03)**:
   - Shuttle EV-01 breaks down; replacement electric shuttle dispatched immediately; stranded cohort notified.
2. **Gate 2 Crowd Surge & Dynamic Rerouting (AT-04, AT-05)**:
   - Anonymous density telemetry at Gate 2 hits 96% capacity.
   - Visual alert pulses red on the Campus Map; operator approves recommended crowd detour to Gate 4 North Plaza.
   - Live PWA schedules refresh in realtime (< 500ms).

---

### Act 7: Event Close, Post-Event Synthesis & Institutional Memory (AT-10)
1. **Automated Post-Event Report (`FR-KB-001`)**:
   - Synthesizes complete operational log: 48 sessions, 2 disruptions resolved, 2 proposals approved, 22 shuttle trips, 97.9% completion rate.
2. **Institutional Knowledge Playbook (`FR-KB-002`, `RULE-10`)**:
   - Curates "Double-Disruption Cascading Stage Relocation Playbook" into RAG vector memory with complete grounding citations.
   - Available as institutional guidance for future editions of KIIT Fest / KBC.

---

**Demonstration Status:** 100% Automated, Deterministic & Green.
