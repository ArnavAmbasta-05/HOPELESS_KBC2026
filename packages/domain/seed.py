"""
KIIT EventOps AI Command Center -- Golden Scenario Seed Data
=============================================================
Deterministic seed for KBC 2026 (KIIT Business Conclave).

This module defines every entity referenced in the golden simulation
(kbc03_simulation_output.txt -- Main Auditorium outage scenario) as typed
Python dataclasses.  The data is intentionally static: no DB dependency,
no randomness, no datetime.now().  When persistence models arrive in
Sprint 1 the loader will map these dataclasses to ORM objects.

Entity IDs follow the canonical scheme from TAD section 20.1.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Final


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EVENT_ID: Final[str] = "evt_kbc2026"
EVENT_NAME: Final[str] = "KBC 2026 (KIIT Business Conclave)"
EVENT_DATE: Final[_dt.date] = _dt.date(2026, 10, 15)
EVENT_TIMEZONE: Final[str] = "Asia/Kolkata"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VenueType(str, Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"


class VolunteerStatus(str, Enum):
    ACTIVE = "active"
    STANDBY = "standby"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    AT_RISK = "at_risk"


class CommChannel(str, Enum):
    INSTAGRAM = "instagram"
    PRINTED_BOARD = "printed_board"
    SMS = "sms"
    EMAIL = "email"
    APP_PUSH = "app_push"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Venue:
    venue_id: str
    name: str
    capacity: int
    building: str
    venue_type: VenueType
    event_id: str = EVENT_ID


@dataclass(frozen=True)
class Session:
    session_id: str
    name: str
    start_time: _dt.time
    end_time: _dt.time
    registrants: int
    venue_id: str
    event_id: str = EVENT_ID
    date: _dt.date = EVENT_DATE


@dataclass(frozen=True)
class Volunteer:
    staff_id: str
    name: str
    role: str
    skill: str
    assigned_session_id: str | None
    assigned_venue_id: str | None
    status: VolunteerStatus
    event_id: str = EVENT_ID


@dataclass(frozen=True)
class Speaker:
    participant_id: str
    name: str
    title: str
    arrival_building: str
    session_id: str
    event_id: str = EVENT_ID


@dataclass(frozen=True)
class Equipment:
    resource_id: str
    name: str
    location: str
    event_id: str = EVENT_ID


@dataclass(frozen=True)
class Task:
    task_id: str
    description: str
    status: TaskStatus
    team: str
    venue_id: str
    event_id: str = EVENT_ID


@dataclass(frozen=True)
class PublicComm:
    notification_id: str
    channel: CommChannel
    content: str
    location: str | None
    mentions_venue_id: str
    event_id: str = EVENT_ID


# ---------------------------------------------------------------------------
# Venue seed data
# ---------------------------------------------------------------------------

VENUE_MAIN_AUDITORIUM = Venue(
    venue_id="ven_main_aud",
    name="Main Auditorium",
    capacity=500,
    building="Bldg A",
    venue_type=VenueType.INDOOR,
)

VENUE_OPEN_AIR_THEATRE = Venue(
    venue_id="ven_open_air",
    name="Open Air Theatre",
    capacity=600,
    building="Bldg C",
    venue_type=VenueType.OUTDOOR,
)

VENUE_SEMINAR_HALL = Venue(
    venue_id="ven_seminar",
    name="Seminar Hall",
    capacity=250,
    building="Bldg B",
    venue_type=VenueType.INDOOR,
)

VENUE_LH3 = Venue(
    venue_id="ven_lh3",
    name="LH-3",
    capacity=150,
    building="Bldg D",
    venue_type=VenueType.INDOOR,
)

VENUE_LH5 = Venue(
    venue_id="ven_lh5",
    name="LH-5",
    capacity=120,
    building="Bldg D",
    venue_type=VenueType.INDOOR,
)

VENUES: list[Venue] = [
    VENUE_MAIN_AUDITORIUM,
    VENUE_OPEN_AIR_THEATRE,
    VENUE_SEMINAR_HALL,
    VENUE_LH3,
    VENUE_LH5,
]


# ---------------------------------------------------------------------------
# Session seed data
# ---------------------------------------------------------------------------

SESSION_OPENING = Session(
    session_id="ses_opening",
    name="Opening Ceremony",
    start_time=_dt.time(10, 0),
    end_time=_dt.time(10, 45),
    registrants=380,
    venue_id="ven_main_aud",
)

SESSION_KEYNOTE = Session(
    session_id="ses_keynote_ai_fintech",
    name="Keynote: AI in FinTech",
    start_time=_dt.time(11, 0),
    end_time=_dt.time(12, 0),
    registrants=230,
    venue_id="ven_main_aud",
)

SESSION_PANEL = Session(
    session_id="ses_panel_startups",
    name="Panel: Building Startups",
    start_time=_dt.time(14, 0),
    end_time=_dt.time(15, 0),
    registrants=180,
    venue_id="ven_main_aud",
)

SESSION_PRIZE = Session(
    session_id="ses_prize_dist",
    name="Prize Distribution",
    start_time=_dt.time(17, 0),
    end_time=_dt.time(18, 0),
    registrants=390,
    venue_id="ven_main_aud",
)

SESSIONS: list[Session] = [
    SESSION_OPENING,
    SESSION_KEYNOTE,
    SESSION_PANEL,
    SESSION_PRIZE,
]


# ---------------------------------------------------------------------------
# Volunteer seed data (16 assignments + 1 standby = 17 total)
# ---------------------------------------------------------------------------

VOLUNTEERS: list[Volunteer] = [
    # Key volunteers referenced in the golden simulation
    Volunteer(
        staff_id="vol_dev",
        name="Dev",
        role="AV Technician",
        skill="av",
        assigned_session_id="ses_keynote_ai_fintech",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_kabir",
        name="Kabir",
        role="Crowd Management",
        skill="crowd",
        assigned_session_id=None,
        assigned_venue_id=None,
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_tanya",
        name="Tanya",
        role="Crowd Management",
        skill="crowd",
        assigned_session_id=None,
        assigned_venue_id=None,
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_meera",
        name="Meera",
        role="Crowd Management",
        skill="crowd",
        assigned_session_id=None,
        assigned_venue_id=None,
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_arjun",
        name="Arjun",
        role="AV Technician",
        skill="av",
        assigned_session_id=None,
        assigned_venue_id=None,
        status=VolunteerStatus.STANDBY,
    ),
    # 12 other assigned volunteers across sessions/roles
    Volunteer(
        staff_id="vol_riya",
        name="Riya",
        role="Registration Desk",
        skill="registration",
        assigned_session_id="ses_opening",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_sahil",
        name="Sahil",
        role="Stage Coordinator",
        skill="stage",
        assigned_session_id="ses_opening",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_neha",
        name="Neha",
        role="Usher",
        skill="crowd",
        assigned_session_id="ses_opening",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_rohan",
        name="Rohan",
        role="Usher",
        skill="crowd",
        assigned_session_id="ses_keynote_ai_fintech",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_priti",
        name="Priti",
        role="Registration Desk",
        skill="registration",
        assigned_session_id="ses_keynote_ai_fintech",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_amit",
        name="Amit",
        role="Usher",
        skill="crowd",
        assigned_session_id="ses_panel_startups",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_divya",
        name="Divya",
        role="Registration Desk",
        skill="registration",
        assigned_session_id="ses_panel_startups",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_karan",
        name="Karan",
        role="Stage Coordinator",
        skill="stage",
        assigned_session_id="ses_prize_dist",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_sonal",
        name="Sonal",
        role="Usher",
        skill="crowd",
        assigned_session_id="ses_prize_dist",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_vikram",
        name="Vikram",
        role="Registration Desk",
        skill="registration",
        assigned_session_id="ses_prize_dist",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_pooja",
        name="Pooja",
        role="Hospitality",
        skill="hospitality",
        assigned_session_id="ses_opening",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
    Volunteer(
        staff_id="vol_isha",
        name="Isha",
        role="Hospitality",
        skill="hospitality",
        assigned_session_id="ses_prize_dist",
        assigned_venue_id="ven_main_aud",
        status=VolunteerStatus.ACTIVE,
    ),
]

# Confirm: 16 assigned roles across 17 volunteers (13 assigned + 3 active crowd pool + 1 standby = 17 total)
assert len(VOLUNTEERS) == 17
assert sum(1 for v in VOLUNTEERS if v.status == VolunteerStatus.STANDBY) == 1
assert sum(1 for v in VOLUNTEERS if v.assigned_session_id is not None) == 13  # 12 others + Dev
# Dev is assigned to Keynote; 12 others assigned to sessions; Kabir, Tanya, Meera are active unassigned; Arjun is standby


# ---------------------------------------------------------------------------
# Speaker seed data
# ---------------------------------------------------------------------------

SPEAKERS: list[Speaker] = [
    Speaker(
        participant_id="spk_chief_guest",
        name="Chief Guest (Vice Chancellor)",
        title="Vice Chancellor",
        arrival_building="Bldg A",
        session_id="ses_opening",
    ),
    Speaker(
        participant_id="spk_dr_mehra",
        name="Dr. Mehra",
        title="Keynote Speaker",
        arrival_building="Bldg B",
        session_id="ses_keynote_ai_fintech",
    ),
    Speaker(
        participant_id="spk_ankit",
        name="Ankit",
        title="Startup Founder",
        arrival_building="Bldg B",
        session_id="ses_panel_startups",
    ),
    Speaker(
        participant_id="spk_priya",
        name="Priya",
        title="Startup Founder",
        arrival_building="Bldg B",
        session_id="ses_panel_startups",
    ),
    Speaker(
        participant_id="spk_ravi",
        name="Ravi",
        title="Startup Founder",
        arrival_building="Bldg B",
        session_id="ses_panel_startups",
    ),
]


# ---------------------------------------------------------------------------
# Equipment / resource seed data
# ---------------------------------------------------------------------------

EQUIPMENT: list[Equipment] = [
    Equipment(
        resource_id="res_stage_light",
        name="Stage-light rig",
        location="Store",
    ),
    Equipment(
        resource_id="res_projector_screen",
        name="Portable projector + screen",
        location="Store",
    ),
]


# ---------------------------------------------------------------------------
# Pre-existing task seed data
# ---------------------------------------------------------------------------

TASKS: list[Task] = [
    Task(
        task_id="tsk_av_setup",
        description="AV setup in Main Auditorium",
        status=TaskStatus.IN_PROGRESS,
        team="tech",
        venue_id="ven_main_aud",
    ),
    Task(
        task_id="tsk_stage_decor",
        description="Stage decor in Main Auditorium",
        status=TaskStatus.PENDING,
        team="stage",
        venue_id="ven_main_aud",
    ),
]


# ---------------------------------------------------------------------------
# Public communications seed data
# ---------------------------------------------------------------------------

PUBLIC_COMMS: list[PublicComm] = [
    PublicComm(
        notification_id="comm_insta_opening",
        channel=CommChannel.INSTAGRAM,
        content="Opening at Main Auditorium",
        location=None,
        mentions_venue_id="ven_main_aud",
    ),
    PublicComm(
        notification_id="comm_board_gate1",
        channel=CommChannel.PRINTED_BOARD,
        content="Printed schedule board at Gate 1",
        location="Gate 1",
        mentions_venue_id="ven_main_aud",
    ),
    PublicComm(
        notification_id="comm_board_gate3",
        channel=CommChannel.PRINTED_BOARD,
        content="Printed schedule board at Gate 3",
        location="Gate 3",
        mentions_venue_id="ven_main_aud",
    ),
]


# ---------------------------------------------------------------------------
# Aggregate: full seed for golden scenario
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GoldenSeed:
    """Complete seed dataset for the KBC 2026 golden simulation scenario."""

    event_id: str = EVENT_ID
    event_name: str = EVENT_NAME
    event_date: _dt.date = EVENT_DATE
    event_timezone: str = EVENT_TIMEZONE
    venues: list[Venue] = field(default_factory=lambda: list(VENUES))
    sessions: list[Session] = field(default_factory=lambda: list(SESSIONS))
    volunteers: list[Volunteer] = field(default_factory=lambda: list(VOLUNTEERS))
    speakers: list[Speaker] = field(default_factory=lambda: list(SPEAKERS))
    equipment: list[Equipment] = field(default_factory=lambda: list(EQUIPMENT))
    tasks: list[Task] = field(default_factory=lambda: list(TASKS))
    public_comms: list[PublicComm] = field(default_factory=lambda: list(PUBLIC_COMMS))


def load_golden_seed() -> GoldenSeed:
    """Return the complete golden scenario seed. Deterministic, no side effects."""
    return GoldenSeed()
