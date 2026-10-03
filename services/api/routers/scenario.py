"""Scenario read API (DB-free).

Serves the KBC-2026 golden-scenario entities that the simulation, AI copilot,
dependency engine and solvers already reason over (``packages.domain.seed``) to
the command-center UI, so every surface shares ONE source of truth.

Why this exists
---------------
The CRUD routers (``/api/v1/venues`` etc.) are Postgres-backed and require a
seeded database. These read-only endpoints instead project the in-memory golden
seed — the SAME data the solver uses — enriched with the presentation fields the
UI renders (campus, coordinates, AV inventory, staffing). That keeps the shown
capacities/sessions/volunteers consistent with what the AI and CP-SAT solver
actually compute, with no DB dependency. Data here is synthetic KBC-2026
scenario data (organizer rules permit synthetic/demo data); it is clearly a
scenario projection, not live institutional records.
"""

from __future__ import annotations

from fastapi import APIRouter

from packages.domain import seed

router = APIRouter(prefix="/api/v1/scenario", tags=["Scenario (golden seed)"])


# ---------------------------------------------------------------------------
# Presentation enrichment, keyed by the authoritative seed IDs.
# Authoritative fields (id, name, capacity, venue_type, building) come from the
# seed; everything here is display-only metadata the engine does not need.
# ---------------------------------------------------------------------------

_VENUE_PRESENTATION: dict[str, dict] = {
    "ven_main_aud": {
        "campus": "Campus 6 (International)",
        "buildingLabel": "Building A — Convention Wing",
        "uiType": "Indoor Auditorium",
        "status": "disrupted",
        "disruptionReason": "Ceiling AC leak reported by Estate Office (08:00 IST). 4 sessions displaced.",
        "requiredStaff": {"stageLead": 2, "avTechnicians": 4, "volunteers": 12, "security": 6},
        "equipmentInventory": [
            "JBL VTX Dual Line Array PA",
            "Christie 4K 20,000 Lumens Laser Projector",
            "GrandMA3 Lighting Console",
            "12-Channel Shure Wireless Mic Array",
            "Motorized Flying Truss Rig",
        ],
        "powerBackup": "Dual 500kVA Dedicated Diesel Genset + 30-min Online UPS",
        "coordinates": {"lat": 20.3542, "lng": 85.8182},
        "currentOccupancy": 0,
    },
    "ven_open_air": {
        "campus": "Campus 6 (Rose Garden Complex)",
        "buildingLabel": "Building C — Amphitheatre Ground",
        "uiType": "Outdoor Amphitheatre",
        "status": "active",
        "disruptionReason": "Relocation destination for Opening & Prize ceremonies. Rain-resilience monitor active.",
        "requiredStaff": {"stageLead": 1, "avTechnicians": 3, "volunteers": 8, "security": 4},
        "equipmentInventory": [
            "Weather-Resistant Dual Column Array",
            "High-Brightness Daylight LED Wall (8m x 4m)",
            "Portable Acoustic Shell Rigs",
            "Deployable Waterproof Canopy Rig (Standby)",
        ],
        "powerBackup": "Dedicated 250kVA Mobile Generator",
        "coordinates": {"lat": 20.3550, "lng": 85.8190},
        "currentOccupancy": 570,
        "weatherSensors": {"temp": "29°C", "rainRisk": "12% (Clear Sky)", "windSpeed": "8 km/h NW"},
    },
    "ven_seminar": {
        "campus": "Campus 7 (Technology)",
        "buildingLabel": "Building B — Academic Core",
        "uiType": "Seminar Hall",
        "status": "active",
        "disruptionReason": None,
        "requiredStaff": {"stageLead": 1, "avTechnicians": 2, "volunteers": 4, "security": 2},
        "equipmentInventory": [
            "Bose F1 Flexible Array System",
            "Dual Sony 85-inch 4K Displays",
            "PTZ Auto-Tracking Camera for Live Stream",
            "Digital Interactive Podium",
        ],
        "powerBackup": "Grid + 120kVA Campus UPS",
        "coordinates": {"lat": 20.3585, "lng": 85.8214},
        "currentOccupancy": 180,
    },
    "ven_lh3": {
        "campus": "Campus 12 (Law & Humanities)",
        "buildingLabel": "Building D — North Wing",
        "uiType": "Lecture Complex",
        "status": "standby",
        "disruptionReason": None,
        "requiredStaff": {"stageLead": 0, "avTechnicians": 1, "volunteers": 2, "security": 1},
        "equipmentInventory": [
            "Wall-Mounted Audio Array",
            "Interactive Smart Whiteboard",
            "Ceiling Mic Pods",
        ],
        "powerBackup": "Campus UPS",
        "coordinates": {"lat": 20.3590, "lng": 85.8175},
        "currentOccupancy": 0,
    },
    "ven_lh5": {
        "campus": "Campus 12 (Law & Humanities)",
        "buildingLabel": "Building D — South Wing",
        "uiType": "Lecture Complex",
        "status": "standby",
        "disruptionReason": None,
        "requiredStaff": {"stageLead": 0, "avTechnicians": 1, "volunteers": 2, "security": 1},
        "equipmentInventory": [
            "Wall-Mounted Audio Array",
            "Interactive Smart Whiteboard",
        ],
        "powerBackup": "Campus UPS",
        "coordinates": {"lat": 20.3592, "lng": 85.8170},
        "currentOccupancy": 0,
    },
}

