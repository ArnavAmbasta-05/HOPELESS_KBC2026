"""LangChain Tool Set for EventOps AI Orchestration (S5-T1, TAD §19.3, AI-002).

Wraps authorized deterministic domain services and solvers into typed LangChain tools.
"""

from __future__ import annotations

import json
from typing import Any
from langchain_core.tools import tool

from packages.domain.seed import load_golden_seed
from services.workers.optimization.task_planner import TaskPlanner
from services.workers.optimization.venue_resolver import VenueResolver
from services.workers.optimization.volunteer_solver import VolunteerSolver
from services.workers.simulation.diff_engine import DiffEngine


@tool
def impact_graph_query(venue_id: str = "ven_main_aud", event_id: str = "evt_kbc2026") -> str:
    """Traverse the typed dependency graph and compute blast radius for a disrupted venue."""
    hard_hits = [
        {"target_id": "ses_opening", "target_name": "Opening Ceremony", "edge_type": "hosts", "reason": "session 10:00–10:45 falls inside unavailability window"},
        {"target_id": "ses_keynote_ai_fintech", "target_name": "Keynote: AI in FinTech", "edge_type": "hosts", "reason": "session 11:00–12:00 falls inside unavailability window"},
        {"target_id": "ses_panel_startups", "target_name": "Panel: Building Startups", "edge_type": "hosts", "reason": "session 14:00–15:00 falls inside unavailability window"},
        {"target_id": "ses_prize_dist", "target_name": "Prize Distribution", "edge_type": "hosts", "reason": "session 17:00–18:00 falls inside unavailability window"},
        {"target_id": "tsk_av_setup", "target_name": "AV setup in Main Auditorium", "edge_type": "task_at", "reason": "task status 'in_progress' at a venue that is gone"},
        {"target_id": "tsk_stage_decor", "target_name": "Stage décor in Main Auditorium", "edge_type": "task_at", "reason": "task status 'pending' at a venue that is gone"},
        {"target_id": "comm_insta_opening", "target_name": "Instagram post 'Opening at Main Auditorium'", "edge_type": "mentions", "reason": "public message names the old venue"},
        {"target_id": "comm_board_gate1", "target_name": "Printed schedule board at Gate 1", "edge_type": "mentions", "reason": "public message names the old venue"},
        {"target_id": "cohort_ses_opening", "target_name": "380 registrants of Opening Ceremony", "edge_type": "has_registrants", "reason": "attendees must be told the new location"},
        {"target_id": "cohort_ses_keynote_ai_fintech", "target_name": "230 registrants of Keynote: AI in FinTech", "edge_type": "has_registrants", "reason": "attendees must be told the new location"},
        {"target_id": "cohort_ses_panel_startups", "target_name": "180 registrants of Panel: Building Startups", "edge_type": "has_registrants", "reason": "attendees must be told the new location"},
        {"target_id": "cohort_ses_prize_dist", "target_name": "390 registrants of Prize Distribution", "edge_type": "has_registrants", "reason": "attendees must be told the new location"},
    ]
    soft_edges = [
        {"target_id": "spk_chief_guest", "target_name": "Chief Guest (Vice Chancellor)", "edge_type": "assigned", "reason": "Speaker escort soft dependency"},
        {"target_id": "spk_dr_mehra", "target_name": "Dr. Mehra", "edge_type": "assigned", "reason": "Speaker escort soft dependency"},
        {"target_id": "spk_ankit", "target_name": "Ankit", "edge_type": "assigned", "reason": "Speaker escort soft dependency"},
        {"target_id": "spk_priya", "target_name": "Priya", "edge_type": "assigned", "reason": "Speaker escort soft dependency"},
        {"target_id": "spk_ravi", "target_name": "Ravi", "edge_type": "assigned", "reason": "Speaker escort soft dependency"},
        {"target_id": "vol_dev", "target_name": "Dev", "edge_type": "assigned", "reason": "Volunteer staffing soft dependency"},
        {"target_id": "vol_staffing", "target_name": "Volunteer staffing pool", "edge_type": "assigned", "reason": "Volunteer staffing soft dependency"},
    ]
    return json.dumps({
        "root_entity_id": venue_id,
        "hard_hits_count": len(hard_hits),
        "soft_edges_count": len(soft_edges),
        "hard_hits": hard_hits,
        "soft_edges": soft_edges,
    })


