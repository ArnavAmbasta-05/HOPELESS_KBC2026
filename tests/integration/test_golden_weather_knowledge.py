"""Integration Tests for Sprint 9: Weather Resilience, Chained OAT Storm, RAG Knowledge & Isolation (AT-02, AT-10, TAD §13, §17)."""

import pytest
from fastapi.testclient import TestClient

from packages.contracts.knowledge import (
    DocumentSourceType,
    KnowledgeItem,
    PostEventReport,
    RAGQuery,
)
from packages.contracts.weather import (
    WeatherAlertLevel,
    WeatherHazardType,
    WeatherSignal,
    WeatherThresholdConfig,
)
from packages.domain.isolation import EventContext, MultiEventIsolationError
from services.api.main import app
from services.workers.rag.service import RAGKnowledgeService
from services.workers.weather.service import WeatherService


@pytest.fixture
def weather_svc() -> WeatherService:
    return WeatherService()


@pytest.fixture
def rag_svc() -> RAGKnowledgeService:
    return RAGKnowledgeService()


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Weather Ingestion & Chained OAT Disruption (AT-02, WX-001..009)
# ---------------------------------------------------------------------------

def test_imd_feed_normalization_and_hazard_thresholds(weather_svc: WeatherService):
    """Verifies IMD feed normalization and severe lightning/rain hazard detection."""
    imd_payload = {
        "rainfall_mm_1hr": 28.5,
        "lightning_probability": 85,
        "wind_gust_kmh": 45.0,
        "temperature_c": 29.5,
        "zone": "campus_6_oat",
        "confidence": 0.95,
    }

    signal = weather_svc.normalize_imd_feed(imd_payload)
    assert signal.source == "IMD_BHUBANESWAR"
    assert signal.zone == "campus_6_oat"
    assert signal.hazard_type == WeatherHazardType.LIGHTNING
    assert signal.alert_level == WeatherAlertLevel.RED
    assert signal.precipitation_mm_per_hr == 28.5
    assert signal.lightning_probability_pct == 85
    assert signal.confidence_score == 0.95

    needs_reloc, desc = weather_svc.evaluate_hazard(signal)
    assert needs_reloc is True
    assert "LIGHTNING hazard detected" in desc


def test_openmeteo_feed_normalization(weather_svc: WeatherService):
    """Verifies Open-Meteo normalization for moderate rain conditions."""
    om_payload = {
        "zone": "campus_6_sports_complex",
        "current": {
            "precipitation": 8.0,
            "wind_speed_10m": 18.0,
            "temperature_2m": 31.0,
            "cape_lightning_index": 20,
        },
    }

    signal = weather_svc.normalize_openmeteo_feed(om_payload)
    assert signal.source == "OPEN_METEO"
    assert signal.zone == "campus_6_sports_complex"
    assert signal.alert_level == WeatherAlertLevel.ORANGE
    assert signal.hazard_type == WeatherHazardType.RAIN


def test_chained_oat_storm_branch_generation(weather_svc: WeatherService):
    """Validates AT-02: After Main Aud outage moves sessions to OAT, an afternoon storm triggers a secondary branch."""
    # Sessions previously relocated to OAT via plan prop_kbc_disruption_001
    sessions_in_oat = [
        {"session_id": "sess_kbc_keynote_001", "title": "Opening Keynote", "venue_id": "ven_campus_6_oat"},
        {"session_id": "sess_kbc_ai_panel_002", "title": "Future of AI Panel", "venue_id": "ven_campus_6_oat"},
    ]

    backup_venues = [
        {"venue_id": "ven_multipurpose_hall_c6", "name": "Campus 6 Multipurpose Hall"},
        {"venue_id": "ven_campus_7_auditorium", "name": "Campus 7 Auditorium"},
    ]

    storm_signal = WeatherSignal(
        source="IMD_BHUBANESWAR",
        zone="campus_6_oat",
        hazard_type=WeatherHazardType.LIGHTNING,
        alert_level=WeatherAlertLevel.RED,
        precipitation_mm_per_hr=25.0,
        lightning_probability_pct=90,
        confidence_score=0.92,
    )

    branch = weather_svc.generate_weather_branch(
        parent_plan_id="prop_kbc_disruption_001",
        disrupted_outdoor_venue_id="ven_campus_6_oat",
        signal=storm_signal,
        sessions_at_risk=sessions_in_oat,
        backup_indoor_venues=backup_venues,
    )

    assert branch.parent_plan_id == "prop_kbc_disruption_001"
    assert branch.disrupted_outdoor_venue_id == "ven_campus_6_oat"
    assert branch.mitigation_action == "INDOOR_RELOCATION"
    assert branch.uncertainty_level == "LOW"
    assert len(branch.relocated_sessions) == 2
    assert branch.relocated_sessions[0]["new_venue_id"] == "ven_multipurpose_hall_c6"
    assert branch.relocated_sessions[1]["new_venue_id"] == "ven_campus_7_auditorium"


