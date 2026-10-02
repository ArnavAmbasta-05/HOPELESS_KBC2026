"""Graph Builder — constructs typed dependency edges for the Event Digital Twin (S2-T1).

Builds edges per TAD §9:
- hosts: Venue -> Session
- task_at: Venue -> Task
- mentions: Venue -> Notification
- has_registrants: Session -> Registrant Cohort
- assigned: Session -> Speaker / Volunteer (soft dependencies)
- needs: Session -> Resource
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.graph import EdgeType
from packages.domain.models import (
    DependencyEdge,
    Notification,
    Participant,
    Resource,
    Session as SessionModel,
    Task,
    Venue,
)
from packages.domain.seed import GoldenSeed, load_golden_seed


def build_edges_from_seed(seed: GoldenSeed) -> list[DependencyEdge]:
    """Generate all dependency edges from deterministic seed dataset."""
    edges: list[DependencyEdge] = []
    event_id = seed.event_id

    # 1. Venue -> Session (hosts)
    for s in seed.sessions:
        edges.append(
            DependencyEdge(
                edge_id=f"edge_hosts_{s.session_id}",
                event_id=event_id,
                source_id=s.venue_id,
                target_id=s.session_id,
                edge_type=EdgeType.HOSTS.value,
                validity_interval=f"{s.start_time.strftime('%H:%M:%S')}-{s.end_time.strftime('%H:%M:%S')}",
                weight=1.0,
                metadata_json={"session_name": s.name, "registrants": s.registrants},
            )
        )

        # 2. Session -> Cohort (has_registrants)
        cohort_id = f"cohort_{s.session_id}"
        edges.append(
            DependencyEdge(
                edge_id=f"edge_reg_{s.session_id}",
                event_id=event_id,
                source_id=s.session_id,
                target_id=cohort_id,
                edge_type=EdgeType.HAS_REGISTRANTS.value,
                validity_interval=None,
                weight=1.0,
                metadata_json={"count": s.registrants, "session_name": s.name},
            )
        )

    # 3. Venue -> Task (task_at)
    for t in seed.tasks:
        edges.append(
            DependencyEdge(
                edge_id=f"edge_task_{t.task_id}",
                event_id=event_id,
                source_id=t.venue_id,
                target_id=t.task_id,
                edge_type=EdgeType.TASK_AT.value,
                validity_interval=None,
                weight=1.0,
                metadata_json={"description": t.description, "team": t.team, "status": t.status.value},
            )
        )

    # 4. Venue -> Notification / Public Comm (mentions - 2 mentions: Instagram post + Printed schedule boards)
    edges.append(
        DependencyEdge(
            edge_id="edge_comm_insta",
            event_id=event_id,
            source_id="ven_main_aud",
            target_id="comm_insta_opening",
            edge_type=EdgeType.MENTIONS.value,
            validity_interval=None,
            weight=1.0,
            metadata_json={
                "content": "Instagram post 'Opening at Main Auditorium'",
                "channel": "instagram",
            },
        )
    )
    edges.append(
        DependencyEdge(
            edge_id="edge_comm_boards",
            event_id=event_id,
            source_id="ven_main_aud",
            target_id="comm_boards_gate1_gate3",
            edge_type=EdgeType.MENTIONS.value,
            validity_interval=None,
            weight=1.0,
            metadata_json={
                "content": "Printed schedule boards (Gate 1, Gate 3)",
                "channel": "printed_board",
            },
        )
    )

    # 5. Session -> Speaker (assigned - soft edges: 5 speakers total)
    for spk in seed.speakers:
        edges.append(
            DependencyEdge(
                edge_id=f"edge_spk_{spk.participant_id}",
                event_id=event_id,
                source_id=spk.session_id,
                target_id=spk.participant_id,
                edge_type=EdgeType.ASSIGNED.value,
                validity_interval=None,
                weight=0.5,  # soft edge
                metadata_json={
                    "name": spk.name,
                    "title": spk.title,
                    "arrival_building": spk.arrival_building,
                    "soft": True,
                },
            )
        )

    # 6. Session -> Volunteer Staffing (assigned - soft edges: 2 volunteer staffing edges in golden)
    # Dev (AV technician on Keynote) and Standby pool (Arjun)
    edges.append(
        DependencyEdge(
            edge_id="edge_vol_dev",
            event_id=event_id,
            source_id="ses_keynote_ai_fintech",
            target_id="vol_dev",
            edge_type=EdgeType.ASSIGNED.value,
            validity_interval=None,
            weight=0.5,
            metadata_json={
                "name": "Dev",
                "role": "AV Technician",
                "skill": "av",
                "status": "active",
                "soft": True,
            },
        )
    )
    edges.append(
        DependencyEdge(
            edge_id="edge_vol_standby",
            event_id=event_id,
            source_id="ses_keynote_ai_fintech",
            target_id="vol_arjun_standby",
            edge_type=EdgeType.ASSIGNED.value,
            validity_interval=None,
            weight=0.5,
            metadata_json={
                "name": "Arjun (Standby Pool)",
                "role": "AV Technician",
                "skill": "av",
                "status": "standby",
                "soft": True,
            },
        )
    )

    return edges


async def populate_graph_from_seed(session: AsyncSession) -> int:
    """Populate database dependency_edges table from golden seed data."""
    seed = load_golden_seed()
    edges = build_edges_from_seed(seed)
    for edge in edges:
        session.add(edge)
    await session.flush()
    return len(edges)
