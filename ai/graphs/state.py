"""EventRunState Schema for LangGraph Supervisor (S5-T2, TAD §12.1).

Defines the complete canonical execution state for AI orchestration runs:
EventRunState = {
    run_id, event_id, baseline_revision, trigger, facts[],
    impacted_nodes[], candidate_plans[], selected_plan, validation_results[],
    communication_plan[], approval_status, external_writes[], audit_refs[],
    ai_trace_id, model_metadata, timestamps, ai_summary, is_ai_generated
}
"""

from __future__ import annotations

from typing import Any, TypedDict


class EventRunState(TypedDict, total=False):
    run_id: str
    event_id: str
    baseline_revision: int
    trigger: dict[str, Any]
    facts: list[dict[str, Any]]
    impacted_nodes: list[str]
    candidate_plans: list[dict[str, Any]]
    selected_plan: dict[str, Any] | None
    validation_results: list[str]
    communication_plan: list[dict[str, Any]]
    approval_status: str  # "branch_only", "pending_approval", "approved", "rejected", "committed"
    approval_reason: str | None
    approved_by: str | None
    external_writes: list[dict[str, Any]]
    audit_refs: list[str]
    ai_trace_id: str
    model_metadata: dict[str, Any]
    timestamps: dict[str, str]
    ai_summary: str
    is_ai_generated: bool
    interrupt_step: str | None