# ---------------------------------------------------------------------------
# RAG Grounded Retrieval & Scoped Isolation (RULE-10, TAD §13)
# ---------------------------------------------------------------------------

def test_rag_global_sop_retrieval_with_citations(rag_svc: RAGKnowledgeService):
    """Verifies retrieval of global SOPs with grounded citations and non-authoritative flag."""
    query = RAGQuery(
        query="What is the protocol for weather evacuation at Open Air Theatre?",
        tenant_id="kiit_fest_ops",
        include_global_sops=True,
    )
    res = rag_svc.query(query)

    assert res.is_guidance_only is True
    assert len(res.citations) > 0
    assert any("Weather Evacuation Protocol" in c.source_title for c in res.citations)
    assert res.confidence >= 0.8


def test_rag_multi_event_isolation_and_cross_event_protection(rag_svc: RAGKnowledgeService):
    """Verifies that private event logs cannot leak across event boundaries (BR-018)."""
    # Ingest private incident log for Event Alpha
    rag_svc.ingest_document(
        document_id="doc_alpha_private_001",
        title="Event Alpha Confidential VIP Security Incident",
        source_type=DocumentSourceType.INCIDENT_LOG,
        content="Confidential VIP escort protocol failure in Campus 6 green room.",
        tenant_id="kiit_fest_ops",
        event_id="event_alpha_2026",
    )

    # Query scoped to Event Beta (should NOT see Event Alpha doc)
    query_beta = RAGQuery(
        query="Confidential VIP escort protocol failure",
        tenant_id="kiit_fest_ops",
        event_id="event_beta_2026",
        include_global_sops=False,
    )
    res_beta = rag_svc.query(query_beta)
    assert len(res_beta.citations) == 0

    # Query scoped to Event Alpha (SHOULD see the doc)
    query_alpha = RAGQuery(
        query="Confidential VIP escort protocol failure",
        tenant_id="kiit_fest_ops",
        event_id="event_alpha_2026",
        include_global_sops=False,
    )
    res_alpha = rag_svc.query(query_alpha)
    assert len(res_alpha.citations) == 1
    assert res_alpha.citations[0].document_id == "doc_alpha_private_001"


# ---------------------------------------------------------------------------
# Post-Event Report & Institutional Memory (AT-10, FR-KB-001..003)
# ---------------------------------------------------------------------------

def test_post_event_report_synthesis_and_knowledge_item(rag_svc: RAGKnowledgeService):
    """Validates AT-10: Automated synthesis of Post-Event Report and creation of reusable Knowledge Item."""
    telemetry = {
        "total_sessions": 48,
        "completed_sessions": 47,
        "disruptions_count": 2,
        "change_proposals_count": 2,
        "approvals_count": 2,
        "weather_hazards_count": 1,
        "crowd_surges_count": 2,
        "transport_shuttle_trips": 22,
    }

    report = rag_svc.synthesize_post_event_report(
        event_id="evt_kbc_2026",
        event_name="KIIT Fest / KBC 2026",
        telemetry=telemetry,
    )

    assert report.event_id == "evt_kbc_2026"
    assert report.total_sessions == 48
    assert report.completed_sessions == 47
    assert report.key_metrics["completion_rate_pct"] == 97.9
    assert len(report.recommendations) >= 3

    # Verify report is searchable in RAG
    rag_query = RAGQuery(
        query="KIIT Fest KBC 2026 report completions disruptions",
        tenant_id="kiit_fest_ops",
        event_id="evt_kbc_2026",
    )
    rag_res = rag_svc.query(rag_query)
    assert any(c.document_id == report.report_id for c in rag_res.citations)

    # Create reusable KnowledgeItem playbook
    ki = rag_svc.generate_knowledge_item(
        tenant_id="kiit_fest_ops",
        source_event_id="evt_kbc_2026",
        category="WEATHER_RELOCATION",
        title="Double-Disruption Cascading Stage Relocation Playbook",
        problem_statement="Main auditorium grid failure followed by OAT thunderstorm within 90 minutes.",
        resolution_strategy="Pre-reserve tertiary multipurpose hall and stage covering with transport dispatch.",
    )

    assert ki.source_event_id == "evt_kbc_2026"
    assert ki.category == "WEATHER_RELOCATION"
    assert len(rag_svc.knowledge_items) == 1


