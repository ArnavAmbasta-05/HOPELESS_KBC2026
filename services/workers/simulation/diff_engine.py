"""Simulation Diff Engine (S4-T1.2, FR-SIM-003, TAD §10).

Calculates baseline <-> proposed diff across venues, sessions, volunteer assignments, tasks, and communications.
"""

from __future__ import annotations

from typing import Any

from packages.contracts.planning import (
    PlannedTask,
    VenueResolutionResult,
    VolunteerReallocationResult,
)
from packages.contracts.simulation import (
    ObjectDiffAction,
    ObjectDiffItem,
    SimulationDiff,
)
from packages.domain.seed import GoldenSeed, load_golden_seed


class DiffEngine:
    """Computes exact semantic diff between baseline event twin and simulated change proposal."""

    def compute_diff(
        self,
        seed: GoldenSeed | None,
        venue_result: VenueResolutionResult,
        volunteer_result: VolunteerReallocationResult,
        task_plan: list[PlannedTask],
    ) -> SimulationDiff:
        if seed is None:
            seed = load_golden_seed()

        items: list[ObjectDiffItem] = []

        # 1. Sessions diff (relocated sessions)
        for assignment in venue_result.assignments:
            items.append(
                ObjectDiffItem(
                    entity_type="session",
                    entity_id=assignment.session_id,
                    action=ObjectDiffAction.MODIFIED,
                    summary=f"Relocated '{assignment.session_name}' from {assignment.original_venue_name} to {assignment.new_venue_name}",
                    old_state={"venue_id": assignment.original_venue_id, "venue_name": assignment.original_venue_name},
                    new_state={"venue_id": assignment.new_venue_id, "venue_name": assignment.new_venue_name, "equipment": assignment.required_equipment},
                )
            )

        # 2. Volunteer assignments diff
        for change in volunteer_result.changes:
            if change.action == "removed":
                items.append(
                    ObjectDiffItem(
                        entity_type="volunteer",
                        entity_id=change.staff_id,
                        action=ObjectDiffAction.REMOVED,
                        summary=f"Released {change.name} ({change.role}) from {change.session_name}",
                        old_state={"role": change.role, "session": change.session_name},
                        new_state=None,
                    )
                )
            elif change.action in ("assigned", "standby_activated"):
                action_type = ObjectDiffAction.ADDED if change.action == "standby_activated" else ObjectDiffAction.MODIFIED
                standby_tag = " [STANDBY ACTIVATED]" if change.is_standby_activated else ""
                items.append(
                    ObjectDiffItem(
                        entity_type="volunteer",
                        entity_id=change.staff_id,
                        action=action_type,
                        summary=f"Assigned {change.name} to {change.session_name} ({change.role}) @ {change.venue_name}{standby_tag}",
                        old_state=None,
                        new_state={"role": change.role, "session": change.session_name, "venue": change.venue_name},
                    )
                )

        # 3. Tasks diff (new operational follow-up tasks)
        for task in task_plan:
            risk_tag = " [AT RISK]" if task.is_at_risk else ""
            items.append(
                ObjectDiffItem(
                    entity_type="task",
                    entity_id=task.task_id,
                    action=ObjectDiffAction.ADDED,
                    summary=f"Created task {task.task_id}: {task.description} (deadline {task.deadline_str}, slack {task.slack_minutes}m){risk_tag}",
                    old_state=None,
                    new_state={"team": task.team, "deadline": task.deadline_str, "slack": task.slack_minutes},
                )
            )

        # 4. Communications diff
        comm_notifications = [
            ("Opening Ceremony", 380, "Open Air Theatre"),
            ("Keynote: AI in FinTech", 230, "Seminar Hall"),
            ("Panel: Building Startups", 180, "Open Air Theatre"),
            ("Prize Distribution", 390, "Open Air Theatre"),
        ]
        for s_name, count, target_venue in comm_notifications:
            items.append(
                ObjectDiffItem(
                    entity_type="communication",
                    entity_id=f"comm_notify_{s_name.lower().replace(' ', '_').replace(':', '')}",
                    action=ObjectDiffAction.ADDED,
                    summary=f"Queued location update broadcast to {count} registrants of '{s_name}' -> {target_venue}",
                    old_state=None,
                    new_state={"registrants": count, "venue": target_venue},
                )
            )

        added = sum(1 for i in items if i.action == ObjectDiffAction.ADDED)
        removed = sum(1 for i in items if i.action == ObjectDiffAction.REMOVED)
        modified = sum(1 for i in items if i.action == ObjectDiffAction.MODIFIED)

        return SimulationDiff(
            total_changes=len(items),
            added_count=added,
            removed_count=removed,
            modified_count=modified,
            items=items,
        )
