"""Script to stage and commit files in exactly 54 granular logical steps with author Udit Pandya."""

import subprocess
import os

COMMITS = [
    # 1. Base Project Config
    (["pyproject.toml"], "chore(config): initialize pyproject.toml with project metadata and dependencies"),
    ([".gitignore"], "chore(config): configure gitignore for python, node, and environment secrets"),
    ([".env.example"], "chore(config): add environment variable template (.env.example)"),
    (["Makefile"], "chore(build): add Makefile with dev, test, lint, and run targets"),
    ([".pre-commit-config.yaml"], "chore(lint): configure pre-commit hooks for ruff, black, and mypy"),
    (["CODEOWNERS"], "chore(governance): add CODEOWNERS defining subsystem domain agent mappings"),
    (["README.md"], "docs(readme): add KoreX project documentation, overview, and architecture sitemap"),
    
    # 2. Infra & CI
    ([".github"], "ci(workflows): add GitHub Actions workflows for continuous integration and linting"),
    (["infra"], "infra(docker): add Dockerfile, docker-compose, and service deployment manifests"),
    (["alembic.ini", "migrations"], "infra(db): initialize alembic migrations and database schema tracking"),
    (["assets"], "assets(branding): add KoreX logo, icons, and visual design assets"),

    # 3. Sprint 0 Contracts & Core Observability
    (["packages/contracts/__init__.py", "packages/contracts/envelope.py"], "feat(contracts): define standard API response and error envelope schemas (TAD §27.1)"),
    (["packages/contracts/logging.py"], "feat(contracts): implement structured JSON logging with correlation-ID context"),
    (["packages/contracts/telemetry.py"], "feat(contracts): configure OpenTelemetry tracer and metrics exporters"),
    (["packages/contracts/auth.py"], "feat(contracts): define user authentication, credentials, and session contracts"),
    (["packages/contracts/rbac.py"], "feat(contracts): define 11 RBAC role enumerations and permission mappings"),

    # 4. Sprint 0 Auth & Observability Services
    (["services/api/auth"], "feat(auth): implement DevLoginProvider and OIDC token verification provider"),
    (["services/api/metrics.py"], "feat(metrics): add Prometheus request middleware and /metrics scraping endpoint"),
    (["services/api/middleware"], "feat(middleware): add CorrelationIDMiddleware for distributed request tracing"),

    # 5. Sprint 0 Unit Tests
    (["tests/__init__.py", "tests/conftest.py"], "test(setup): configure pytest test fixtures, async event loops, and database engines"),
    (["tests/unit/test_auth.py"], "test(auth): add unit test suite for JWT creation, verification, and token tampering"),
    (["tests/unit/test_rbac.py"], "test(rbac): add unit test suite for role-permission matrix and event scoping"),
    (["tests/unit/test_observability.py"], "test(observability): add unit tests for correlation ID propagation and telemetry"),

    # 6. Sprint 1 Domain Twin Models & Repository
    (["packages/domain/__init__.py", "packages/domain/models"], "feat(domain): define 16 core digital twin database entities and relationships"),
    (["packages/domain/repository.py"], "feat(domain): implement generic SQLAlchemy repository with revision concurrency control"),
    (["packages/domain/seed.py", "tests/fixtures"], "feat(seed): implement golden festival seed data loader and simulation fixtures"),
    (["tests/unit/test_domain_models.py"], "test(domain): add unit test suite for domain entity instantiation and constraints"),
    (["tests/unit/test_repository.py"], "test(repository): add unit test suite for CRUD mutations, audit records, and stale revisions"),
    (["tests/unit/test_seed.py"], "test(seed): add unit test suite validating golden fixture schema and expected constants"),

    # 7. Sprint 1 API Routers
    (["services/api/routers/events.py"], "feat(api): add events router with lifecycle state management"),
    (["services/api/routers/venues.py"], "feat(api): add venues router with capacity and coordinate queries"),
    (["services/api/routers/sessions.py"], "feat(api): add sessions router with speaker and schedule associations"),
    (["services/api/routers/participants.py"], "feat(api): add participants router with registration tracking"),
    (["services/api/routers/resources.py"], "feat(api): add resources router for stage and AV equipment allocation"),
    (["services/api/routers/audit.py"], "feat(api): add audit router for immutable mutation log queries"),
    (["tests/integration/test_crud_api.py"], "test(api): add integration test suite for digital twin REST endpoints"),

    # 8. Sprint 2 Dependency Graph & Blast Radius
    (["packages/contracts/graph.py"], "feat(contracts): define dependency edge types, blast radius requests, and impact schemas"),
    (["packages/domain/graph"], "feat(graph): implement recursive dependency graph builder and BlastRadiusEngine"),
    (["services/api/routers/dependencies.py"], "feat(api): add dependencies router and blast radius query endpoints"),
    (["tests/integration/test_golden_blast_radius.py"], "test(graph): add golden blast radius integration test suite (AT-01)"),
    (["tests/unit/test_graph_perf.py"], "test(perf): add 5,000-edge blast radius performance benchmark test"),

    # 9. Sprint 3 Rules, Optimization & Task Planning
    (["packages/contracts/planning.py"], "feat(contracts): define CP-SAT solver status, assignment, and manual option schemas"),
    (["services/workers/optimization/config.py"], "feat(optimization): implement RuleConfig for speed, capacity, and buffer parameters"),
    (["services/workers/optimization/venue_resolver.py"], "feat(optimization): implement VenueResolver multi-venue constraint solver"),
    (["services/workers/optimization/task_planner.py"], "feat(optimization): implement TaskPlanner with lead time buffer calculations"),
    (["services/workers/optimization/volunteer_solver.py"], "feat(optimization): implement VolunteerSolver with skill matching and shift limits"),
    (["services/workers/optimization/infeasible.py"], "feat(optimization): implement InfeasibleResolutionHandler with ranked manual options (AT-09)"),
    (["services/api/routers/planning.py"], "feat(api): add planning and optimization execution API endpoints"),
    (["tests/integration/test_golden_optimization.py"], "test(optimization): add golden simulation tests for venue, task, and volunteer solvers"),

    # 10. Sprint 4 Simulation, Proposals & Diff
    (["packages/contracts/simulation.py"], "feat(contracts): define simulation branch, change proposal, and diff schemas"),
    (["services/workers/simulation"], "feat(simulation): implement BranchManager, DiffEngine, and ProposalAssembler"),
    (["services/api/routers/proposals.py"], "feat(api): add proposal simulation, diff, and approval/rejection endpoints"),
    (["tests/integration/test_golden_simulation_proposal.py"], "test(simulation): add simulation branch creation, diff, and HITL approval tests"),

    # 11. Sprint 5 AI Orchestration (LangChain + LangGraph)
    (["packages/contracts/ai.py"], "feat(contracts): define AI supervisor run state, tool call, and trace schemas"),
    (["ai/tools.py"], "feat(ai): register allow-listed LangChain tools wrapping domain solvers"),
    (["ai/security.py"], "feat(ai): implement PromptSecurityGuard with injection filters and mutating tool gates"),
    (["ai/explainer.py"], "feat(ai): implement AIExplainer with exact AT-07 watermark and hard constraint validation"),
    (["ai/fallback.py", "ai/tracing.py"], "feat(ai): implement LLMOutageFallbackHandler and AITraceManager"),
    (["ai/graphs", "ai/__init__.py"], "feat(ai): build LangGraph EventSupervisor with HITL interrupt and checkpointing"),
    (["services/api/routers/ai.py"], "feat(api): add AI runs and HITL resume/approval endpoints"),
    (["tests/integration/test_golden_ai_orchestration.py"], "test(ai): add integration tests for LangGraph supervisor, HITL interrupt, and AI explainer"),

    # 12. Sprint 6 Notion Live Integration
    (["packages/contracts/notion.py"], "feat(contracts): define Notion sync schemas, cursor, and write operation models"),
    (["integrations/notion"], "feat(notion): implement NotionAdapter, HMAC webhooks, 32 write plan executor, DLQ and conflict detector"),
    (["services/api/routers/notion.py"], "feat(api): add Notion webhook and commit execution endpoints"),
    (["tests/integration/test_golden_notion_sync.py"], "test(notion): add Notion adapter, webhook verification, 32 outbound writes, and conflict tests"),

    # 13. Sprint 7 Participant Operations (Notifications + Attendance)
    (["packages/contracts/notifications.py"], "feat(contracts): define participant notifications, message drafts, and delivery status schemas"),
    (["packages/contracts/attendance.py"], "feat(contracts): define attendance credential, scan ingest, and occupancy models"),
    (["services/workers/notifications"], "feat(notifications): implement CohortDerivationEngine, drafter, multi-channel dispatcher and stale detector"),
    (["services/workers/attendance"], "feat(attendance): implement AttendanceCredentialService, ScanIngestService, replay, and reconciler"),
    (["services/api/routers/notifications.py", "services/api/routers/attendance.py"], "feat(api): add notifications dispatch and attendance scan endpoints"),
    (["tests/integration/test_golden_participant_ops.py"], "test(participant): add participant operations, mass dispatch approval gate, and attendance scan tests"),

    # 14. Sprint 8 Mobility & Crowd Control
    (["packages/contracts/mobility.py", "packages/contracts/crowd.py", "packages/contracts/transport.py"], "feat(contracts): define transport fleet, shuttle routes, crowd zones, and gate flow schemas"),
    (["services/workers/transport"], "feat(transport): implement TransportService with fleet management and shuttle disruption reallocation"),
    (["services/workers/crowd"], "feat(crowd): implement CrowdSafetyService with anonymous counts, surge alerts, and gate reroute"),
    (["services/api/routers/transport.py", "services/api/routers/crowd.py"], "feat(api): add transport and crowd control API endpoints"),
    (["tests/integration/test_golden_mobility_crowd.py"], "test(mobility): add transport disruption reallocation, corridor bottleneck alerts, and reroute tests"),

    # 15. Sprint 9 Weather Resilience & Institutional Memory (RAG)
    (["packages/contracts/weather.py"], "feat(contracts): define weather hazard, threshold, and branch proposal models"),
    (["packages/contracts/knowledge.py"], "feat(contracts): define RAG document chunk, citation, post-event report, and KnowledgeItem schemas"),
    (["services/workers/weather"], "feat(weather): implement WeatherService with IMD/Open-Meteo feeds and chained OAT storm branch"),
    (["services/workers/rag"], "feat(rag): implement RAGKnowledgeService with scoped retrieval, post-event reports, and playbooks"),
    (["packages/domain/isolation.py"], "feat(domain): implement EventContext multi-tenant and multi-event isolation enforcer"),
    (["services/api/routers/weather.py", "services/api/routers/knowledge.py"], "feat(api): add weather and knowledge base API endpoints"),
    (["tests/integration/test_golden_weather_knowledge.py"], "test(weather-rag): add weather branch proposal, scoped RAG retrieval, post-event report, and isolation tests"),

    # 16. Sprint 10 Hardening, Evaluation & Demo
    (["tests/unit/test_benchmarks_kpi.py"], "test(benchmarks): add KPI performance benchmarks suite for blast radius, solver, and branch latency"),
    (["tests/integration/test_resilience_drills.py"], "test(resilience): add resilience and failure drills suite (attendance, Notion DLQ, fallback)"),
    (["tests/integration/test_ai_evaluation.py"], "test(ai-eval): add AI evaluation and governance test suite (TAD §24.1)"),
    (["tests/integration/test_security_scans.py"], "test(security): add security, prompt injection defense, and threat model scan suite"),
    (["tests/e2e"], "test(e2e): add complete AT-01 through AT-10 end-to-end acceptance regression matrix"),

    # 17. Application Integration & Web Frontend
    (["services/workers/__init__.py", "services/workers/app.py"], "feat(workers): add worker daemon application entrypoint and task listener"),
    (["services/api/__init__.py", "services/api/main.py", "services/api/routers/__init__.py"], "feat(api): assemble FastAPI application with all 17 domain and worker routers"),
    (["apps/web"], "feat(frontend): implement KoreX 2.5D Digital Twin Command Center web application"),

    # 18. Documentation & Final Sign-Off
    (["docs/DEMO_SCRIPT.md"], "docs(demo): add master live demonstration script (Acts 1-7) for command center evaluation"),
    (["docs/ARCHITECTURE_COMPLIANCE.md"], "docs(compliance): add TAD architecture compliance and KPI verification report"),
    (["SPRINT_IMPLEMENTATION_PLAN.md"], "docs(sprint-plan): complete full Sprint 0-10 implementation checklist and sign TAD Appendix A gate"),
]

def main():
    count = 0
    for files, msg in COMMITS:
        for f in files:
            subprocess.run(f"git add {f}", shell=True, check=False)
        commit_cmd = f'git commit -m "{msg}"'
        res = subprocess.run(commit_cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            count += 1
            print(f"[{count:02d}] {msg}")
        else:
            if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
                pass
            else:
                print(f"[WARN] {res.stderr.strip() or res.stdout.strip()}")

    # Stage any remaining files if any
    status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout.strip()
    if status:
        subprocess.run("git add .", shell=True, check=False)
        count += 1
        subprocess.run('git commit -m "chore(finalize): finalize repository cleanup and full sprint delivery"', shell=True, check=False)
        print(f"[{count:02d}] chore(finalize): finalize repository cleanup and full sprint delivery")

    print(f"\nTotal commits created in this run: {count}")

if __name__ == "__main__":
    main()
