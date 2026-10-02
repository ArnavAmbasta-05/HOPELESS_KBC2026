"""Pydantic contracts for Rules, Optimization, and Task Planning (Sprint 3, TAD §10, §11)."""

from __future__ import annotations

from datetime import datetime, time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Solver & Optimization Status
# ---------------------------------------------------------------------------

class SolverStatus(StrEnum):
    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    TIMEOUT = "timeout"


# ---------------------------------------------------------------------------
# Venue Resolution Schemas (S3-T2)
# ---------------------------------------------------------------------------

class VenueRejectionReason(BaseModel):
    venue_id: str
    venue_name: str
    capacity: int
    registrants: int
    reason: str


class SessionVenueAssignment(BaseModel):
    session_id: str
    session_name: str
    original_venue_id: str
    original_venue_name: str
    new_venue_id: str
    new_venue_name: str
    new_venue_building: str
    registrants: int
    capacity: int
    required_equipment: list[str] = Field(default_factory=list)
    rejections: list[VenueRejectionReason] = Field(default_factory=list)


class SpeakerReevalItem(BaseModel):
    speaker_id: str
    name: str
    title: str
    session_id: str
    session_name: str
    arrival_building: str
    venue_building: str
    escort_needed: bool
    status_symbol: str = Field(..., description="✓ or ✗")
    note: str


class VenueResolutionResult(BaseModel):
    event_id: str
    status: SolverStatus
    assignments: list[SessionVenueAssignment]
    speaker_reevaluations: list[SpeakerReevalItem] = Field(default_factory=list)
    unresolved_sessions: list[str] = Field(default_factory=list)
    total_rejections_logged: int


# ---------------------------------------------------------------------------
# Volunteer Reallocation Schemas (S3-T3)
# ---------------------------------------------------------------------------

class VolunteerAssignmentChange(BaseModel):
    action: str = Field(..., description="removed, assigned, standby_activated, untouched")
    staff_id: str
    name: str
    role: str
    skill: str
    session_id: str | None = None
    session_name: str | None = None
    venue_id: str | None = None
    venue_name: str | None = None
    is_standby_activated: bool = False
    note: str = ""


class VolunteerReallocationResult(BaseModel):
    event_id: str
    status: SolverStatus
    total_volunteers: int
    untouched_count: int
    changes_count: int
    changes: list[VolunteerAssignmentChange]
    standby_activations: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Task Planning & Slack Schemas (S3-T4)
# ---------------------------------------------------------------------------

class PlannedTask(BaseModel):
    task_id: str = Field(..., description="Canonical task identifier (e.g. N01, N08)")
    description: str
    team: str
    venue_name: str | None = None
    session_name: str | None = None
    duration_minutes: int
    deadline_str: str
    estimated_finish_str: str
    slack_minutes: int = Field(..., description="Slack = deadline - finish")
    is_at_risk: bool = Field(default=False, description="True if slack == 0m or negative")
    depends_on: list[str] = Field(default_factory=list)


class EscalationItem(BaseModel):
    task_id: str
    description: str
    slack: str
    escalate_to_role: str
    reason: str


class TaskPlanResult(BaseModel):
    event_id: str
    total_tasks: int
    tasks: list[PlannedTask]
    at_risk_tasks: list[PlannedTask]
    escalations: list[EscalationItem]


# ---------------------------------------------------------------------------
# Infeasible State & Manual Queue Schemas (S3-T5, AT-09)
# ---------------------------------------------------------------------------

class ManualActionOption(BaseModel):
    rank: int
    title: str
    description: str
    tradeoffs: str


class InfeasibleResolutionResult(BaseModel):
    event_id: str
    status: SolverStatus = SolverStatus.INFEASIBLE
    disrupted_entity_id: str
    unmet_constraints: list[str]
    rejected_reasons: list[str]
    manual_action_options: list[ManualActionOption]