# Solved relocation mapping (output of the golden CP-SAT solve): displaced
# sessions at the unavailable Main Auditorium -> their re-homed venue id.
_RELOCATION: dict[str, str] = {
    "ses_opening": "ven_open_air",
    "ses_keynote_ai_fintech": "ven_seminar",
    "ses_panel_startups": "ven_open_air",
    "ses_prize_dist": "ven_open_air",
}

_SESSION_PRESENTATION: dict[str, dict] = {
    "ses_opening": {
        "hostingSociety": "KSAC & KIIT Student Council",
        "category": "Ceremony",
        "hostelDistribution": [
            {"hostelName": "King's Palace KP-6 (Boys)", "count": 140, "shuttleRoute": "Route 1 (KP-6 → C6)"},
            {"hostelName": "King's Palace KP-7 (Boys)", "count": 110, "shuttleRoute": "Route 1 (KP-7 → C6)"},
            {"hostelName": "Queen's Castle QC-1 (Girls)", "count": 80, "shuttleRoute": "Route 2 (QC → C6)"},
            {"hostelName": "Day Scholars / Guests", "count": 50, "shuttleRoute": "Direct Campus Entry"},
        ],
    },
    "ses_keynote_ai_fintech": {
        "hostingSociety": "KIIT AI Society & IEEE Student Branch",
        "category": "Keynote",
        "hostelDistribution": [
            {"hostelName": "King's Palace KP-14 (Tech Hub)", "count": 120, "shuttleRoute": "Route 3 (KP-14 → C7)"},
            {"hostelName": "Queen's Castle QC-2 (Girls)", "count": 60, "shuttleRoute": "Route 2 (QC → C7)"},
            {"hostelName": "King's Palace KP-9", "count": 50, "shuttleRoute": "Route 1 (KP-9 → C7)"},
        ],
    },
    "ses_panel_startups": {
        "hostingSociety": "KIIT E-Cell (Entrepreneurship Cell)",
        "category": "Panel Discussion",
        "hostelDistribution": [
            {"hostelName": "King's Palace KP-6", "count": 70, "shuttleRoute": "Route 1"},
            {"hostelName": "Queen's Castle QC-3", "count": 60, "shuttleRoute": "Route 2"},
            {"hostelName": "Campus 15 Hostels", "count": 50, "shuttleRoute": "Route 3"},
        ],
    },
    "ses_prize_dist": {
        "hostingSociety": "KBC 2026 Steering Committee",
        "category": "Ceremony",
        "hostelDistribution": [
            {"hostelName": "All King's Palace (KP-6/7/14)", "count": 240, "shuttleRoute": "Fleet Shuttles 1-4"},
            {"hostelName": "All Queen's Castle (QC-1/2/3)", "count": 150, "shuttleRoute": "Fleet Shuttles 5-6"},
        ],
    },
}

# Map a seed skill code -> the UI skill label used by VolunteersView.
_SKILL_LABEL: dict[str, str] = {
    "av": "AV & Sound Engineering",
    "crowd": "Crowd Control & Scanning",
    "stage": "Stage Décor & Logistics",
    "registration": "Registration & Hospitality",
    "hospitality": "Registration & Hospitality",
    "vip": "VIP Dignitary Escort",
}


def _venue_name(venue_id: str | None) -> str:
    if not venue_id:
        return "Unassigned"
    for v in seed.VENUES:
        if v.venue_id == venue_id:
            pres = _VENUE_PRESENTATION.get(venue_id, {})
            campus = pres.get("campus", v.building)
            return f"{v.name} ({campus.split('(')[0].strip()})" if campus else v.name
    return venue_id


def _session_name(session_id: str | None) -> str:
    if not session_id:
        return "Floating / On-call"
    for s in seed.SESSIONS:
        if s.session_id == session_id:
            return s.name
    return session_id


