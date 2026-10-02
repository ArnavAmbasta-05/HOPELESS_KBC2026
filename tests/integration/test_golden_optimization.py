"""Integration and Golden Simulation Tests for Sprint 3 (Rules, Optimization, Task Planning).

Validates sections [2], [3], [4], [5] of the Golden Simulation Fixture (kbc03_simulation_output.txt)
and the AT-09 Infeasible Fallback.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from packages.contracts.planning import SolverStatus
from packages.domain.seed import load_golden_seed
from services.api.auth.providers import DevLoginProvider
from services.api.main import app
from services.workers.optimization.config import get_rule_config
from services.workers.optimization.infeasible import InfeasibleResolutionHandler
from services.workers.optimization.task_planner import TaskPlanner
from services.workers.optimization.venue_resolver import VenueResolver
from services.workers.optimization.volunteer_solver import VolunteerSolver


def _make_auth_header(role: str = "ops_lead", sub: str = "test-user") -> dict[str, str]:
    provider = DevLoginProvider()
    token = provider.create_token(
        email=f"{sub}@korex.kiit.ac.in",
        name=sub,
        roles=[role],
        event_id="evt_kbc2026",
    )
    return {"Authorization": f"Bearer {token}"}


class TestGoldenVenueResolution:
    """Golden Section [2] Tests."""

    def test_golden_venue_assignments_and_rejections(self) -> None:
        resolver = VenueResolver()
        seed = load_golden_seed()
        res = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id="ven_main_aud")

        assert res.status == SolverStatus.OPTIMAL
        assert len(res.assignments) == 4

        # 1. Opening Ceremony -> Open Air Theatre
        opening = next(a for a in res.assignments if a.session_id == "ses_opening")
        assert opening.new_venue_name == "Open Air Theatre"
        assert "Portable stage-light rig" in opening.required_equipment
        assert len(opening.rejections) == 3
        rejection_texts = [r.reason for r in opening.rejections]
        assert any("Seminar Hall: capacity 250 < 380" in t for t in rejection_texts)
        assert any("LH-3: capacity 150 < 380" in t for t in rejection_texts)
        assert any("LH-5: capacity 120 < 380" in t for t in rejection_texts)

        # 2. Keynote: AI in FinTech -> Seminar Hall
        keynote = next(a for a in res.assignments if a.session_id == "ses_keynote_ai_fintech")
        assert keynote.new_venue_name == "Seminar Hall"
        assert len(keynote.rejections) == 2
        rejection_texts = [r.reason for r in keynote.rejections]
        assert any("LH-3: capacity 150 < 230" in t for t in rejection_texts)
        assert any("LH-5: capacity 120 < 230" in t for t in rejection_texts)

        # 3. Panel: Building Startups -> Open Air Theatre
        panel = next(a for a in res.assignments if a.session_id == "ses_panel_startups")
        assert panel.new_venue_name == "Open Air Theatre"
        assert "Portable projector + screen" in panel.required_equipment
        assert len(panel.rejections) == 3
        rejection_texts = [r.reason for r in panel.rejections]
        assert any("Seminar Hall: already booked in this slot" in t for t in rejection_texts)
        assert any("LH-3: capacity 150 < 180" in t for t in rejection_texts)
        assert any("LH-5: capacity 120 < 180" in t for t in rejection_texts)

        # 4. Prize Distribution -> Open Air Theatre
        prize = next(a for a in res.assignments if a.session_id == "ses_prize_dist")
        assert prize.new_venue_name == "Open Air Theatre"
        assert "Portable stage-light rig" in prize.required_equipment
        assert len(prize.rejections) == 3
        rejection_texts = [r.reason for r in prize.rejections]
        assert any("Seminar Hall: capacity 250 < 390" in t for t in rejection_texts)
        assert any("LH-3: capacity 150 < 390" in t for t in rejection_texts)
        assert any("LH-5: capacity 120 < 390" in t for t in rejection_texts)

        # Total rejections logged across 4 sessions = 3 + 2 + 3 + 3 = 11
        assert res.total_rejections_logged == 11

    def test_golden_speaker_soft_reevaluation(self) -> None:
        resolver = VenueResolver()
        seed = load_golden_seed()
        res = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id="ven_main_aud")

        speakers = res.speaker_reevaluations
        assert len(speakers) == 5

        # VC -> escort needed
        vc = next(s for s in speakers if s.speaker_id == "spk_chief_guest")
        assert vc.escort_needed is True
        assert vc.status_symbol == "✗"
        assert "arrives at Bldg A, venue now Bldg C → escort needed" in vc.note

        # Dr. Mehra -> no action
        dr_mehra = next(s for s in speakers if s.speaker_id == "spk_dr_mehra")
        assert dr_mehra.escort_needed is False
        assert dr_mehra.status_symbol == "✓"
        assert "arrival building unchanged, no action" in dr_mehra.note

        # 3 Founders -> escort needed
        founders = [s for s in speakers if s.speaker_id in ("spk_ankit", "spk_priya", "spk_ravi")]
        assert len(founders) == 3
        for f in founders:
            assert f.escort_needed is True
            assert f.status_symbol == "✗"
            assert "arrives at Bldg B, venue now Bldg C → escort needed" in f.note


class TestGoldenVolunteerReallocation:
    """Golden Section [3] Tests."""

    def test_golden_volunteer_cp_sat_solver(self) -> None:
        solver = VolunteerSolver()
        seed = load_golden_seed()
        res = solver.solve_reallocation(seed=seed, disrupted_venue_id="ven_main_aud")

        assert res.status == SolverStatus.OPTIMAL
        assert res.untouched_count == 15
        assert res.total_volunteers == 17
        assert "Arjun" in res.standby_activations

        # Check changes
        names_actions = [(c.name, c.action) for c in res.changes]
        assert ("Dev", "removed") in names_actions
        assert ("Kabir", "assigned") in names_actions
        assert ("Tanya", "assigned") in names_actions
        assert ("Meera", "assigned") in names_actions
        assert ("Arjun", "standby_activated") in names_actions


class TestGoldenTaskPlannerAndEscalations:
    """Golden Sections [4] and [5] Tests."""

    def test_golden_17_tasks_and_slack(self) -> None:
        planner = TaskPlanner()
        seed = load_golden_seed()
        res = planner.generate_plan(seed=seed)

        assert res.total_tasks == 17
        task_ids = [t.task_id for t in res.tasks]
        assert len(set(task_ids)) == 17

        # Assert N08 is AT RISK with slack 0m
        n08 = next(t for t in res.tasks if t.task_id == "N08")
        assert n08.slack_minutes == 0
        assert n08.is_at_risk is True
        assert n08.description == "Opening act rehearsal at Open Air Theatre"

        # Assert all other tasks have positive slack
        for t in res.tasks:
            if t.task_id != "N08":
                assert t.slack_minutes > 0
                assert t.is_at_risk is False

        # Check specific slacks
        n01 = next(t for t in res.tasks if t.task_id == "N01")
        assert n01.slack_minutes == 25
        n14 = next(t for t in res.tasks if t.task_id == "N14")
        assert n14.slack_minutes == 420

        # Golden Section [5] Escalation
        assert len(res.escalations) == 1
        esc = res.escalations[0]
        assert esc.task_id == "N08"
        assert esc.slack == "0m"
        assert esc.escalate_to_role == "stage_lead"
        assert "notify stage_lead" in esc.reason


class TestInfeasibleResolution:
    """AT-09 Infeasible Path Tests."""

    def test_infeasible_handler_returns_reasons_and_manual_queue(self) -> None:
        handler = InfeasibleResolutionHandler()
        res = handler.handle_infeasible_session(
            event_id="ev_kbc2026",
            disrupted_entity_id="ses_mega",
            session_name="Mega Concert",
            registrants=1200,
            available_candidate_capacities={"Open Air Theatre": 600, "Seminar Hall": 250, "LH-3": 150},
        )

        assert res.status == SolverStatus.INFEASIBLE
        assert len(res.unmet_constraints) == 3
        assert any("capacity 600 < 1200" in c for c in res.unmet_constraints)
        assert len(res.manual_action_options) == 4
        assert res.manual_action_options[0].rank == 1


class TestPlanningAPI:
    """REST API verification for planning endpoints."""

    @pytest.mark.asyncio
    async def test_resolve_venues_api(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = _make_auth_header("ops_lead")
            resp = await client.post("/api/v1/planning/resolve-venues?unavailable_venue_id=ven_main_aud", headers=headers)
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["status"] == "optimal"
            assert len(data["assignments"]) == 4
            assert len(data["speaker_reevaluations"]) == 5

    @pytest.mark.asyncio
    async def test_reallocate_volunteers_api(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = _make_auth_header("volunteer_coordinator")
            resp = await client.post("/api/v1/planning/reallocate-volunteers", headers=headers)
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["status"] == "optimal"
            assert data["untouched_count"] == 15
            assert "Arjun" in data["standby_activations"]

    @pytest.mark.asyncio
    async def test_generate_tasks_api(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = _make_auth_header("event_commander")
            resp = await client.post("/api/v1/planning/generate-tasks", headers=headers)
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["total_tasks"] == 17
            assert len(data["at_risk_tasks"]) == 1
            assert data["at_risk_tasks"][0]["task_id"] == "N08"

    @pytest.mark.asyncio
    async def test_infeasible_check_api(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = _make_auth_header("ops_lead")
            resp = await client.post("/api/v1/planning/infeasible-check", headers=headers)
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["status"] == "infeasible"
            assert len(data["manual_action_options"]) == 4

    @pytest.mark.asyncio
    async def test_planning_rbac_denial(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Unknown or unpermitted role should be denied (403)
            headers = _make_auth_header("unauthorized_guest")
            resp = await client.post("/api/v1/planning/resolve-venues", headers=headers)
            assert resp.status_code == 403
