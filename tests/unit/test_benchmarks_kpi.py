"""Sprint 10: Performance & KPI Benchmarks Suite (S10-T1, TAD §23, §5.1, NFR-PERF-001..003)."""

from __future__ import annotations

import time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.graph import BlastRadiusRequest, EdgeType
from packages.contracts.simulation import ProposalSimulateRequest
from packages.domain.graph.engine import BlastRadiusEngine
from packages.domain.models import DependencyEdge
from packages.domain.seed import load_golden_seed
from services.workers.notifications.service import NotificationService
from services.workers.optimization.venue_resolver import VenueResolver
from services.workers.simulation.branch_manager import BranchManager


@pytest.mark.asyncio
async def test_kpi_graph_blast_radius_performance(db_session: AsyncSession):
    """Benchmark: Impact calculation <= 5s for 5,000 edges (TAD §23, §5.1)."""
    event_id = "evt_perf_kpi"
    num_nodes = 500
    edges_per_node = 10

    edge_objects: list[DependencyEdge] = []
    for i in range(num_nodes):
        source_id = f"node_{i}"
        for j in range(1, edges_per_node + 1):
            target_id = f"node_{(i * edges_per_node + j) % (num_nodes * 2)}"
            edge = DependencyEdge(
                edge_id=f"edge_kpi_{i}_{j}",
                event_id=event_id,
                source_id=source_id,
                target_id=target_id,
                edge_type=EdgeType.HOSTS.value if j % 2 == 0 else EdgeType.NEEDS.value,
                validity_interval="09:00:00-18:00:00",
                weight=1.0,
                metadata_json={"session_name": f"Synthetic Session {target_id}"},
            )
            edge_objects.append(edge)

    for edge in edge_objects:
        db_session.add(edge)
    await db_session.flush()

    engine = BlastRadiusEngine(db_session)
    request = BlastRadiusRequest(
        event_id=event_id,
        root_entity_id="node_0",
        root_entity_type="node",
        start_time="08:00:00",
        end_time="20:00:00",
        max_depth=5,
    )

    t_start = time.perf_counter()
    result = await engine.compute_blast_radius(request)
    elapsed = time.perf_counter() - t_start

    assert elapsed < 5.0, f"Blast radius took {elapsed:.4f}s (threshold: 5.0s)"
    assert result.total_impacted > 0


def test_kpi_first_plan_generation_latency():
    """Benchmark: First feasible plan generation <= 15s (TAD §5.1)."""
    resolver = VenueResolver()
    seed = load_golden_seed()
    
    start = time.perf_counter()
    res = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id="ven_main_aud")
    elapsed = time.perf_counter() - start

    assert elapsed < 15.0, f"Solver took {elapsed:.4f}s (threshold: 15.0s)"
    assert len(res.assignments) == 4


def test_kpi_audience_build_latency():
    """Benchmark: Target audience build <= 2s for golden cohorts (TAD §23)."""
    notif_svc = NotificationService()
    
    start = time.perf_counter()
    cohorts = notif_svc.get_impacted_cohorts()
    elapsed = time.perf_counter() - start

    assert elapsed < 2.0, f"Audience build took {elapsed:.4f}s (threshold: 2.0s)"
    assert len(cohorts) == 5


def test_kpi_simulation_branch_creation_latency():
    """Benchmark: Simulation branch creation <= 10s (TAD §23)."""
    mgr = BranchManager()
    seed = load_golden_seed()
    req = ProposalSimulateRequest(
        event_id="evt_kbc2026",
        disrupted_venue_id="ven_main_aud",
        disrupted_time_range="14:00:00-18:00:00",
    )
    
    start = time.perf_counter()
    proposal = mgr.create_simulation_branch(
        request=req,
        seed=seed,
        created_by="operator_001",
    )
    elapsed = time.perf_counter() - start

    assert elapsed < 10.0, f"Simulation branch creation took {elapsed:.4f}s (threshold: 10.0s)"
    assert proposal.proposal_id is not None
