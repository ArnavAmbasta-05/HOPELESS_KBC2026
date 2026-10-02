"""Unit tests for domain entity model definitions and constraints (S1-T1)."""

from __future__ import annotations

import datetime as dt
import pytest

from packages.domain.models import (
    AttendanceRecord,
    AuditRecord,
    ChangeProposal,
    DependencyEdge,
    Escalation,
    Event,
    Incident,
    KnowledgeItem,
    Notification,
    Participant,
    Resource,
    Route,
    Session,
    Task,
    Vehicle,
    Venue,
    WeatherSignal,
)


class TestDomainModelStructure:
    def test_all_16_entities_defined(self) -> None:
        models = [
            Event,
            Venue,
            Session,
            Participant,
            Resource,
            Vehicle,
            Route,
            Task,
            Notification,
            AttendanceRecord,
            WeatherSignal,
            ChangeProposal,
            DependencyEdge,
            Incident,
            Escalation,
            KnowledgeItem,
            AuditRecord,
        ]
        for m in models:
            assert hasattr(m, "__tablename__")

    def test_event_instantiation(self) -> None:
        event = Event(
            event_id="evt_test",
            name="Test Event",
            description="Test description",
            start_date=dt.date(2026, 10, 15),
            end_date=dt.date(2026, 10, 16),
            timezone="Asia/Kolkata",
            revision=1,
        )
        assert event.event_id == "evt_test"
        assert event.name == "Test Event"
        assert event.revision == 1

    def test_venue_instantiation(self) -> None:
        venue = Venue(
            venue_id="ven_test",
            event_id="evt_test",
            name="Test Hall",
            capacity=300,
            building="Bldg A",
            venue_type="indoor",
            is_available=True,
            revision=1,
        )
        assert venue.capacity == 300
        assert venue.is_available is True
        assert venue.revision == 1

    def test_session_instantiation(self) -> None:
        session = Session(
            session_id="ses_test",
            event_id="evt_test",
            name="Opening Session",
            venue_id="ven_test",
            session_date=dt.date(2026, 10, 15),
            start_time=dt.time(10, 0),
            end_time=dt.time(11, 0),
            registrants=150,
            status="scheduled",
            revision=1,
        )
        assert session.registrants == 150
        assert session.status == "scheduled"
        assert session.revision == 1
