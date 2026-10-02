"""Shared Pydantic contracts and schemas for KoreX domain entities (TAD §20, §27).

Defines canonical representations, creation schemas, update schemas, and filters.
"""

from __future__ import annotations

from datetime import date, datetime, time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VenueType(StrEnum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"


class SessionStatus(StrEnum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class ParticipantRole(StrEnum):
    ATTENDEE = "attendee"
    SPEAKER = "speaker"
    VOLUNTEER = "volunteer"
    VIP = "vip"
    ORGANIZER = "organizer"


class VolunteerStatus(StrEnum):
    ACTIVE = "active"
    STANDBY = "standby"
    UNAVAILABLE = "unavailable"


class ResourceCategory(StrEnum):
    AV = "av"
    STAGE = "stage"
    SIGNAGE = "signage"
    FURNITURE = "furniture"
    VEHICLE = "vehicle"
    OTHER = "other"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    AT_RISK = "at_risk"


class NotificationChannel(StrEnum):
    INSTAGRAM = "instagram"
    PRINTED_BOARD = "printed_board"
    SMS = "sms"
    EMAIL = "email"
    APP_PUSH = "app_push"


# ---------------------------------------------------------------------------
# Base & Metadata
# ---------------------------------------------------------------------------

class EntityBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Event Schemas
# ---------------------------------------------------------------------------

class EventCreate(BaseModel):
    event_id: str = Field(..., description="Canonical event ID (e.g. evt_kbc2026)")
    name: str = Field(..., min_length=2, max_length=255)
    description: str = ""
    start_date: date
    end_date: date
    timezone: str = Field(default="Asia/Kolkata")
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class EventUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    timezone: str | None = None
    metadata_json: dict[str, Any] | None = None


class EventRead(EntityBase):
    event_id: str
    name: str
    description: str
    start_date: date
    end_date: date
    timezone: str
    revision: int
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Venue Schemas
# ---------------------------------------------------------------------------

class VenueCreate(BaseModel):
    venue_id: str = Field(..., description="Canonical venue ID (e.g. ven_main_aud)")
    event_id: str
    name: str = Field(..., min_length=2, max_length=255)
    capacity: int = Field(..., gt=0, description="Validated positive integer capacity")
    building: str = Field(..., min_length=1, max_length=100)
    venue_type: VenueType = VenueType.INDOOR
    is_available: bool = True
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class VenueUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    building: str | None = None
    venue_type: VenueType | None = None
    is_available: bool | None = None
    metadata_json: dict[str, Any] | None = None


class VenueRead(EntityBase):
    venue_id: str
    event_id: str
    name: str
    capacity: int
    building: str
    venue_type: VenueType
    is_available: bool
    revision: int
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Session Schemas
# ---------------------------------------------------------------------------

class SessionCreate(BaseModel):
    session_id: str = Field(..., description="Canonical session ID (e.g. ses_opening)")
    event_id: str
    name: str = Field(..., min_length=2, max_length=255)
    description: str = ""
    venue_id: str
    session_date: date
    start_time: time
    end_time: time
    registrants: int = Field(default=0, ge=0)
    status: SessionStatus = SessionStatus.SCHEDULED
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class SessionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    venue_id: str | None = None
    session_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    registrants: int | None = Field(default=None, ge=0)
    status: SessionStatus | None = None
    metadata_json: dict[str, Any] | None = None


class SessionRead(EntityBase):
    session_id: str
    event_id: str
    name: str
    description: str
    venue_id: str
    session_date: date
    start_time: time
    end_time: time
    registrants: int
    status: SessionStatus
    revision: int
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Participant & Volunteer Schemas
# ---------------------------------------------------------------------------

class ParticipantCreate(BaseModel):
    participant_id: str = Field(..., description="Canonical participant ID (e.g. spk_dr_mehra)")
    event_id: str
    name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., max_length=255)
    role: ParticipantRole = ParticipantRole.ATTENDEE
    arrival_building: str | None = None
    assigned_session_id: str | None = None
    assigned_venue_id: str | None = None
    skill: str | None = None
    volunteer_status: VolunteerStatus | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ParticipantUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    role: ParticipantRole | None = None
    arrival_building: str | None = None
    assigned_session_id: str | None = None
    assigned_venue_id: str | None = None
    skill: str | None = None
    volunteer_status: VolunteerStatus | None = None
    metadata_json: dict[str, Any] | None = None


class ParticipantRead(EntityBase):
    participant_id: str
    event_id: str
    name: str
    email: str
    role: ParticipantRole
    arrival_building: str | None = None
    assigned_session_id: str | None = None
    assigned_venue_id: str | None = None
    skill: str | None = None
    volunteer_status: VolunteerStatus | None = None
    revision: int
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Resource Schemas
# ---------------------------------------------------------------------------

class ResourceCreate(BaseModel):
    resource_id: str = Field(..., description="Canonical resource ID (e.g. res_stage_light)")
    event_id: str
    name: str = Field(..., min_length=2, max_length=255)
    category: ResourceCategory = ResourceCategory.OTHER
    location: str = Field(default="Store", min_length=1, max_length=100)
    quantity: int = Field(default=1, gt=0)
    assigned_venue_id: str | None = None
    assigned_session_id: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ResourceUpdate(BaseModel):
    name: str | None = None
    category: ResourceCategory | None = None
    location: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    assigned_venue_id: str | None = None
    assigned_session_id: str | None = None
    metadata_json: dict[str, Any] | None = None


class ResourceRead(EntityBase):
    resource_id: str
    event_id: str
    name: str
    category: ResourceCategory
    location: str
    quantity: int
    assigned_venue_id: str | None
    assigned_session_id: str | None
    revision: int
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Audit Record Schemas (Append-only)
# ---------------------------------------------------------------------------

class AuditRecordRead(EntityBase):
    audit_id: str
    event_id: str
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    trace_id: str | None = None
    correlation_id: str | None = None
    created_at: datetime
