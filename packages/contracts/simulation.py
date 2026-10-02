"""Pydantic contracts for Simulation, Change Proposals, and Branches (Sprint 4, TAD §10, §20.2)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from packages.contracts.planning import (
    EscalationItem,
    PlannedTask,
    SolverStatus,
    SpeakerReevalItem,
    VenueResolutionResult,
    VolunteerReallocationResult,
)


class BranchStatus(StrEnum):
    BRANCH_ONLY = "branch_only"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMMITTED = "committed"


class ObjectDiffAction(StrEnum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNTOUCHED = "untouched"


class ObjectDiffItem(BaseModel):
    entity_type: str = Field(..., description="venue, session, volunteer, task, comm, speaker")
    entity_id: str
    action: ObjectDiffAction
    summary: str
    old_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None


class SimulationDiff(BaseModel):
    total_changes: int
    added_count: int
    removed_count: int
    modified_count: int
    items: list[ObjectDiffItem]


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskItem(BaseModel):
    risk_id: str
    severity: RiskLevel
    title: str
    description: str
    affected_entity_id: str
    mitigation: str


class RiskPlan(BaseModel):
    overall_risk: RiskLevel
    at_risk_tasks_count: int
    at_risk_tasks: list[PlannedTask]
    unresolved_dependencies: list[str] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)


class CommunicationAction(BaseModel):
    channel: str
    target_audience: str
    count: int
    message: str
    status: str = "queued"


class ChangeProposalTrigger(BaseModel):
    trigger_type: str = Field(..., description="venue_outage, weather, transport, crowd, attendance")
    venue_id: str | None = None
    venue_name: str | None = None
    time_window: str = Field(..., description="e.g. 08:00–23:59")
    reason: str
    reported_by: str
    reported_at: str


class ChangeProposal(BaseModel):
    proposal_id: str
    event_id: str
    baseline_revision: int
    version: int = 1
    status: BranchStatus = BranchStatus.BRANCH_ONLY
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by: str
    trigger: ChangeProposalTrigger
    blast_radius_summary: dict[str, Any]
    venue_resolution: VenueResolutionResult
    volunteer_reallocation: VolunteerReallocationResult
    task_plan: list[PlannedTask]
    escalations: list[EscalationItem]
    risk_plan: RiskPlan
    communication_plan: list[CommunicationAction]
    diff: SimulationDiff
    ai_summary: str = Field(
        ...,
        description="AI-generated explanatory narrative (clearly labeled, unverified facts)",
    )
    is_ai_generated_summary: bool = True
    approved_by: str | None = None
    approved_at: str | None = None
    rejection_reason: str | None = None
    commit_result: dict[str, Any] | None = None


class ProposalSimulateRequest(BaseModel):
    event_id: str = "evt_kbc2026"
    unavailable_venue_id: str = "ven_main_aud"
    reason: str = "Ceiling AC leak reported by Estate Office"
    time_window: str = "08:00–23:59"
    reported_by: str = "ops-lead (via Notion)"


class ProposalDecisionRequest(BaseModel):
    reason: str | None = None
    notes: str | None = None
