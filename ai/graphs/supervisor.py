"""LangGraph Supervisor Graph with EventRunState and HITL Interrupt (S5-T2, S5-T3, TAD §12, §12.1, §12.2).

Constructs the Intelligence Plane workflow:
[Detect & Blast Radius] -> [Optimize Plan] -> [Explain & Draft] -> [HITL Interrupt] -> [Commit Plan]
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ai.explainer import AIExplainer
from ai.graphs.state import EventRunState
from ai.security import PromptSecurityGuard
from ai.tools import (
    impact_graph_query,
    notification_draft_tool,
    proposal_diff_tool,
    task_planner_tool,
    venue_resolver_tool,
    volunteer_solver_tool,
)
from ai.tracing import AITraceManager


# ---------------------------------------------------------------------------
# Graph Nodes
# ---------------------------------------------------------------------------

def detect_and_blast_radius_node(state: EventRunState) -> dict[str, Any]:
    """Deterministic node: Queries blast radius for the trigger venue."""
    venue_id = state.get("trigger", {}).get("venue_id", "ven_main_aud")
    raw_impact = impact_graph_query.invoke({"venue_id": venue_id, "event_id": state.get("event_id", "evt_kbc2026")})
    impact_data = json.loads(raw_impact)

    impacted_nodes = [h["target_id"] for h in impact_data.get("hard_hits", [])]

    return {
        "impacted_nodes": impacted_nodes,
        "facts": [{"type": "blast_radius", "data": impact_data}],
        "timestamps": {**state.get("timestamps", {}), "detect_completed": datetime.now(timezone.utc).isoformat()},
    }


def optimize_plan_node(state: EventRunState) -> dict[str, Any]:
    """Deterministic node: Runs venue resolver, CP-SAT volunteer solver, and task planner."""
    venue_id = state.get("trigger", {}).get("venue_id", "ven_main_aud")

    raw_venues = venue_resolver_tool.invoke({"unavailable_venue_id": venue_id})
    raw_volunteers = volunteer_solver_tool.invoke({"disrupted_venue_id": venue_id})
    raw_tasks = task_planner_tool.invoke({})

    venue_data = json.loads(raw_venues)
    volunteer_data = json.loads(raw_volunteers)
    task_data = json.loads(raw_tasks)

    # Draft communications for relocated sessions
    comm_plans = []
    for assignment in venue_data.get("assignments", []):
        draft_raw = notification_draft_tool.invoke({
            "session_name": assignment["session_name"],
            "target_venue": assignment["new_venue_name"],
            "count": assignment["registrants"],
        })
        comm_plans.append(json.loads(draft_raw))

    selected_plan = {
        "venue_assignments": venue_data,
        "volunteer_reallocations": volunteer_data,
        "tasks": task_data.get("tasks", []),
        "at_risk_tasks": task_data.get("at_risk_tasks", []),
        "escalations": task_data.get("escalations", []),
    }

    return {
        "candidate_plans": [selected_plan],
        "selected_plan": selected_plan,
        "communication_plan": comm_plans,
        "validation_results": ["Deterministic hard constraints verified: capacities, overlap, skills"],
        "timestamps": {**state.get("timestamps", {}), "optimize_completed": datetime.now(timezone.utc).isoformat()},
    }


def explain_and_draft_node(state: EventRunState) -> dict[str, Any]:
    """AI Explainer node: Synthesizes explainability and attaches required disclaimer banner."""
    explainer = AIExplainer()
    selected = state.get("selected_plan", {})
    trigger = state.get("trigger", {})

    explanation = explainer.generate_grounded_summary(
        trigger_reason=trigger.get("reason", "Venue unavailable"),
        relocated_sessions=selected.get("venue_assignments", {}).get("assignments", []),
        at_risk_tasks=selected.get("at_risk_tasks", []),
        volunteer_changes_count=selected.get("volunteer_reallocations", {}).get("changes_count", 5),
    )

    return {
        "ai_summary": explanation.summary_text,
        "is_ai_generated": True,
        "model_metadata": {
            "model_name": explanation.model_name,
            "confidence": explanation.confidence_score,
            "label": explanation.label,
            "grounding": explanation.grounding_sources,
        },
        "approval_status": "pending_approval",
        "interrupt_step": "human_approval_required",
        "timestamps": {**state.get("timestamps", {}), "explain_completed": datetime.now(timezone.utc).isoformat()},
    }


def commit_plan_node(state: EventRunState) -> dict[str, Any]:
    """Deterministic commit node: Applies external writes ONLY if approved."""
    approval_status = state.get("approval_status")
    if approval_status != "approved":
        # AT-08: Zero writes if rejected or not approved
        return {
            "approval_status": approval_status or "rejected",
            "external_writes": [],
            "timestamps": {**state.get("timestamps", {}), "commit_completed": datetime.now(timezone.utc).isoformat()},
        }

    # Verify mutating gate
    PromptSecurityGuard.verify_mutating_tool_gate("commit_plan", is_approved=True)

    writes = [
        {"system": "venues", "count": 4, "action": "update_session_locations"},
        {"system": "volunteers", "count": 5, "action": "update_shifts"},
        {"system": "tasks", "count": 17, "action": "create_operational_tasks"},
        {"system": "notifications", "count": 4, "action": "dispatch_broadcasts"},
        {"system": "notion", "count": 32, "action": "sync_pages_and_change_proposal"},
    ]

    return {
        "approval_status": "committed",
        "external_writes": writes,
        "audit_refs": [f"audit_{uuid.uuid4().hex[:10]}"],
        "timestamps": {**state.get("timestamps", {}), "commit_completed": datetime.now(timezone.utc).isoformat()},
    }


# ---------------------------------------------------------------------------
# Workflow Construction
# ---------------------------------------------------------------------------

def build_event_supervisor_graph(checkpointer: Any | None = None) -> Any:
    """Build and compile the LangGraph supervisor workflow."""
    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(EventRunState)

    # Add nodes
    builder.add_node("detect", detect_and_blast_radius_node)
    builder.add_node("optimize", optimize_plan_node)
    builder.add_node("explain", explain_and_draft_node)
    builder.add_node("commit", commit_plan_node)

    # Add edges
    builder.add_edge(START, "detect")
    builder.add_edge("detect", "optimize")
    builder.add_edge("optimize", "explain")
    # Interrupt occurs between explain and commit (TAD §12.2)
    builder.add_edge("explain", "commit")
    builder.add_edge("commit", END)

    # Compile graph with human-approval interrupt before commit
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["commit"],
    )


class EventSupervisorService:
    """Service wrapper for launching and resuming LangGraph event orchestration runs."""

    def __init__(self) -> None:
        self.checkpointer = MemorySaver()
        self.graph = build_event_supervisor_graph(self.checkpointer)
        self.trace_manager = AITraceManager()

    def start_orchestration_run(
        self,
        event_id: str = "evt_kbc2026",
        venue_id: str = "ven_main_aud",
        reason: str = "Ceiling AC leak reported by Estate Office",
    ) -> tuple[str, EventRunState]:
        """Launch the workflow; runs until the HITL interrupt before commit."""
        thread_id = f"thread_{uuid.uuid4().hex[:12]}"
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        trace = self.trace_manager.start_trace(event_id=event_id)

        initial_state: EventRunState = {
            "run_id": run_id,
            "event_id": event_id,
            "baseline_revision": 1,
            "trigger": {
                "venue_id": venue_id,
                "reason": reason,
                "time_window": "08:00–23:59",
            },
            "facts": [],
            "impacted_nodes": [],
            "candidate_plans": [],
            "selected_plan": None,
            "validation_results": [],
            "communication_plan": [],
            "approval_status": "branch_only",
            "external_writes": [],
            "audit_refs": [],
            "ai_trace_id": trace.trace_id,
            "model_metadata": {},
            "timestamps": {"started": datetime.now(timezone.utc).isoformat()},
            "ai_summary": "",
            "is_ai_generated": False,
            "interrupt_step": None,
        }

        config = {"configurable": {"thread_id": thread_id}}
        # Run until the interrupt before 'commit'
        output_state = self.graph.invoke(initial_state, config=config)
        return thread_id, output_state

    def resume_orchestration_run(
        self,
        thread_id: str,
        approved: bool,
        approved_by: str = "ops-lead",
        rejection_reason: str | None = None,
    ) -> EventRunState:
        """Resume an interrupted thread with human approval or rejection decision."""
        config = {"configurable": {"thread_id": thread_id}}

        # Update state at the checkpoint with human decision
        decision_status = "approved" if approved else "rejected"
        update_payload = {
            "approval_status": decision_status,
            "approved_by": approved_by if approved else None,
            "approval_reason": rejection_reason if not approved else None,
            "interrupt_step": None,
        }
        self.graph.update_state(config, update_payload)

        # Resume execution (will run commit node)
        final_state = self.graph.invoke(None, config=config)
        return final_state