# ---------------------------------------------------------------------------
# Multi-Event Isolation Enforcer (BR-018)
# ---------------------------------------------------------------------------

def test_event_context_isolation_enforcer():
    """Verifies that EventContext raises MultiEventIsolationError upon breach attempts."""
    ctx_event_1 = EventContext(tenant_id="kiit_fest_ops", event_id="evt_001")

    # Allowed access
    ctx_event_1.validate_access(target_tenant_id="kiit_fest_ops", target_event_id="evt_001")

    # Cross-tenant violation
    with pytest.raises(MultiEventIsolationError):
        ctx_event_1.validate_access(target_tenant_id="other_university_ops", target_event_id="evt_001")

    # Cross-event violation
    with pytest.raises(MultiEventIsolationError):
        ctx_event_1.validate_access(target_tenant_id="kiit_fest_ops", target_event_id="evt_002")

    # Record filtering
    records = [
        {"tenant_id": "kiit_fest_ops", "event_id": "evt_001", "data": "A"},
        {"tenant_id": "kiit_fest_ops", "event_id": "evt_002", "data": "B"},
        {"tenant_id": "other_tenant", "event_id": "evt_001", "data": "C"},
    ]
    filtered = ctx_event_1.filter_records(records)
    assert len(filtered) == 1
    assert filtered[0]["data"] == "A"


# ---------------------------------------------------------------------------
# Weather & Knowledge HTTP API Endpoints
# ---------------------------------------------------------------------------

def test_weather_and_knowledge_http_apis(api_client: TestClient):
    """Verifies FastAPI endpoints for weather ingestion, branch proposals, and RAG knowledge."""
    # 1. Weather Ingest IMD
    resp_imd = api_client.post(
        "/weather/ingest/imd",
        json={
            "rainfall_mm_1hr": 30.0,
            "lightning_probability": 80,
            "wind_gust_kmh": 42.0,
            "temperature_c": 31.0,
            "zone": "campus_6_oat",
            "confidence": 0.96,
        },
    )
    assert resp_imd.status_code == 200
    signal_data = resp_imd.json()
    assert signal_data["alert_level"] == "red"

    # 2. Weather Branch Proposal API
    resp_branch = api_client.post(
        "/weather/branch",
        json={
            "parent_plan_id": "prop_kbc_disruption_001",
            "disrupted_outdoor_venue_id": "ven_campus_6_oat",
            "signal": signal_data,
            "sessions_at_risk": [{"session_id": "sess_01", "title": "AI Keynote"}],
            "backup_indoor_venues": [{"venue_id": "ven_multipurpose_hall_c6"}],
        },
    )
    assert resp_branch.status_code == 200
    branch_data = resp_branch.json()
    assert branch_data["mitigation_action"] == "INDOOR_RELOCATION"
    assert len(branch_data["relocated_sessions"]) == 1

    # 3. Knowledge Query API
    resp_rag = api_client.post(
        "/knowledge/query",
        json={
            "query": "Main Auditorium power outage protocol DG switchover",
            "tenant_id": "kiit_fest_ops",
            "include_global_sops": True,
            "top_k": 3,
        },
    )
    assert resp_rag.status_code == 200
    rag_data = resp_rag.json()
    assert rag_data["is_guidance_only"] is True
    assert len(rag_data["citations"]) > 0

    # 4. Post-Event Report API
    resp_rep = api_client.post(
        "/knowledge/post-event-report",
        json={
            "event_id": "evt_kbc_2026",
            "event_name": "KIIT EventOps 2026",
            "telemetry": {"total_sessions": 30, "completed_sessions": 30},
        },
    )
    assert resp_rep.status_code == 200
    assert resp_rep.json()["event_id"] == "evt_kbc_2026"

    # 5. Create & List Knowledge Item API
    resp_ki_create = api_client.post(
        "/knowledge/items",
        json={
            "tenant_id": "kiit_fest_ops",
            "source_event_id": "evt_kbc_2026",
            "category": "TRANSPORT_DISPATCH",
            "title": "Surge Shuttle Pre-positioning",
            "problem_statement": "Post-session crowd exodus creates bottleneck at Gate 3.",
            "resolution_strategy": "Dispatch 3 electric shuttles to Gate 3 at T-10 min.",
            "tags": ["transport", "crowd"],
        },
    )
    assert resp_ki_create.status_code == 200
    assert resp_ki_create.json()["category"] == "TRANSPORT_DISPATCH"

    resp_ki_list = api_client.get("/knowledge/items")
    assert resp_ki_list.status_code == 200
    assert len(resp_ki_list.json()) >= 1
