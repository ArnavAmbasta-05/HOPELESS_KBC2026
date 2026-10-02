"""Integration and Golden Scenario Tests for Sprint 8 (Mobility & Crowd Control).

Validates:
- S8-T1 & S8-T2: Transport Models, Disruption Reallocation (AT-03), Vehicle Tasks & Participant Notices (TRN-001..008)
- S8-T3 & S8-T4: Crowd Zones, Gates, Anonymous Headcount Ingest, Corridor Bottleneck Reroute Proposals (AT-04) & Venue Capacity Advisory (AT-05) (CRD-001..007)
- S8-API: REST Endpoints for Transport and Crowd APIs
"""

from __future__ import annotations

import pytest
import httpx

from packages.contracts.crowd import AlertSeverity
from packages.contracts.mobility import VehicleStatus
from services.api.auth.providers import DevLoginProvider
from services.api.main import app
from services.workers.crowd.service import CrowdSafetyService
from services.workers.transport.service import TransportService


class TestTransportMobilityEngine:
    """Tests for S8-T1 & S8-T2 (TRN-001..008, AT-03)."""

    def test_transport_fleet_and_routes_initialized(self) -> None:
        service = TransportService()
        vehicles = service.get_vehicles()
        routes = service.get_routes()
        trips = service.get_trips()

        assert len(vehicles) >= 3
        assert len(routes) >= 2
        assert len(trips) >= 1

        # Check vehicle capacity and status
        shuttle_02 = [v for v in vehicles if v.vehicle_id == "veh_shuttle_02"][0]
        assert shuttle_02.capacity == 30
        assert shuttle_02.status == VehicleStatus.AVAILABLE

    def test_at03_transport_disruption_and_reallocation_workflow(self) -> None:
        """AT-03: Assigned shuttle unavailable -> recalculate capacity -> propose alternate bus -> notify affected participants."""
        service = TransportService()

        # Trigger disruption on Shuttle 2
        plan = service.handle_transport_disruption(
            disrupted_vehicle_id="veh_shuttle_02",
            reason="Battery management system fault",
        )

        assert plan.disrupted_vehicle_id == "veh_shuttle_02"
        assert plan.reallocated_vehicle_id == "veh_bus_standby_a"
        assert plan.recalculated_capacity == 50  # Upgraded capacity
        assert plan.status == "APPROVED_DISPATCHED"

        # Check driver task (TRN-007)
        assert len(plan.vehicle_tasks) == 1
        task = plan.vehicle_tasks[0]
        assert "Heavy Coach Bus A" in task.instructions
        assert task.pickup_stop_id == "stop_c6_hub"

        # Check participant notice (TRN-006, COM-003)
        assert len(plan.passenger_notices) == 1
        notice = plan.passenger_notices[0]
        assert "Bay 4" in notice.new_pickup
        assert "50 seats" in notice.instructions

        # Check vehicle status transitions
        assert service.vehicles["veh_shuttle_02"].status == VehicleStatus.UNAVAILABLE
        assert service.vehicles["veh_bus_standby_a"].status == VehicleStatus.IN_TRANSIT