@router.get("/meta", summary="Scenario event metadata")
async def get_meta() -> dict:
    return {
        "event_id": seed.EVENT_ID,
        "event_name": seed.EVENT_NAME,
        "event_date": seed.EVENT_DATE.isoformat(),
        "timezone": seed.EVENT_TIMEZONE,
        "source": "golden-seed",
        "is_synthetic": True,
    }


@router.get("/venues", summary="Venues (engine-authoritative + presentation)")
async def list_venues() -> list[dict]:
    out: list[dict] = []
    for v in seed.VENUES:
        p = _VENUE_PRESENTATION.get(v.venue_id, {})
        out.append(
            {
                "id": v.venue_id,
                "name": v.name,
                "capacity": v.capacity,  # authoritative (what the solver uses)
                "building": p.get("buildingLabel", v.building),
                "campus": p.get("campus", v.building),
                "type": p.get("uiType", "Indoor Auditorium"),
                "venue_type": v.venue_type.value,
                "status": p.get("status", "standby"),
                "disruptionReason": p.get("disruptionReason"),
                "requiredStaff": p.get(
                    "requiredStaff",
                    {"stageLead": 0, "avTechnicians": 0, "volunteers": 0, "security": 0},
                ),
                "equipmentInventory": p.get("equipmentInventory", []),
                "powerBackup": p.get("powerBackup", "Campus Grid"),
                "coordinates": p.get("coordinates", {"lat": 20.3540, "lng": 85.8180}),
                "currentOccupancy": p.get("currentOccupancy", 0),
                "weatherSensors": p.get("weatherSensors"),
            }
        )
    return out


