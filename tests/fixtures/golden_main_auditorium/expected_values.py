"""
Expected values for the Main Auditorium outage golden scenario.

These constants encode every deterministic outcome from
kbc03_simulation_output.txt so that regression tests can assert
against them without re-parsing the narrative fixture.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# [1] Blast radius
# ---------------------------------------------------------------------------

EXPECTED_HARD_HITS: Final[int] = 12
"""
4 hosts (sessions at Main Auditorium)
+ 2 task_at (AV setup, Stage decor)
+ 2 mentions (Instagram post, Printed schedule boards)
+ 4 has_registrants (380 + 230 + 180 + 390 registrant cohorts)
= 12 hard-hit nodes.
"""

EXPECTED_SOFT_EDGES_DEFERRED: Final[int] = 7
"""
Deferred to re-evaluation after resolution:
  Chief Guest (Vice Chancellor)       -- 1
  Dr. Mehra (Keynote)                 -- 1
  Startup panel (3 founders)          -- 3
  Volunteer staffing                  -- 2 (Dev removal + standby consideration)
= 7 soft edges.
"""

# ---------------------------------------------------------------------------
# [2] Venue resolution
# ---------------------------------------------------------------------------

EXPECTED_VENUE_REASSIGNMENTS: Final[dict[str, str]] = {
    "Opening Ceremony": "Open Air Theatre",
    "Keynote: AI in FinTech": "Seminar Hall",
    "Panel: Building Startups": "Open Air Theatre",
    "Prize Distribution": "Open Air Theatre",
}
"""Session name -> new venue name after Main Auditorium outage."""

EXPECTED_EQUIPMENT_MOVES: Final[list[dict[str, str]]] = [
    {
        "equipment": "Stage-light rig",
        "from": "Store",
        "to": "Open Air Theatre",
        "for_session": "Opening Ceremony",
    },
    {
        "equipment": "Portable projector + screen",
        "from": "Store",
        "to": "Open Air Theatre",
        "for_session": "Panel: Building Startups",
    },
    {
        "equipment": "Stage-light rig",
        "from": "Store",
        "to": "Open Air Theatre",
        "for_session": "Prize Distribution",
    },
]
"""Equipment moves required by the venue reassignment."""

# ---------------------------------------------------------------------------
# Speaker soft-edge re-evaluation
# ---------------------------------------------------------------------------

EXPECTED_SPEAKER_ESCORT_NEEDED: Final[list[str]] = [
    "Chief Guest (Vice Chancellor)",
    "Startup panel (3 founders)",
]
"""Speakers needing escort because their arrival building differs from new venue building."""

EXPECTED_SPEAKER_NO_ACTION: Final[list[str]] = [
    "Dr. Mehra",
]
"""Speakers whose arrival building is unchanged (Bldg B -> Seminar Hall in Bldg B)."""

# ---------------------------------------------------------------------------
# [3] Volunteer re-allocation
# ---------------------------------------------------------------------------

EXPECTED_VOLUNTEER_CHANGES: Final[list[dict[str, str]]] = [
    {
        "action": "removed",
        "name": "Dev",
        "from_session": "Keynote: AI in FinTech",
        "role": "AV",
    },
    {
        "action": "assigned",
        "name": "Kabir",
        "to_session": "Prize Distribution",
        "role": "crowd",
        "venue": "Open Air Theatre",
    },
    {
        "action": "assigned",
        "name": "Tanya",
        "to_session": "Opening Ceremony",
        "role": "crowd",
        "venue": "Open Air Theatre",
    },
    {
        "action": "assigned",
        "name": "Meera",
        "to_session": "Panel: Building Startups",
        "role": "crowd",
        "venue": "Open Air Theatre",
    },
    {
        "action": "standby_activated",
        "name": "Arjun",
        "to_session": "Keynote: AI in FinTech",
        "role": "AV",
        "venue": "Seminar Hall",
    },
]
"""Volunteer changes: 1 removal + 3 crowd assignments + 1 standby activation."""

# ---------------------------------------------------------------------------
# [4] Follow-up task plan
# ---------------------------------------------------------------------------

EXPECTED_TASKS: Final[int] = 17
"""Total follow-up tasks generated (N01 through N17)."""

EXPECTED_AT_RISK_TASKS: Final[list[str]] = [
    "N08",
]
"""Task IDs with zero slack (AT RISK)."""

EXPECTED_AT_RISK_TASK_DETAILS: Final[dict[str, str]] = {
    "N08": "Opening act rehearsal at Open Air Theatre",
}
"""Description of each at-risk task."""

# ---------------------------------------------------------------------------
# [5] Escalations
# ---------------------------------------------------------------------------

EXPECTED_ESCALATIONS: Final[list[dict[str, str]]] = [
    {
        "task_id": "N08",
        "description": "Opening act rehearsal at Open Air Theatre",
        "slack": "0m",
        "escalate_to": "stage lead",
    },
]
"""Tasks escalated because their slack is critically low."""

# ---------------------------------------------------------------------------
# Registrant cohorts
# ---------------------------------------------------------------------------

EXPECTED_REGISTRANT_COHORTS: Final[dict[str, int]] = {
    "Opening Ceremony": 380,
    "Keynote: AI in FinTech": 230,
    "Panel: Building Startups": 180,
    "Prize Distribution": 390,
}
"""Session name -> registrant count (all must be notified of venue change)."""

# ---------------------------------------------------------------------------
# Stale communications
# ---------------------------------------------------------------------------

EXPECTED_STALE_COMMS: Final[list[dict[str, str]]] = [
    {
        "type": "instagram",
        "content": "Opening at Main Auditorium",
        "action_needed": "Re-issue with new venue",
    },
    {
        "type": "printed_board",
        "location": "Gate 1",
        "action_needed": "Update schedule boards & venue signage",
    },
    {
        "type": "printed_board",
        "location": "Gate 3",
        "action_needed": "Update schedule boards & venue signage",
    },
]
"""Public communications that become stale after the venue change."""

# ---------------------------------------------------------------------------
# [6] Notion write plan
# ---------------------------------------------------------------------------

EXPECTED_NOTION_WRITES: Final[int] = 32
"""Approximate number of Notion API calls to apply the full change plan.
   4 session updates + 5 assignment edits + 17 task pages + flags + 1 Impact
   Report + 1 Change Proposal = ~32."""
