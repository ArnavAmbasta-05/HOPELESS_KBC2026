"""Participant itinerary dispatch.

Sends every registered participant of an event their personal itinerary:
event + session details, venue, timings AND their transport plan (hostel
shuttle route + pickup time). Built from the real attendance roster, the
golden-scenario session timings and a deterministic transport plan, so it is
fully demonstrable (register someone in the Participant Portal, then dispatch).

Dispatch here is simulated (no SMS/email is actually sent); each itinerary is
composed and marked queued on the participant's available channels. Swap the
_dispatch() body for a real provider (Twilio / SES / FCM) in production.
"""

from __future__ import annotations

import datetime as _dt
import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.domain import seed
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.api.routers import attendance as attendance_mod

router = APIRouter(prefix="/api/v1/itineraries", tags=["participant itineraries"])


# Deterministic transport plan per venue (hostel shuttle → venue).
_TRANSPORT_BY_VENUE: dict[str, dict[str, str]] = {
    "ven_main_aud": {"route": "Route 1 · Hostel Loop → Main Auditorium (Campus 6)", "bay": "Bay 1, Campus 6 Gate"},
    "ven_open_air": {"route": "Route 1 · Hostel Loop → Open Air Theatre (Campus 6)", "bay": "Bay 4, Campus 6 Gate"},
    "ven_seminar": {"route": "Route 3 · KP-14 → Campus 7 Seminar Hall", "bay": "Bay 2, Campus 7 Link Gate"},
    "ven_lh3": {"route": "Route 2 · Queen's Castle → LH-3 (Campus 12)", "bay": "Bay 3, Campus 12"},
    "ven_lh5": {"route": "Route 2 · Queen's Castle → LH-5 (Campus 12)", "bay": "Bay 3, Campus 12"},
    "ven_oat": {"route": "Route 1 · Hostel Loop → Open Air Theatre (Campus 6)", "bay": "Bay 4, Campus 6 Gate"},
}


class ItineraryItem(BaseModel):
    participant: str
    roll_no: str
    event_name: str
    session_name: str
    venue_name: str
    session_window_ist: str
    transport_route: str
    pickup_point: str
    pickup_time_ist: str
    channels: list[str]
    message: str


class DispatchResult(BaseModel):
    event_id: str
    dispatched: int
    channels_used: list[str]
    itineraries: list[ItineraryItem]
    note: str


def _session_by_id(session_id: str) -> seed.Session | None:
    for s in seed.SESSIONS:
        if s.session_id == session_id:
            return s
    return None


def _fmt(t: _dt.time) -> str:
    return t.strftime("%H:%M")


def _pickup(start: _dt.time, minutes: int = 40) -> str:
    base = _dt.datetime.combine(_dt.date.today(), start) - _dt.timedelta(minutes=minutes)
    return base.strftime("%H:%M")


def _build_itinerary(rec) -> ItineraryItem:
    session = _session_by_id(rec.session_id)
    if session:
        window = f"{_fmt(session.start_time)}–{_fmt(session.end_time)} IST"
        pickup_time = f"{_pickup(session.start_time)} IST"
    else:
        window = "See schedule"
        pickup_time = "45 min before start"

    venue_key = rec.venue_id if rec.venue_id in _TRANSPORT_BY_VENUE else "ven_oat"
    transport = _TRANSPORT_BY_VENUE[venue_key]

    channels: list[str] = []
    if getattr(rec, "email", None):
        channels.append("email")
    if getattr(rec, "phone", None):
        channels.append("sms")
    channels.append("app_push")

    message = (
        f"Hi {rec.full_name}, your KBC 2026 itinerary:\n"
        f"• Session: {rec.session_name} ({window})\n"
        f"• Venue: {rec.venue_name}\n"
        f"• Shuttle: {transport['route']}\n"
        f"• Pickup: {transport['bay']} at {pickup_time}\n"
        f"Please arrive at the pickup point 5 minutes early. — KoreX Ops"
    )

    return ItineraryItem(
        participant=rec.full_name,
        roll_no=rec.roll_no,
        event_name=seed.EVENT_NAME,
        session_name=rec.session_name,
        venue_name=rec.venue_name,
        session_window_ist=window,
        transport_route=transport["route"],
        pickup_point=transport["bay"],
        pickup_time_ist=pickup_time,
        channels=channels,
        message=message,
    )


@router.get(
    "/preview",
    response_model=ResponseEnvelope[list[ItineraryItem]],
    summary="Preview per-participant itineraries (event + transport + timings)",
)
async def preview_itineraries(
    session_id: str | None = Query(default=None),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[ItineraryItem]]:
    records = list(attendance_mod._participant_roster.values())
    if session_id:
        records = [r for r in records if r.session_id == session_id]
    items = [_build_itinerary(r) for r in records]
    return make_success_envelope(data=items, request_id=str(uuid.uuid4()))


@router.post(
    "/dispatch",
    response_model=ResponseEnvelope[DispatchResult],
    summary="Dispatch itineraries to all registered participants",
)
async def dispatch_itineraries(
    session_id: str | None = Query(default=None),
    user: AuthUser = Depends(require_permission(Permission.NOTIFICATION_SEND)),
) -> ResponseEnvelope[DispatchResult]:
    records = list(attendance_mod._participant_roster.values())
    if session_id:
        records = [r for r in records if r.session_id == session_id]

    items = [_build_itinerary(r) for r in records]
    channels_used = sorted({c for it in items for c in it.channels})

    result = DispatchResult(
        event_id=seed.EVENT_ID,
        dispatched=len(items),
        channels_used=channels_used,
        itineraries=items,
        note="Simulated dispatch — composed and queued per channel; wire a real provider for production.",
    )
    return make_success_envelope(data=result, request_id=str(uuid.uuid4()))