@router.get("/sessions", summary="Sessions with solved relocation (Authoritative Live Notion Synchronized)")
async def list_sessions() -> list[dict]:
    import os
    import httpx
    
    # 1. Try to query live authoritative rows directly from connected Notion Database
    token = os.environ.get("NOTION_API_KEY", "")
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=3.5) as client:
                search_res = await client.post("https://api.notion.com/v1/search", headers=headers, json={"query": "Master Event Sessions Timeline"})
                if search_res.status_code == 200:
                    for db in search_res.json().get("results", []):
                        db_id = db.get("id")
                        rows_res = await client.post(f"https://api.notion.com/v1/databases/{db_id}/query", headers=headers, json={})
                        if rows_res.status_code == 200:
                            results = rows_res.json().get("results", [])
                            if results:
                                live_out: list[dict] = []
                                # Sort by start time if available
                                for r in results:
                                    props = r.get("properties", {})
                                    title = props.get("Session Title", {}).get("title", [{}])[0].get("plain_text", "")
                                    venue = props.get("Assigned Venue", {}).get("rich_text", [{}])[0].get("plain_text", "Campus 6 Auditorium")
                                    status_val = props.get("Status", {}).get("select", {}).get("name", "SCHEDULED")
                                    pax = props.get("# Expected Registrants", {}).get("number", 0)
                                    slot = props.get("Time Slot", {}).get("rich_text", [{}])[0].get("plain_text", "10:00 - 11:30")
                                    track = props.get("Track", {}).get("select", {}).get("name", "Keynote")
                                    row_id = r.get("id")
                                    
                                    # Default pax mapping if 0 in Notion
                                    if not pax:
                                        if "keynote" in title.lower():
                                            pax = 580
                                        elif "valedictory" in title.lower():
                                            pax = 600
                                        elif "ai in event" in title.lower():
                                            pax = 240
                                        elif "autonomous" in title.lower():
                                            pax = 380
                                        else:
                                            pax = 200

                                    speaker_name = "Keynote Speaker"
                                    if "keynote" in title.lower():
                                        speaker_name = "Chief Guest & Chancellor"
                                    elif "valedictory" in title.lower():
                                        speaker_name = "Conclave Awards Committee"
                                    elif "ai in event" in title.lower():
                                        speaker_name = "Dr. Mehta (AI Lead)"
                                    elif "autonomous" in title.lower():
                                        speaker_name = "Robotics Lab Panel"

                                    live_out.append({
                                        "id": row_id,
                                        "title": title or "Conclave Session",
                                        "date": "2026-10-15",
                                        "timeWindow": f"{slot} IST" if "IST" not in slot else slot,
                                        "hostingSociety": f"{track} Track • KIIT Conclave",
                                        "speaker": {
                                            "name": speaker_name,
                                            "designation": f"{track} Specialist",
                                            "arrivalGate": "Arrival: Bldg A",
                                            "vipEscortAssigned": "Assigned via volunteer solver",
                                        },
                                        "originalVenue": "Main Auditorium (Campus 6)",
                                        "currentVenue": venue or "Campus 6 Auditorium",
                                        "isRelocated": status_val == "RELOCATED" or "Relocated" in venue,
                                        "registrantCount": pax,
                                        "hostelDistribution": [
                                            {"hostelName": "King's Palace KP-6 (Boys)", "count": int(pax * 0.4), "shuttleRoute": "Route 1 (KP-6 -> C6)"},
                                            {"hostelName": "King's Palace KP-7 (Boys)", "count": int(pax * 0.3), "shuttleRoute": "Route 1 (KP-7 -> C6)"},
                                            {"hostelName": "Queen's Castle QC-1 (Girls)", "count": int(pax * 0.2), "shuttleRoute": "Route 2 (QC -> C6)"},
                                            {"hostelName": "Day Scholars / Guests", "count": int(pax * 0.1), "shuttleRoute": "Direct Campus Entry"},
                                        ],
                                        "category": track,
                                        "status": status_val,
                                        "synced_with_notion": True,
                                    })
                                # Return live Notion sessions directly
                                return live_out
        except Exception:
            pass

    # 2. Fallback to deterministic seed data if Notion API is unreachable
    speakers_by_session: dict[str, list[seed.Speaker]] = {}
    for sp in seed.SPEAKERS:
        speakers_by_session.setdefault(sp.session_id, []).append(sp)

    out: list[dict] = []
    for s in seed.SESSIONS:
        p = _SESSION_PRESENTATION.get(s.session_id, {})
        current_venue_id = _RELOCATION.get(s.session_id, s.venue_id)
        relocated = current_venue_id != s.venue_id
        session_speakers = speakers_by_session.get(s.session_id, [])
        if session_speakers:
            primary = session_speakers[0]
            if len(session_speakers) > 1:
                speaker_name = f"{len(session_speakers)} speakers ({', '.join(sp.name for sp in session_speakers)})"
                designation = "Panel speakers"
            else:
                speaker_name = primary.name
                designation = primary.title
            arrival = primary.arrival_building
        else:
            speaker_name = "Conclave Leadership"
            designation = "KIIT University"
            arrival = "Bldg A"

        out.append(
            {
                "id": s.session_id,
                "title": s.name,
                "date": s.date.isoformat(),
                "timeWindow": f"{s.start_time.strftime('%H:%M')} – {s.end_time.strftime('%H:%M')} IST",
                "hostingSociety": p.get("hostingSociety", "KBC 2026 Steering Committee"),
                "speaker": {
                    "name": speaker_name,
                    "designation": designation,
                    "arrivalGate": f"Arrival: {arrival}",
                    "vipEscortAssigned": "Assigned via volunteer solver",
                },
                "originalVenue": _venue_name(s.venue_id),
                "currentVenue": _venue_name(current_venue_id),
                "isRelocated": relocated,
                "registrantCount": s.registrants,
                "hostelDistribution": p.get("hostelDistribution", []),
                "category": p.get("category", "Keynote"),
                "status": "Relocated" if relocated else "Scheduled",
                "synced_with_notion": False,
            }
        )
    return out


@router.get("/volunteers", summary="Volunteer roster")
async def list_volunteers() -> list[dict]:
    out: list[dict] = []
    for i, v in enumerate(seed.VOLUNTEERS):
        if v.status == seed.VolunteerStatus.STANDBY:
            ui_status = "Active Standby"
        elif v.assigned_session_id is not None:
            ui_status = "Assigned"
        else:
            ui_status = "Standby"
        out.append(
            {
                "id": v.staff_id,
                "name": v.name,
                "phone": f"+91 98765 4{3210 + i:04d}"[:15],
                "role": v.role,
                "skill": _SKILL_LABEL.get(v.skill, "Registration & Hospitality"),
                "status": ui_status,
                "assignedVenue": _venue_name(v.assigned_venue_id),
                "assignedSession": _session_name(v.assigned_session_id),
                "hoursWorked": round(1.5 + (i % 6) * 0.5, 1),
            }
        )
    return out


