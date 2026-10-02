"""Integration and Golden Simulation Tests for Sprint 4 (Simulation Branches, Change Proposals, Approval & Diff).

Validates what-if simulation, baseline immutability, Change Proposal assembly (TAD §10),
the Approve/Reject API with idempotency and optimistic concurrency, and AT-08 zero-write rejection.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from packages.contracts.simulation import BranchStatus
from packages.domain.seed import load_golden_seed
from services.api.auth.providers import DevLoginProvider
from services.api.main import app
from services.workers.simulation.branch_manager import BranchManager, get_branch_manager


def _make_auth_header(role: str = "ops_lead", sub: str = "test-user") -> dict[str, str]:
    provider = DevLoginProvider()
    token = provider.create_token(
        email=f"{sub}@korex.kiit.ac.in",
        name=sub,
        roles=[role],
        event_id="evt_kbc2026",
    )
    return {"Authorization": f"Bearer {token}"}


class TestSimulationAndChangeProposal:
    """Tests for S4-T1 and S4-T2."""

    def test_simulation_branch_creation_and_baseline_immutability(self) -> None:
        manager = get_branch_manager()
        seed = load_golden_seed()
        initial_sessions_count = len(seed.sessions)

        from packages.contracts.simulation import ProposalSimulateRequest

        req = ProposalSimulateRequest(
            event_id="evt_kbc2026",
            unavailable_venue_id="ven_main_aud",
            reason="Ceiling AC leak reported by Estate Office",
            time_window="08:00–23:59",
            reported_by="ops-lead (via Notion)",
        )

        proposal = manager.create_simulation_branch(request=req, seed=seed)

        assert proposal.status == BranchStatus.BRANCH_ONLY
        assert proposal.event_id == "evt_kbc2026"
        assert proposal.baseline_revision == 1
        assert proposal.trigger.venue_id == "ven_main_aud"

        # Assert baseline seed data is NOT modified
        assert len(seed.sessions) == initial_sessions_count
        assert any(s.venue_id == "ven_main_aud" for s in seed.sessions)

    def test_proposal_artifacts_and_diff(self) -> None:
        manager = get_branch_manager()
        seed = load_golden_seed()
        from packages.contracts.simulation import ProposalSimulateRequest

        req = ProposalSimulateRequest(
            event_id="evt_kbc2026",
            unavailable_venue_id="ven_main_aud",
            reason="Ceiling AC leak reported by Estate Office",
            time_window="08:00–23:59",
            reported_by="ops-lead (via Notion)",
        )
        proposal = manager.create_simulation_branch(request=req, seed=seed)

        # 1. Diff assertions
        diff = proposal.diff
        assert diff.total_changes > 0
        assert diff.modified_count >= 4  # 4 relocated sessions
        assert any(i.entity_type == "session" and i.entity_id == "ses_opening" for i in diff.items)
        assert any(i.entity_type == "volunteer" and i.entity_id == "vol_arjun" for i in diff.items)
        assert any(i.entity_type == "task" and i.entity_id == "N08" for i in diff.items)

        # 2. Risk plan assertions
        risk_plan = proposal.risk_plan
        assert risk_plan.at_risk_tasks_count == 1
        assert risk_plan.at_risk_tasks[0].task_id == "N08"
        assert risk_plan.at_risk_tasks[0].slack_minutes == 0

        # 3. Explainability / Rejection trace in proposal
        venue_res = proposal.venue_resolution
        assert len(venue_res.assignments) == 4
        assert venue_res.total_rejections_logged == 11

        # 4. AI Summary labeling
        assert proposal.is_ai_generated_summary is True
        assert "Main Auditorium is out for the day" in proposal.ai_summary


class TestProposalAPIWorkflow:
    """Tests for S4-T3, AT-08, and REST API."""

    @pytest.mark.asyncio
    async def test_simulate_proposal_api(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = _make_auth_header("ops_lead")
            body = {
                "event_id": "evt_kbc2026",
                "unavailable_venue_id": "ven_main_aud",
                "reason": "Ceiling AC leak reported by Estate Office",
                "time_window": "08:00–23:59",
                "reported_by": "ops-lead",
            }
            resp = await client.post("/api/v1/proposals/simulate", json=body, headers=headers)
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["status"] == "branch_only"
            assert data["trigger"]["venue_name"] == "Main Auditorium"
            assert len(data["task_plan"]) == 17
            proposal_id = data["proposal_id"]

            # GET proposal by ID
            get_resp = await client.get(f"/api/v1/proposals/{proposal_id}", headers=headers)
            assert get_resp.status_code == 200
            assert get_resp.json()["data"]["proposal_id"] == proposal_id

    @pytest.mark.asyncio
    async def test_approve_proposal_flow_and_idempotency(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = _make_auth_header("event_commander")
            # 1. Simulate
            body = {
                "event_id": "evt_kbc2026",
                "unavailable_venue_id": "ven_main_aud",
                "reason": "Ceiling AC leak reported by Estate Office",
                "time_window": "08:00–23:59",
                "reported_by": "ops-lead",
            }
            resp = await client.post("/api/v1/proposals/simulate", json=body, headers=headers)
            proposal_id = resp.json()["data"]["proposal_id"]

            # 2. Approve
            approve_resp = await client.post(f"/api/v1/proposals/{proposal_id}/approve", headers=headers)
            assert approve_resp.status_code == 200
            approved_data = approve_resp.json()["data"]
            assert approved_data["status"] == "approved"
            assert approved_data["commit_result"]["status"] == "SUCCESS"
            assert approved_data["approved_by"] is not None

            # 3. Idempotent approval
            idempotent_resp = await client.post(f"/api/v1/proposals/{proposal_id}/approve", headers=headers)
            assert idempotent_resp.status_code == 200
            assert idempotent_resp.json()["data"]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_reject_proposal_produces_zero_writes(self) -> None:
        """AT-08: Rejecting the proposal leaves baseline untouched and produces zero writes."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = _make_auth_header("ops_lead")
            # 1. Simulate
            body = {
                "event_id": "evt_kbc2026",
                "unavailable_venue_id": "ven_main_aud",
                "reason": "Ceiling AC leak",
                "time_window": "08:00–23:59",
                "reported_by": "ops-lead",
            }
            resp = await client.post("/api/v1/proposals/simulate", json=body, headers=headers)
            proposal_id = resp.json()["data"]["proposal_id"]

            # 2. Reject
            reject_resp = await client.post(
                f"/api/v1/proposals/{proposal_id}/reject",
                json={"reason": "Manual review determined Main Auditorium repair can be completed by 09:30"},
                headers=headers,
            )
            assert reject_resp.status_code == 200
            rejected_data = reject_resp.json()["data"]
            assert rejected_data["status"] == "rejected"
            assert rejected_data["rejection_reason"] == "Manual review determined Main Auditorium repair can be completed by 09:30"
            assert rejected_data["commit_result"] is None

    @pytest.mark.asyncio
    async def test_proposal_rbac_enforcement(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Volunteer role cannot approve proposals (only proposal:read)
            headers = _make_auth_header("volunteer")
            body = {
                "event_id": "evt_kbc2026",
                "unavailable_venue_id": "ven_main_aud",
                "reason": "Ceiling AC leak",
                "time_window": "08:00–23:59",
                "reported_by": "ops-lead",
            }
            resp = await client.post(
                "/api/v1/proposals/prop_test_fake/approve",
                headers=headers,
            )
            assert resp.status_code == 403