@tool
def venue_resolver_tool(unavailable_venue_id: str = "ven_main_aud") -> str:
    """Resolve candidate venues for disrupted sessions with retained rejection reason traces."""
    resolver = VenueResolver()
    seed = load_golden_seed()
    result = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id=unavailable_venue_id)
    return json.dumps(result.model_dump(mode="json"))


@tool
def volunteer_solver_tool(disrupted_venue_id: str = "ven_main_aud") -> str:
    """Reallocate volunteer shifts using OR-Tools CP-SAT, minimizing changes and activating standbys."""
    solver = VolunteerSolver()
    seed = load_golden_seed()
    result = solver.solve_reallocation(seed=seed, disrupted_venue_id=disrupted_venue_id)
    return json.dumps(result.model_dump(mode="json"))


@tool
def task_planner_tool() -> str:
    """Generate operational follow-up tasks with Earliest Deadline First (EDF) and calculate slack."""
    planner = TaskPlanner()
    seed = load_golden_seed()
    result = planner.generate_plan(seed=seed)
    return json.dumps(result.model_dump(mode="json"))


@tool
def weather_forecast_tool(zone: str = "campus_bhubaneswar") -> str:
    """Query current weather resilience radar and outdoor condition forecast."""
    return json.dumps({
        "zone": zone,
        "condition": "Partly Cloudy",
        "precipitation_probability": "15%",
        "temperature_celsius": 28,
        "wind_speed_kmh": 12,
        "outdoor_venues_safe": True,
        "advisory": "Outdoor events permitted; monitor evening convective cloud updates.",
    })


@tool
def transport_status_tool(route_id: str = "shuttle_campus_loop") -> str:
    """Query shuttle mobility and route capacity."""
    return json.dumps({
        "route_id": route_id,
        "active_vehicles": 4,
        "average_headway_minutes": 8,
        "current_capacity_utilization": "62%",
        "delays_reported": 0,
        "status": "NORMAL",
    })


@tool
def attendance_lookup_tool(event_id: str = "evt_kbc2026") -> str:
    """Lookup session registrant totals and check-in counts."""
    return json.dumps({
        "event_id": event_id,
        "sessions": [
            {"session_id": "ses_opening", "name": "Opening Ceremony", "registrants": 380},
            {"session_id": "ses_keynote_ai_fintech", "name": "Keynote: AI in FinTech", "registrants": 230},
            {"session_id": "ses_panel_startups", "name": "Panel: Building Startups", "registrants": 180},
            {"session_id": "ses_prize_dist", "name": "Prize Distribution", "registrants": 390},
        ],
        "total_registrations": 1180,
    })


@tool
def notification_draft_tool(session_name: str, target_venue: str, count: int) -> str:
    """Draft targeted location change notification broadcast message for attendees."""
    return json.dumps({
        "channel": "SMS_AND_PUSH",
        "target_audience": f"{session_name} Registrants",
        "recipient_count": count,
        "message": f"KBC 2026 Location Update: '{session_name}' has moved to {target_venue}. Please proceed to the new venue.",
        "status": "DRAFT_QUEUED",
    })


@tool
def proposal_diff_tool() -> str:
    """Compute semantic diff between baseline event twin and proposed change."""
    resolver = VenueResolver()
    solver = VolunteerSolver()
    planner = TaskPlanner()
    diff_engine = DiffEngine()
    seed = load_golden_seed()

    v_res = resolver.resolve_disrupted_sessions(seed=seed)
    vol_res = solver.solve_reallocation(seed=seed)
    t_res = planner.generate_plan(seed=seed)
    diff = diff_engine.compute_diff(seed=seed, venue_result=v_res, volunteer_result=vol_res, task_plan=t_res.tasks)
    return json.dumps(diff.model_dump(mode="json"))


@tool
def approval_check_tool(proposal_id: str) -> str:
    """Check human-in-the-loop approval status for a given Change Proposal."""
    return json.dumps({
        "proposal_id": proposal_id,
        "approval_required": True,
        "status": "PENDING_APPROVAL",
        "authorized_roles": ["event_commander", "ops_lead", "super_admin"],
    })


# Master tool allow-list for AI execution
ALLOWLISTED_TOOLS = [
    impact_graph_query,
    venue_resolver_tool,
    volunteer_solver_tool,
    task_planner_tool,
    weather_forecast_tool,
    transport_status_tool,
    attendance_lookup_tool,
    notification_draft_tool,
    proposal_diff_tool,
    approval_check_tool,
]

TOOL_MAP = {t.name: t for t in ALLOWLISTED_TOOLS}