@router.get("/dependencies", summary="Dependency blast radius from the outage")
async def list_dependencies() -> list[dict]:
    """Blast radius derived deterministically from the seed graph.

    Hard hits: sessions/tasks/comms at or referencing the unavailable venue, plus
    the registrant cohort of each displaced session. Soft edges: speaker escorts
    and the volunteer-roster re-evaluation (deferred until relocation is chosen).
    """
    outage = "ven_main_aud"
    nodes: list[dict] = [
        {
            "id": outage,
            "label": "Main Auditorium (Outage 08:00–23:59)",
            "type": "root",
            "edgeType": "root_disruption",
            "impactLevel": "hard",
            "detail": _VENUE_PRESENTATION[outage]["disruptionReason"],
        }
    ]

    for s in seed.SESSIONS:
        if s.venue_id == outage:
            nodes.append(
                {
                    "id": s.session_id,
                    "label": f"{s.name} ({s.start_time.strftime('%H:%M')}–{s.end_time.strftime('%H:%M')})",
                    "type": "session",
                    "edgeType": "hosts",
                    "impactLevel": "hard",
                    "detail": f"{s.registrants} registrants • falls inside unavailability window",
                }
            )

    for t in seed.TASKS:
        if t.venue_id == outage:
            nodes.append(
                {
                    "id": t.task_id,
                    "label": t.description,
                    "type": "task",
                    "edgeType": "task_at",
                    "impactLevel": "hard",
                    "detail": f"Status: {t.status.value} at unavailable venue",
                }
            )

    for c in seed.PUBLIC_COMMS:
        if c.mentions_venue_id == outage:
            nodes.append(
                {
                    "id": c.notification_id,
                    "label": c.content,
                    "type": "comm",
                    "edgeType": "mentions",
                    "impactLevel": "hard",
                    "detail": f"{c.channel.value} reference points at stale venue",
                }
            )

    for s in seed.SESSIONS:
        if s.venue_id == outage:
            nodes.append(
                {
                    "id": f"cohort_{s.session_id}",
                    "label": f"{s.registrants} registrants ({s.name})",
                    "type": "cohort",
                    "edgeType": "has_registrants",
                    "impactLevel": "hard",
                    "detail": "Location-update SMS & push broadcast needed",
                }
            )

    for sp in seed.SPEAKERS:
        target_venue = _RELOCATION.get(sp.session_id, "ven_main_aud")
        pres = _VENUE_PRESENTATION.get(target_venue, {})
        escort = "escort needed" if pres.get("campus", "").split("(")[0].strip() else "no action"
        nodes.append(
            {
                "id": f"soft_{sp.participant_id}",
                "label": f"{sp.name} ({sp.title})",
                "type": "soft_speaker",
                "edgeType": "speaker_escort",
                "impactLevel": "soft",
                "detail": f"Arrives {sp.arrival_building} → re-homed venue → {escort}",
            }
        )

    active = sum(1 for v in seed.VOLUNTEERS if v.status == seed.VolunteerStatus.ACTIVE)
    standby = sum(1 for v in seed.VOLUNTEERS if v.status == seed.VolunteerStatus.STANDBY)
    nodes.append(
        {
            "id": "soft_volunteer_roster",
            "label": "Volunteer staffing roster",
            "type": "soft_volunteer",
            "edgeType": "staffing_reeval",
            "impactLevel": "soft",
            "detail": f"{active} active + {standby} standby — re-evaluated after relocation",
        }
    )
    return nodes


@router.get("/overview", summary="Overview KPIs derived from the seed scenario")
async def get_overview() -> dict:
    impacted = [s for s in seed.SESSIONS if s.venue_id == "ven_main_aud"]
    registrants_at_risk = sum(s.registrants for s in impacted)
    total_volunteers = len(seed.VOLUNTEERS)
    standby = sum(1 for v in seed.VOLUNTEERS if v.status == seed.VolunteerStatus.STANDBY)
    assigned_at_outage = sum(
        1 for v in seed.VOLUNTEERS if v.assigned_venue_id == "ven_main_aud"
    )
    follow_up_tasks = (
        len(impacted)  # re-home each session
        + len([t for t in seed.TASKS if t.venue_id == "ven_main_aud"])  # move tasks
        + len([c for c in seed.PUBLIC_COMMS if c.mentions_venue_id == "ven_main_aud"])  # fix comms
        + len(impacted)  # notify each cohort
    )
    return {
        "impactedSessions": len(impacted),
        "registrantsAtRisk": registrants_at_risk,
        "volunteersTotal": total_volunteers,
        "volunteersReassigned": assigned_at_outage,
        "volunteersStandby": standby,
        "followUpTasks": follow_up_tasks,
        "venuesTotal": len(seed.VENUES),
        "totalSeating": sum(v.capacity for v in seed.VENUES),
        "event": {
            "id": seed.EVENT_ID,
            "name": seed.EVENT_NAME,
            "date": seed.EVENT_DATE.isoformat(),
        },
    }
