"""Integration tests for CRUD APIs, Envelopes, Idempotency, RBAC, and Audit Logging (Sprint 1)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from services.api.auth.providers import DevLoginProvider


def make_token(roles: list[str], event_id: str = "evt_kbc2026") -> str:
    provider = DevLoginProvider()
    return provider.create_token(
        email="test@korex.kiit.ac.in",
        name="Test User",
        roles=roles,
        event_id=event_id,
    )


@pytest.mark.asyncio
async def test_event_crud_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # 1. Create Event
    create_payload = {
        "event_id": "evt_kbc2026",
        "name": "KIIT Business Conclave 2026",
        "description": "Flagship university business and tech conclave",
        "start_date": "2026-10-15",
        "end_date": "2026-10-16",
        "timezone": "Asia/Kolkata",
    }
    res = await async_client.post("/api/v1/events", json=create_payload, headers=auth_headers)
    assert res.status_code == 201
    body = res.json()
    assert body["data"]["event_id"] == "evt_kbc2026"
    assert body["meta"]["revision"] == 1
    assert body["error"] is None

    # 2. Get Event
    get_res = await async_client.get("/api/v1/events/evt_kbc2026", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["name"] == "KIIT Business Conclave 2026"

    # 3. Update Event with valid revision
    update_headers = {**auth_headers, "If-Match": "1"}
    up_res = await async_client.put(
        "/api/v1/events/evt_kbc2026",
        json={"name": "KBC 2026 (Updated)"},
        headers=update_headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["data"]["name"] == "KBC 2026 (Updated)"
    assert up_res.json()["meta"]["revision"] == 2

    # 4. Stale revision returns 409 Conflict (AT-06 primitive)
    stale_headers = {**auth_headers, "If-Match": "1"}
    stale_res = await async_client.put(
        "/api/v1/events/evt_kbc2026",
        json={"name": "Should Fail"},
        headers=stale_headers,
    )
    assert stale_res.status_code == 409
    assert stale_res.json()["error"]["code"] == "STALE_REVISION_CONFLICT"


@pytest.mark.asyncio
async def test_venue_crud_and_idempotency(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # First create parent event
    await async_client.post(
        "/api/v1/events",
        json={
            "event_id": "evt_kbc2026",
            "name": "KBC 2026",
            "start_date": "2026-10-15",
            "end_date": "2026-10-16",
        },
        headers=auth_headers,
    )

    venue_payload = {
        "venue_id": "ven_main_aud",
        "event_id": "evt_kbc2026",
        "name": "Main Auditorium",
        "capacity": 500,
        "building": "Bldg A",
        "venue_type": "indoor",
    }
    idempotent_headers = {**auth_headers, "Idempotency-Key": "idem_venue_001"}

    # 1. Create with Idempotency-Key
    res1 = await async_client.post("/api/v1/venues", json=venue_payload, headers=idempotent_headers)
    assert res1.status_code == 201

    # 2. Replay same request -> Returns cached result without error
    res2 = await async_client.post("/api/v1/venues", json=venue_payload, headers=idempotent_headers)
    assert res2.status_code == 201
    assert res2.json()["data"]["venue_id"] == "ven_main_aud"

    # 3. List venues
    list_res = await async_client.get("/api/v1/venues?event_id=evt_kbc2026", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 1


@pytest.mark.asyncio
async def test_session_and_participant_crud(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # 1. Setup event & venue
    await async_client.post(
        "/api/v1/events",
        json={
            "event_id": "evt_kbc2026",
            "name": "KBC 2026",
            "start_date": "2026-10-15",
            "end_date": "2026-10-16",
        },
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/venues",
        json={
            "venue_id": "ven_main_aud",
            "event_id": "evt_kbc2026",
            "name": "Main Auditorium",
            "capacity": 500,
            "building": "Bldg A",
            "venue_type": "indoor",
        },
        headers=auth_headers,
    )

    # 2. Create Session
    session_payload = {
        "session_id": "ses_opening",
        "event_id": "evt_kbc2026",
        "name": "Opening Ceremony",
        "venue_id": "ven_main_aud",
        "session_date": "2026-10-15",
        "start_time": "10:00:00",
        "end_time": "10:45:00",
        "registrants": 380,
    }
    s_res = await async_client.post("/api/v1/sessions", json=session_payload, headers=auth_headers)
    assert s_res.status_code == 201
    assert s_res.json()["data"]["registrants"] == 380

    # 3. Create Participant
    p_payload = {
        "participant_id": "spk_dr_mehra",
        "event_id": "evt_kbc2026",
        "name": "Dr. Mehra",
        "email": "mehra@example.com",
        "role": "speaker",
        "arrival_building": "Bldg B",
    }
    p_res = await async_client.post("/api/v1/participants", json=p_payload, headers=auth_headers)
    assert p_res.status_code == 201
    assert p_res.json()["data"]["name"] == "Dr. Mehra"


@pytest.mark.asyncio
async def test_rbac_endpoint_enforcement(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # Setup event
    await async_client.post(
        "/api/v1/events",
        json={
            "event_id": "evt_kbc2026",
            "name": "KBC 2026",
            "start_date": "2026-10-15",
            "end_date": "2026-10-16",
        },
        headers=auth_headers,
    )

    # Volunteer role token (has venue:read, session:read, attendance:scan, but NOT venue:write)
    vol_token = make_token(roles=["volunteer"])
    vol_headers = {"Authorization": f"Bearer {vol_token}"}

    # 1. Volunteer can read venues
    read_res = await async_client.get("/api/v1/venues?event_id=evt_kbc2026", headers=vol_headers)
    assert read_res.status_code == 200

    # 2. Volunteer CANNOT create venue (server-side 403 Forbidden)
    write_res = await async_client.post(
        "/api/v1/venues",
        json={
            "venue_id": "ven_hack",
            "event_id": "evt_kbc2026",
            "name": "Unauthorized Venue",
            "capacity": 100,
            "building": "Bldg X",
        },
        headers=vol_headers,
    )
    assert write_res.status_code == 403
    assert write_res.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_audit_log_capture(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # Create event and venue (each produces an audit record)
    await async_client.post(
        "/api/v1/events",
        json={
            "event_id": "evt_kbc2026",
            "name": "KBC 2026",
            "start_date": "2026-10-15",
            "end_date": "2026-10-16",
        },
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/venues",
        json={
            "venue_id": "ven_audited",
            "event_id": "evt_kbc2026",
            "name": "Audited Hall",
            "capacity": 250,
            "building": "Bldg B",
        },
        headers=auth_headers,
    )

    # Fetch audit logs (super_admin has admin:audit)
    audit_res = await async_client.get("/api/v1/audit?event_id=evt_kbc2026", headers=auth_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()["data"]
    assert len(logs) >= 2
    actions = [l["action"] for l in logs]
    assert "events.create" in actions
    assert "venues.create" in actions


@pytest.mark.asyncio
async def test_multi_event_tenant_isolation(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # User belonging exclusively to Event Alpha
    alpha_token = make_token(roles=["ops_lead"], event_id="evt_alpha")
    alpha_headers = {"Authorization": f"Bearer {alpha_token}"}

    # User belonging exclusively to Event Beta
    beta_token = make_token(roles=["ops_lead"], event_id="evt_beta")
    beta_headers = {"Authorization": f"Bearer {beta_token}"}

    # Create event alpha by super_admin
    await async_client.post(
        "/api/v1/events",
        json={
            "event_id": "evt_alpha",
            "name": "Alpha Conclave",
            "start_date": "2026-10-15",
            "end_date": "2026-10-16",
        },
        headers=auth_headers,
    )
    # Alpha user creates venue in evt_alpha
    await async_client.post(
        "/api/v1/venues",
        json={
            "venue_id": "ven_alpha_1",
            "event_id": "evt_alpha",
            "name": "Alpha 1",
            "capacity": 100,
            "building": "Bldg A",
        },
        headers=alpha_headers,
    )

    # Beta user attempts to access evt_alpha venue -> 403 Forbidden (BR-018)
    denied_res = await async_client.get("/api/v1/venues/ven_alpha_1?event_id=evt_alpha", headers=beta_headers)
    assert denied_res.status_code == 403
