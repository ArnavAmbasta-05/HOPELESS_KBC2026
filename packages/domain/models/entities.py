"""SQLAlchemy domain models for all BRD §18.1 entities.

Implements:
1. Event, Venue, Session, Participant (incl. Volunteer/Speaker), Resource
2. Vehicle, Route, Task, Notification, AttendanceRecord
3. WeatherSignal, ChangeProposal, DependencyEdge, Incident, Escalation, KnowledgeItem
4. AuditRecord (append-only)
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.domain.models.base import (
    Base,
    RevisionMixin,
    TenantScopedMixin,
    TimestampMixin,
    utc_now,
)


# ---------------------------------------------------------------------------
# 1. Event
# ---------------------------------------------------------------------------

class Event(Base, TimestampMixin, RevisionMixin):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 2. Venue
# ---------------------------------------------------------------------------

class Venue(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "venues"

    venue_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    building: Mapped[str] = mapped_column(String(100), nullable=False)
    venue_type: Mapped[str] = mapped_column(String(32), default="indoor", nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_venues_event_id_building", "event_id", "building"),
    )


# ---------------------------------------------------------------------------
# 3. Session
# ---------------------------------------------------------------------------

class Session(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    venue_id: Mapped[str] = mapped_column(String(64), ForeignKey("venues.venue_id"), nullable=False, index=True)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    registrants: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="scheduled", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_sessions_event_id_date", "event_id", "session_date"),
    )


# ---------------------------------------------------------------------------
# 4. Participant (Attendees, Volunteers, Speakers, VIPs)
# ---------------------------------------------------------------------------

class Participant(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "participants"

    participant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="attendee", nullable=False)
    arrival_building: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    assigned_venue_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    skill: Mapped[str | None] = mapped_column(String(64), nullable=True)
    volunteer_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_participants_event_role", "event_id", "role"),
    )


# ---------------------------------------------------------------------------
# 5. Resource (Equipment, Signs, Staging)
# ---------------------------------------------------------------------------

class Resource(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "resources"

    resource_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(32), default="other", nullable=False)
    location: Mapped[str] = mapped_column(String(100), default="Store", nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    assigned_venue_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    assigned_session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 6. Vehicle
# ---------------------------------------------------------------------------

class Vehicle(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "vehicles"

    vehicle_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="available", nullable=False)
    current_location: Mapped[str] = mapped_column(String(100), default="Gate 1", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 7. Route
# ---------------------------------------------------------------------------

class Route(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "routes"

    route_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 8. Task
# ---------------------------------------------------------------------------

class Task(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    team: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    venue_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    slack_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 9. Notification / Public Communication
# ---------------------------------------------------------------------------

class Notification(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "notifications"

    notification_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mentions_venue_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 10. AttendanceRecord (RULE-07: never mutates registration rows)
# ---------------------------------------------------------------------------

class AttendanceRecord(Base, TenantScopedMixin):
    __tablename__ = "attendance_records"

    attendance_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("sessions.session_id"), nullable=False, index=True)
    participant_id: Mapped[str] = mapped_column(String(64), ForeignKey("participants.participant_id"), nullable=False, index=True)
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    scanner_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_attendance_event_session", "event_id", "session_id"),
    )


# ---------------------------------------------------------------------------
# 11. WeatherSignal
# ---------------------------------------------------------------------------

class WeatherSignal(Base, TenantScopedMixin):
    __tablename__ = "weather_signals"

    signal_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    forecast_window: Mapped[str] = mapped_column(String(64), nullable=False)
    condition: Mapped[str] = mapped_column(String(64), nullable=False)
    wind_speed_kmh: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rainfall_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_hazard: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 12. ChangeProposal
# ---------------------------------------------------------------------------

class ChangeProposal(Base, TimestampMixin, RevisionMixin, TenantScopedMixin):
    __tablename__ = "change_proposals"

    proposal_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending_approval", nullable=False)
    proposed_by: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    plan_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 13. DependencyEdge (TAD §9 graph engine)
# ---------------------------------------------------------------------------

class DependencyEdge(Base, TenantScopedMixin):
    __tablename__ = "dependency_edges"

    edge_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    edge_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    validity_interval: Mapped[str | None] = mapped_column(String(64), nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_edges_source_target_type", "event_id", "source_id", "target_id", "edge_type"),
    )


# ---------------------------------------------------------------------------
# 14. Incident & Escalation
# ---------------------------------------------------------------------------

class Incident(Base, TimestampMixin, TenantScopedMixin):
    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="high", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    venue_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class Escalation(Base, TimestampMixin, TenantScopedMixin):
    __tablename__ = "escalations"

    escalation_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    incident_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    escalated_to_role: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 15. KnowledgeItem
# ---------------------------------------------------------------------------

class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# ---------------------------------------------------------------------------
# 16. AuditRecord (Append-Only System of Record — BR-015, TAD §18)
# ---------------------------------------------------------------------------

class AuditRecord(Base, TenantScopedMixin):
    """Append-only audit log table. No UPDATE or DELETE path is ever exposed."""
    __tablename__ = "audit_records"

    audit_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    before_state: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    __table_args__ = (
        Index("ix_audit_event_entity", "event_id", "entity_type", "entity_id"),
    )
