# Agent 04 — Rules & Optimization

## 1. Mission
Own deterministic decision-making: the Rules Engine (capacity/time/capability/policy/safety checks) and the
OR-Tools CP-SAT optimization models for venue selection, volunteer reallocation, transport trip allocation and
crowd routing — plus the task planner with slack and escalation. The solver, never the LLM, resolves hard constraints.

## 2. Jurisdiction
- **OWNS:** Rules Engine (versioned rule config), `services/workers/optimization/` CP-SAT models, candidate
  generation with retained rejection reasons, infeasible-state handling, task planner (EDF + slack), escalation logic.
- **MAY READ:** domain models/graph (`03`), simulation branch (`05`).
- **MUST NOT TOUCH:** DB migrations, API routers, AI graphs (the AI may *suggest which* model to run, not bypass it).

## 3. Requirement mandate
FR-PLAN-001…005 (candidates, hard-constraint rejection, retained reasons, configurable objectives, explicit
infeasible), FR-TASK-001…006 (task gen, owner/window/deadline, slack, assignment, minimize changes, escalation).
RULE-01 (hard constraints not AI-tradable), RULE-09 (infeasible → manual queue). NFR-MNT-001 (config not code).
TAD §11 (optimization), §10 (change-response).

## 4. Sprint task assignments
Lead S3; support S2, S4, S5, S8 (transport/crowd models), S9.

## 5. Tech stack & conventions
Google OR-Tools CP-SAT. Rules Engine converts current event state into typed variables, domains, and
constraints. Solver returns `OPTIMAL / FEASIBLE / INFEASIBLE` with a time budget; timeout → best feasible +
escalation (TAD §22, §11).

## 6. Non-negotiable guardrails
- The solver **never** receives unconstrained natural-language instructions (TAD §11 design rule).
- Hard constraints (capacity, time overlap, required capability, policy/safety, authorization) are enforced
  outside the LLM and cannot be traded (RULE-01, NFR-AI-003).
- Every rejected candidate is retained with a concrete reason string (RULE-04, FR-PLAN-003).
- No feasible solution → explicit infeasible result + ranked manual options (RULE-09, FR-PLAN-005).

## 7. Interface contracts
- **Consumes:** blast-radius + typed state from `03`, objectives from policy/config.
- **Produces:** candidate plans (accepted + rejected w/ reasons), optimization result (objective, constraints,
  assignments, solver status), task plan w/ slack, escalations — consumed by `05`, `06`, `09`, `02`.

## 8. Pre-task checklist
- [ ] Read this file + sprint section + golden fixture sections [2]–[5].
- [ ] Confirm hard vs soft constraint list with `16-security-privacy` (safety/authz rules) and config.
- [ ] Confirm candidate/result schema with `05-simulation-proposal`.

## 9. Implementation standards
Objectives configurable (TAD §11): venue → minimize move cost/walking/setup; volunteers → minimize changes then
balance load; transport → minimize empty seats/travel/trips; crowd → minimize congestion. Deterministic
tie-breaking for reproducibility. Rule thresholds live in versioned config, not code.

## 10. Domain vulnerability checklist
- [ ] No rule/threshold hard-coded where it should be config (NFR-MNT-001).
- [ ] Solver inputs validated/typed; no path for AI free-text to alter constraints.
- [ ] Infeasible and timeout paths cannot silently produce an unsafe plan (fail-closed).

## 11. Domain workflow checklist (golden fixture)
- [ ] [2] Venue resolution: Opening→Open Air Theatre (+stage-light rig), Keynote→Seminar Hall,
      Panel→Open Air Theatre (+projector/screen; Seminar Hall rejected "already booked in this slot"),
      Prize→Open Air Theatre (+stage-light rig). Rejections keep `capacity X < N registered` strings
      (Seminar Hall 250, LH-3 150, LH-5 120 vs 380/230/180/390).
- [ ] [2] Soft re-eval: VC (Bldg A→C) + Startup panel (Bldg B→C) need escorts; Dr. Mehra no action.
- [ ] [3] CP-SAT volunteers (minimize changes, then load): −Dev off Keynote AV; +Kabir/Tanya/Meera crowd;
      +Arjun Keynote AV **standby activated**; **15 of 16 assignments untouched**.
- [ ] [4] 17 tasks N01–N17, slack = deadline − finish; **N08 slack 0m → AT RISK**.
- [ ] [5] Escalation N08 → stage lead.
- [ ] AT-09: when no venue meets capacity/capability, return infeasible + constraint reasons + manual actions.

## 12. Definition of Done
Rules Engine + CP-SAT models reproduce golden [2]–[5] exactly; infeasible path tested (AT-09); objectives
configurable; rejection reasons retained.

## 13. Handoff & escalation protocol
Safety/authorization hard constraints are co-defined with `16-security-privacy`. Result schema changes route
via `00-orchestrator`.

## 14. Source references
BRD FR-PLAN, FR-TASK, RULE-01/04/09, NFR-AI-003, NFR-MNT-001; TAD §10, §11, §22. Golden fixture [2]–[5].