class TestCrowdSafetyEngine:
    """Tests for S8-T3 & S8-T4 (CRD-001..007, AT-04/05)."""

    def test_crowd_zones_and_gates_initialized(self) -> None:
        service = CrowdSafetyService()
        zones = service.get_zones()
        gates = service.get_gates()

        assert len(zones) >= 2
        assert len(gates) >= 3

        lawn_zone = [z for z in zones if z.zone_id == "zone_c6_lawn"][0]
        assert lawn_zone.max_safe_capacity == 800
        assert lawn_zone.warning_threshold_ratio == 0.80

    def test_anonymous_people_count_ingest_privacy(self) -> None:
        """CRD-006, ATT-007: Ingest uses only anonymous numbers, no identity tracking."""
        service = CrowdSafetyService()

        # Ingest 250 headcount into Campus 6 Lawn
        zone, alert = service.ingest_anonymous_count(zone_id="zone_c6_lawn", headcount=250)
        assert zone.current_anonymous_count == 250
        assert zone.occupancy_ratio == 0.31
        assert alert is None  # Below 80%

    def test_at04_corridor_bottleneck_and_reroute_proposal_workflow(self) -> None:
        """AT-04: Gate/corridor load exceeds threshold -> alert -> show affected sessions -> propose reroute."""
        service = CrowdSafetyService()

        # Surge headcount: 270 in 300-capacity corridor (90% load)
        alert, proposal = service.evaluate_corridor_surge_and_propose_reroute(
            zone_id="corridor_link_c6_c7",
            surge_count=270,
        )

        assert alert.severity in (AlertSeverity.WARNING, AlertSeverity.CRITICAL)
        assert alert.load_ratio == 0.90
        assert "ses_opening" in alert.affected_sessions

        # Propose rerouting to Gate 2 East
        assert proposal.congested_gate_id == "gate_1_main"
        assert proposal.alternate_gate_id == "gate_2_east"
        assert "Gate 2 East Side Arch" in proposal.guidance_message
        assert proposal.requires_operator_confirm is True

    def test_at05_venue_capacity_advisory_workflow(self) -> None:
        """AT-05: Attendance approaching venue capacity -> crowd/ops advisory."""
        service = CrowdSafetyService()

        # OAT venue headcount at 570/600 (95%)
        advisory = service.trigger_venue_capacity_advisory(
            venue_id="ven_oat",
            venue_name="Open Air Theatre",
            current_headcount=570,
            max_capacity=600,
        )

        assert advisory.severity == "ADVISORY_SURGE"
        assert "overflow viewing area" in advisory.message
        assert len(service.advisories) == 1


class TestMobilityCrowdHTTPAPI:
    """HTTP REST API endpoint tests for Sprint 8 routes."""

    @pytest.mark.asyncio
    async def test_transport_and_crowd_api_endpoints(self) -> None:
        provider = DevLoginProvider()
        token = provider.create_token(email="admin@kiit.ac.in", roles=["event_commander", "transport_coordinator", "security_lead"])
        headers = {"Authorization": f"Bearer {token}"}

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Vehicles API
            veh_resp = await client.get("/api/v1/transport/vehicles", headers=headers)
            assert veh_resp.status_code == 200
            assert len(veh_resp.json()["data"]) >= 3

            # 2. Routes API
            routes_resp = await client.get("/api/v1/transport/routes", headers=headers)
            assert routes_resp.status_code == 200
            assert len(routes_resp.json()["data"]) >= 2

            # 3. Transport Disruption API (AT-03)
            dis_resp = await client.post(
                "/api/v1/transport/disrupt",
                json={"vehicle_id": "veh_shuttle_02", "reason": "Mechanical failure"},
                headers=headers,
            )
            assert dis_resp.status_code == 200
            plan_data = dis_resp.json()["data"]
            assert plan_data["reallocated_vehicle_id"] == "veh_bus_standby_a"

            # 4. Crowd Zones API
            zones_resp = await client.get("/api/v1/crowd/zones", headers=headers)
            assert zones_resp.status_code == 200
            assert len(zones_resp.json()["data"]) >= 2

            # 5. Crowd Gates API
            gates_resp = await client.get("/api/v1/crowd/gates", headers=headers)
            assert gates_resp.status_code == 200
            assert len(gates_resp.json()["data"]) >= 3

            # 6. Evaluate Surge API (AT-04)
            surge_resp = await client.post(
                "/api/v1/crowd/evaluate-surge",
                json={"zone_id": "corridor_link_c6_c7", "surge_count": 270},
                headers=headers,
            )
            assert surge_resp.status_code == 200
            surge_data = surge_resp.json()["data"]
            assert surge_data["proposal"]["alternate_gate_id"] == "gate_2_east"

            # 7. Venue Capacity Advisory API (AT-05)
            adv_resp = await client.post(
                "/api/v1/crowd/advisory",
                json={
                    "venue_id": "ven_oat",
                    "venue_name": "Open Air Theatre",
                    "current_headcount": 570,
                    "max_capacity": 600,
                },
                headers=headers,
            )
            assert adv_resp.status_code == 200
            assert adv_resp.json()["data"]["severity"] == "ADVISORY_SURGE"
