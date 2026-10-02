"""Crowd Safety & Zone Flow Data Contracts (Sprint 8, CRD-001..007, AT-04/05, TAD §16)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CrowdZone(BaseModel):
    zone_id: str
    name: str
    building: str
    max_safe_capacity: int
    warning_threshold_ratio: float = 0.80  # 80%
    surge_threshold_ratio: float = 0.95    # 95%
    connected_gates: list[str] = Field(default_factory=list)
    current_anonymous_count: int = 0
    occupancy_ratio: float = 0.0


class Gate(BaseModel):
    gate_id: str
    name: str
    zone_id: str
    open_window: str = "07:00–23:00"
    max_flow_rate_per_min: int = 60
    current_flow_rate_per_min: int = 0
    is_open: bool = True


class CrowdAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"crd_alt_{uuid.uuid4().hex[:8]}")
    zone_id: str
    zone_name: str
    severity: AlertSeverity
    current_count: int
    max_capacity: int
    load_ratio: float
    message: str
    affected_sessions: list[str] = Field(default_factory=list)
    recommended_action: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RerouteProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: f"crd_prop_{uuid.uuid4().hex[:8]}")
    alert_id: str
    congested_zone_id: str
    congested_gate_id: str
    alternate_gate_id: str
    alternate_route_name: str
    target_cohort_id: str
    guidance_message: str
    requires_operator_confirm: bool = True
    status: str = "PENDING_OPERATOR_APPROVAL"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CrowdAdvisory(BaseModel):
    advisory_id: str = Field(default_factory=lambda: f"adv_{uuid.uuid4().hex[:8]}")
    title: str
    message: str
    target_area: str
    severity: str = "ADVISORY"
    issued_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
