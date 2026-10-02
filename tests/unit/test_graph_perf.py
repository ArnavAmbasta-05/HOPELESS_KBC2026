"""Performance benchmark test for Dependency Engine blast radius (S2-T5, NFR-PERF-001).

Builds a synthetic 5,000-edge graph and asserts blast-radius traversal completes
within ≤ 5.0 seconds.
"""

from __future__ import annotations

import time as _pytime
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.graph import BlastRadiusRequest, EdgeType
from packages.domain.graph.engine import BlastRadiusEngine
from packages.domain.models import DependencyEdge


@pytest.mark.asyncio
async def test_5000_edge_blast_radius_performance(db_session: AsyncSession) -> None:
    event_id = "evt_perf_benchmark"
    num_nodes = 500
    edges_per_node = 10
    total_edges = num_nodes * edges_per_node  # 5,000 edges

    # Create synthetic connected DAG
    edge_objects: list[DependencyEdge] = []
    for i in range(num_nodes):
        source_id = f"node_{i}"
        for j in range(1, edges_per_node + 1):
            target_id = f"node_{(i * edges_per_node + j) % (num_nodes * 2)}"
            edge = DependencyEdge(
                edge_id=f"edge_perf_{i}_{j}",
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

    assert len(edge_objects) == 5000

    engine = BlastRadiusEngine(db_session)
    request = BlastRadiusRequest(
        event_id=event_id,
        root_entity_id="node_0",
        root_entity_type="node",
        start_time="08:00:00",
        end_time="20:00:00",
        max_depth=5,
    )

    t_start = _pytime.perf_counter()
    result = await engine.compute_blast_radius(request)
    t_elapsed = _pytime.perf_counter() - t_start

    # NFR-PERF-001: Blast radius computation on 5,000 edges must complete in ≤ 5.0 seconds
    assert t_elapsed <= 5.0, f"Benchmark took {t_elapsed:.3f}s (threshold: 5.0s)"
    assert result.computation_ms < 5000.0
    assert result.total_impacted > 0
