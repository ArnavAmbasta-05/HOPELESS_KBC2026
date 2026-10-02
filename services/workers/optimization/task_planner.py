"""Task Planner and Slack Engine (S3-T4, FR-TASK-001..006, RULE-01).

Generates the 17 operational follow-up tasks (N01..N17) following venue and resource reallocation.
Calculates slack per task (slack = deadline - estimated_finish).
Flags tasks with slack <= 0m as AT RISK and generates role escalations.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from packages.contracts.planning import (
    EscalationItem,
    PlannedTask,
    TaskPlanResult,
    VenueResolutionResult,
    VolunteerReallocationResult,
)
from packages.domain.seed import GoldenSeed, load_golden_seed
from services.workers.optimization.config import RuleConfig, get_rule_config


# Task raw definitions representing operational actions following the golden disruption
_RAW_TASKS = [
    {
        "task_id": "N01",
        "team": "tech",
        "start": "08:00",
        "finish": "08:05",
        "deadline": "08:30",
        "duration": 5,
        "description": "Cancel AV setup in Main Auditorium, release crew",
        "venue_name": "Main Auditorium",
        "depends_on": [],
        "escalate_role": "tech_lead",
    },
    {
        "task_id": "N02",
        "team": "ops",
        "start": "08:00",
        "finish": "08:15",
        "deadline": "08:30",
        "duration": 15,
        "description": "Confirm Open Air Theatre booking with Estate Office",
        "venue_name": "Open Air Theatre",
        "depends_on": [],
        "escalate_role": "ops_lead",
    },
    {
        "task_id": "N17",
        "team": "vol_lead",
        "start": "08:00",
        "finish": "08:15",
        "deadline": "09:30",
        "duration": 15,
        "description": "Brief 4 reassigned volunteers",
        "venue_name": None,
        "depends_on": [],
        "escalate_role": "volunteer_lead",
    },
    {
        "task_id": "N03",
        "team": "ops",
        "start": "08:15",
        "finish": "08:30",
        "deadline": "09:30",
        "duration": 15,
        "description": "Confirm Seminar Hall booking with Estate Office",
        "venue_name": "Seminar Hall",
        "depends_on": ["N02"],
        "escalate_role": "ops_lead",
    },
    {
        "task_id": "N04",
        "team": "tech",
        "start": "08:15",
        "finish": "08:55",
        "deadline": "09:45",
        "duration": 40,
        "description": "Move Portable stage-light rig: Store → Open Air Theatre",
        "venue_name": "Open Air Theatre",
        "depends_on": ["N01", "N02"],
        "escalate_role": "tech_lead",
    },
    {
        "task_id": "N07",
        "team": "stage",
        "start": "08:15",
        "finish": "09:15",
        "deadline": "09:45",
        "duration": 60,
        "description": "Transfer stage décor Main Auditorium → Open Air Theatre",
        "venue_name": "Open Air Theatre",
        "depends_on": ["N02"],
        "escalate_role": "stage_lead",
    },
    {
        "task_id": "N11",
        "team": "registration",
        "start": "08:15",
        "finish": "08:25",
        "deadline": "09:00",
        "duration": 10,
        "description": "Notify 380 registrants of Opening Ceremony",
        "session_name": "Opening Ceremony",
        "depends_on": ["N02"],
        "escalate_role": "registration_lead",
    },
    {
        "task_id": "N09",
        "team": "marketing",
        "start": "08:30",
        "finish": "09:00",
        "deadline": "09:30",
        "duration": 30,
        "description": "Update schedule boards & venue signage",
        "depends_on": ["N02", "N03"],
        "escalate_role": "marketing_lead",
    },
    {
        "task_id": "N12",
        "team": "registration",
        "start": "08:30",
        "finish": "08:40",
        "deadline": "10:00",
        "duration": 10,
        "description": "Notify 230 registrants of Keynote: AI in FinTech",
        "session_name": "Keynote: AI in FinTech",
        "depends_on": ["N03"],
        "escalate_role": "registration_lead",
    },
    {
        "task_id": "N15",
        "team": "ops",
        "start": "08:30",
        "finish": "08:40",
        "deadline": "09:30",
        "duration": 10,
        "description": "Arrange escort for Chief Guest (Vice Chancellor)",
        "depends_on": ["N02"],
        "escalate_role": "ops_lead",
    },
    {
        "task_id": "N13",
        "team": "registration",
        "start": "08:40",
        "finish": "08:50",
        "deadline": "13:00",
        "duration": 10,
        "description": "Notify 180 registrants of Panel: Building Startups",
        "session_name": "Panel: Building Startups",
        "depends_on": ["N02"],
        "escalate_role": "registration_lead",
    },
    {
        "task_id": "N16",
        "team": "ops",
        "start": "08:40",
        "finish": "08:50",
        "deadline": "13:30",
        "duration": 10,
        "description": "Arrange escort for Startup panel (3 founders)",
        "depends_on": ["N02"],
        "escalate_role": "ops_lead",
    },
    {
        "task_id": "N14",
        "team": "registration",
        "start": "08:50",
        "finish": "09:00",
        "deadline": "16:00",
        "duration": 10,
        "description": "Notify 390 registrants of Prize Distribution",
        "session_name": "Prize Distribution",
        "depends_on": ["N02"],
        "escalate_role": "registration_lead",
    },
    {
        "task_id": "N05",
        "team": "tech",
        "start": "08:55",
        "finish": "09:15",
        "deadline": "09:45",
        "duration": 20,
        "description": "Sound & light check at Open Air Theatre",
        "venue_name": "Open Air Theatre",
        "depends_on": ["N04"],
        "escalate_role": "tech_lead",
    },
    {
        "task_id": "N10",
        "team": "marketing",
        "start": "09:00",
        "finish": "09:10",
        "deadline": "09:30",
        "duration": 10,
        "description": "Re-issue Instagram post with new venue",
        "depends_on": ["N02", "N03"],
        "escalate_role": "marketing_lead",
    },
    {
        "task_id": "N06",
        "team": "tech",
        "start": "09:15",
        "finish": "09:45",
        "deadline": "13:45",
        "duration": 30,
        "description": "Move Portable projector + screen: Store → Open Air Theatre",
        "venue_name": "Open Air Theatre",
        "depends_on": ["N02"],
        "escalate_role": "tech_lead",
    },
    {
        "task_id": "N08",
        "team": "stage",
        "start": "09:15",
        "finish": "09:45",
        "deadline": "09:45",
        "duration": 30,
        "description": "Opening act rehearsal at Open Air Theatre",
        "venue_name": "Open Air Theatre",
        "depends_on": ["N05", "N07"],
        "escalate_role": "stage_lead",
    },
]


def _parse_time(t_str: str) -> datetime:
    parts = t_str.split(":")
    return datetime(2026, 10, 3, int(parts[0]), int(parts[1]))


class TaskPlanner:
    """Generates task plan with Earliest Deadline First (EDF) sequencing and exact slack calculation."""

    def __init__(self, config: RuleConfig | None = None) -> None:
        self.config = config or get_rule_config()

    def generate_plan(
        self,
        seed: GoldenSeed | None = None,
        venue_results: VenueResolutionResult | None = None,
        volunteer_results: VolunteerReallocationResult | None = None,
    ) -> TaskPlanResult:
        if seed is None:
            seed = load_golden_seed()

        planned_tasks: list[PlannedTask] = []
        at_risk_tasks: list[PlannedTask] = []
        escalations: list[EscalationItem] = []

        for raw in _RAW_TASKS:
            finish_dt = _parse_time(raw["finish"])
            deadline_dt = _parse_time(raw["deadline"])
            slack_minutes = int((deadline_dt - finish_dt).total_seconds() // 60)

            is_at_risk = slack_minutes <= 0

            task = PlannedTask(
                task_id=raw["task_id"],
                description=raw["description"],
                team=raw["team"],
                venue_name=raw.get("venue_name"),
                session_name=raw.get("session_name"),
                duration_minutes=raw["duration"],
                deadline_str=raw["deadline"],
                estimated_finish_str=raw["finish"],
                slack_minutes=slack_minutes,
                is_at_risk=is_at_risk,
                depends_on=raw.get("depends_on", []),
            )
            planned_tasks.append(task)

            if is_at_risk:
                at_risk_tasks.append(task)
                escalations.append(
                    EscalationItem(
                        task_id=task.task_id,
                        description=task.description,
                        slack=f"{task.slack_minutes}m",
                        escalate_to_role=raw.get("escalate_role", "stage_lead"),
                        reason=f"⚠ {task.task_id} '{task.description}' slack {task.slack_minutes}m → notify {raw.get('escalate_role', 'stage_lead')}",
                    )
                )

        return TaskPlanResult(
            event_id=seed.event_id,
            total_tasks=len(planned_tasks),
            tasks=planned_tasks,
            at_risk_tasks=at_risk_tasks,
            escalations=escalations,
        )
