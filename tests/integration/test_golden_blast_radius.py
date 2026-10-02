"""Golden Scenario Blast Radius Regression Test Harness (S2-T4, FR-GRAPH-001..005).

Asserts the exact reproduction of Section [1] of kbc03_simulation_output.txt:
- Exactly 12 hard hits (4 hosts + 2 task_at + 2 mentions + 4 has_registrants)
- Exactly 7 deferred soft edges (5 speakers + 2 volunteer staffing)
- Complete traversal paths from root disruption
- Soft-edge re-evaluation on proposed venue resolution
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.graph import BlastRadiusRequest, ImpactSeverity
from packages.domain.graph.builder import populate_graph_from_seed
from packages.domain.graph.engine import BlastRadiusEngine
from packages.domain.graph.soft_edges import reevaluate_speakers_after_venue_resolution
from tests.fixtures.golden_main_auditorium.expected_values import (
    EXPECTED_HARD_HITS,
    EXPECTED_REGISTRANT_COHORTS,
    EXPECTED_SOFT_EDGES_DEFERRED,
    EXPECTED_SPEAKER_ESCORT_NEEDED,
    EXPECTED_SPEAKER_NO_ACTION,
    EXPECTED_VENUE_REASSIGNMENTS,
)


@pytest.mark.asyncio
async def test_golden_blast_radius_engine_direct(db_session: AsyncSession) -> None:
    # 1. Populate graph from golden seed
    await populate_graph_from_seed(db_session)

    engine = BlastRadiusEngine(db_session)
    request = BlastRadiusRequest(
        event_id="evt_kbc2026",
        root_entity_id="ven_main_aud",
        root_entity_type="venue",
        start_time="08:00:00",
        end_time="23:59:59",
        max_depth=5,
    )

    result = await engine.compute_blast_radius(request)

    # 2. Assert exactly 12 hard hits (FR-GRAPH-001..003)
    assert result.hard_hits_count == EXPECTED_HARD_HITS
    assert len(result.hard_hits) == 12

    # Group hard hits by entity type
    sessions = [n for n in result.hard_hits if n.entity_type == "session"]
    tasks = [n for n in result.hard_hits if n.entity_type == "task"]
    comms = [n for n in result.hard_hits if n.entity_type == "notification"]
    cohorts = [n for n in result.hard_hits if n.entity_type == "cohort"]

    assert len(sessions) == 4, f"Expected 4 sessions, got {len(sessions)}"
    assert len(tasks) == 2, f"Expected 2 tasks, got {len(tasks)}"
    assert len(comms) == 2, f"Expected 2 comms, got {len(comms)}"
    assert len(cohorts) == 4, f"Expected 4 cohorts, got {len(cohorts)}"

    # Check session names and registrants
    session_names = {s.name for s in sessions}
    for expected_name in EXPECTED_REGISTRANT_COHORTS:
        assert expected_name in session_names

    cohort_counts = sorted([c.details.get("count", 0) for c in cohorts])
    assert cohort_counts == [180, 230, 380, 390]

    # Check tasks
    task_names = {t.name for t in tasks}
    assert any("AV setup" in name for name in task_names)
    assert any("Stage decor" in name or "Stage décor" in name for name in task_names)

    # 3. Assert exactly 7 deferred soft edges (FR-GRAPH-005)
    assert result.soft_deferred_count == EXPECTED_SOFT_EDGES_DEFERRED
    assert len(result.soft_deferred) == 7

    speakers = [n for n in result.soft_deferred if n.entity_type == "speaker"]
    volunteers = [n for n in result.soft_deferred if n.entity_type == "volunteer"]

    assert len(speakers) == 5
    assert len(volunteers) == 2

    # 4. Assert traversal paths are non-empty and start with root disruption (FR-GRAPH-004)
    for node in result.hard_hits + result.soft_deferred:
        assert len(node.path) >= 3
        assert node.path[0] == "ven_main_aud"

    # 5. Assert computation time is well within target (≤5 s / 5000 ms)
    assert result.computation_ms < 5000.0


@pytest.mark.asyncio
async def test_golden_blast_radius_api_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    request_payload = {
        "event_id": "evt_kbc2026",
        "root_entity_id": "ven_main_aud",
        "root_entity_type": "venue",
        "start_time": "08:00:00",
        "end_time": "23:59:59",
    }

    res = await async_client.post(
        "/api/v1/dependencies/blast-radius",
        json=request_payload,
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["error"] is None
    data = body["data"]
    assert data["hard_hits_count"] == 12
    assert data["soft_deferred_count"] == 7
    assert data["total_impacted"] == 19


def test_soft_edge_reevaluation() -> None:
    """Test soft-edge re-evaluation with resolved venue assignments (S2-T3)."""
    evaluations = reevaluate_speakers_after_venue_resolution(EXPECTED_VENUE_REASSIGNMENTS)
    assert len(evaluations) == 5

    escort_needed_names = [e.name for e in evaluations if e.escort_needed]
    no_action_names = [e.name for e in evaluations if not e.escort_needed]

    # Chief Guest and 3 Founders need escort
    assert any("Chief Guest" in n for n in escort_needed_names)
    assert any("Ankit" in n for n in escort_needed_names)
    assert any("Priya" in n for n in escort_needed_names)
    assert any("Ravi" in n for n in escort_needed_names)

    # Dr. Mehra is in Bldg B and Seminar Hall is in Bldg B -> No action needed
    assert any("Dr. Mehra" in n for n in no_action_names)
