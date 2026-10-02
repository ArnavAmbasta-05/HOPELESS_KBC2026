"""Pydantic contracts and schemas for Dependency Graph and Blast Radius (TAD §9, §27)."""

from __future__ import annotations

from datetime import datetime, time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EdgeType(StrEnum):
    HOSTS = "hosts"
    TASK_AT = "task_at"
    MENTIONS = "mentions"
    HAS_REGISTRANTS = "has_registrants"
    ASSIGNED = "assigned"
    NEEDS = "needs"
    SERVED_BY = "served_by"
    OCCUPIES = "occupies"
    EXPOSED_TO = "exposed_to"


class ImpactSeverity(StrEnum):
    HARD_HIT = "hard_hit"
    SOFT_DEFERRED = "soft_deferred"
    UNAFFECTED = "unaffected"


class NodeImpact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    node_id: str = Field(..., description="Canonical ID of the impacted entity")
    entity_type: str = Field(..., description="Entity type (session, task, comm, cohort, speaker, volunteer, etc.)")
    name: str = Field(..., description="Display name or description of entity")
    severity: ImpactSeverity = Field(..., description="Classification of impact (hard_hit or soft_deferred)")
    edge_type: str = Field(..., description="Edge type connecting to this node")
    path: list[str] = Field(default_factory=list, description="Sequence of node/edge steps from root disruption")
    details: dict[str, Any] = Field(default_factory=dict, description="Metadata such as registrants, building, or timing")


class BlastRadiusRequest(BaseModel):
    event_id: str = Field(..., description="Event scope ID")
    root_entity_id: str = Field(..., description="Disrupted entity ID (e.g. ven_main_aud)")
    root_entity_type: str = Field(default="venue", description="Type of disrupted entity")
    start_time: str = Field(default="08:00:00", description="Start of disruption window (HH:MM:SS)")
    end_time: str = Field(default="23:59:59", description="End of disruption window (HH:MM:SS)")
    max_depth: int = Field(default=5, ge=1, le=10, description="Maximum traversal depth (DoS protection)")


class BlastRadiusResult(BaseModel):
    event_id: str
    root_entity_id: str
    hard_hits_count: int
    soft_deferred_count: int
    hard_hits: list[NodeImpact]
    soft_deferred: list[NodeImpact]
    total_impacted: int
    computation_ms: float
    computed_at: datetime
