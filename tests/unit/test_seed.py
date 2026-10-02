"""Unit tests for synthetic seed data and golden fixture (S0-T6).

Verifies the deterministic seed for KBC 2026 matches all golden scenario constraints
and fixture entities.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from integrations.notion.config import (
    ENTITY_VENUES,
    ENTITY_SESSIONS,
    ENTITY_VOLUNTEERS,
    get_sandbox_notion_config,
)
from packages.domain.seed import (
    EVENT_ID,
    EVENT_NAME,
    VENUES,
    SESSIONS,
    VOLUNTEERS,
    SPEAKERS,
    EQUIPMENT,
    TASKS,
    PUBLIC_COMMS,
    VolunteerStatus,
    load_golden_seed,
)
from tests.fixtures.golden_main_auditorium.expected_values import (
    EXPECTED_HARD_HITS,
    EXPECTED_SOFT_EDGES_DEFERRED,
    EXPECTED_TASKS,
    EXPECTED_REGISTRANT_COHORTS,
    EXPECTED_VENUE_REASSIGNMENTS,
    EXPECTED_VOLUNTEER_CHANGES,
)


class TestGoldenSeedData:
    def test_load_golden_seed_structure(self) -> None:
        seed = load_golden_seed()
        assert seed.event_id == EVENT_ID
        assert seed.event_name == EVENT_NAME
        assert len(seed.venues) == 5
        assert len(seed.sessions) == 4
        assert len(seed.volunteers) == 17
        assert len(seed.speakers) == 5
        assert len(seed.equipment) == 2
        assert len(seed.tasks) == 2
        assert len(seed.public_comms) == 3

    def test_venues_capacities_and_buildings(self) -> None:
        venue_map = {v.name: v for v in VENUES}
        assert "Main Auditorium" in venue_map
        assert venue_map["Main Auditorium"].capacity == 500
        assert venue_map["Main Auditorium"].building == "Bldg A"

        assert "Open Air Theatre" in venue_map
        assert venue_map["Open Air Theatre"].capacity == 600
        assert venue_map["Open Air Theatre"].building == "Bldg C"

        assert "Seminar Hall" in venue_map
        assert venue_map["Seminar Hall"].capacity == 250
        assert venue_map["Seminar Hall"].building == "Bldg B"

        assert "LH-3" in venue_map
        assert venue_map["LH-3"].capacity == 150
        assert venue_map["LH-3"].building == "Bldg D"

        assert "LH-5" in venue_map
        assert venue_map["LH-5"].capacity == 120
        assert venue_map["LH-5"].building == "Bldg D"

    def test_sessions_registrants_and_timing(self) -> None:
        session_map = {s.name: s for s in SESSIONS}
        assert session_map["Opening Ceremony"].registrants == 380
        assert session_map["Keynote: AI in FinTech"].registrants == 230
        assert session_map["Panel: Building Startups"].registrants == 180
        assert session_map["Prize Distribution"].registrants == 390

        # All sessions initially at Main Auditorium
        for s in SESSIONS:
            assert s.venue_id == "ven_main_aud"

    def test_volunteers_standby_and_counts(self) -> None:
        assert len(VOLUNTEERS) == 17
        standby_list = [v for v in VOLUNTEERS if v.status == VolunteerStatus.STANDBY]
        assert len(standby_list) == 1
        assert standby_list[0].name == "Arjun"
        assert standby_list[0].skill == "av"

        vol_names = {v.name for v in VOLUNTEERS}
        for expected in ["Dev", "Kabir", "Tanya", "Meera", "Arjun"]:
            assert expected in vol_names

    def test_speakers_and_arrival_buildings(self) -> None:
        assert len(SPEAKERS) == 5
        spk_map = {s.name: s for s in SPEAKERS}
        assert spk_map["Chief Guest (Vice Chancellor)"].arrival_building == "Bldg A"
        assert spk_map["Dr. Mehra"].arrival_building == "Bldg B"
        assert spk_map["Ankit"].arrival_building == "Bldg B"
        assert spk_map["Priya"].arrival_building == "Bldg B"
        assert spk_map["Ravi"].arrival_building == "Bldg B"

    def test_equipment_and_store_location(self) -> None:
        assert len(EQUIPMENT) == 2
        for eq in EQUIPMENT:
            assert eq.location == "Store"

    def test_pre_existing_tasks(self) -> None:
        assert len(TASKS) == 2
        task_teams = {t.team for t in TASKS}
        assert "tech" in task_teams
        assert "stage" in task_teams

    def test_public_comms(self) -> None:
        assert len(PUBLIC_COMMS) == 3
        channels = {c.channel.value for c in PUBLIC_COMMS}
        assert "instagram" in channels
        assert "printed_board" in channels


class TestGoldenFixtureAndExpectedValues:
    def test_golden_simulation_output_file_exists(self) -> None:
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "golden_main_auditorium"
            / "simulation_output.txt"
        )
        assert fixture_path.exists()
        content = fixture_path.read_text(encoding="utf-8")
        assert "Main Auditorium" in content
        assert "Hard hits" in content or "12" in content

    def test_expected_values_constants(self) -> None:
        assert EXPECTED_HARD_HITS == 12
        assert EXPECTED_SOFT_EDGES_DEFERRED == 7
        assert EXPECTED_TASKS == 17
        assert len(EXPECTED_REGISTRANT_COHORTS) == 4
        assert len(EXPECTED_VENUE_REASSIGNMENTS) == 4
        assert len(EXPECTED_VOLUNTEER_CHANGES) == 5


class TestNotionSandboxConfig:
    def test_sandbox_config_defaults(self) -> None:
        cfg = get_sandbox_notion_config()
        assert cfg.workspace_id == "ws_notion_kbc2026_sandbox"
        assert cfg.token_env_var == "NOTION_API_TOKEN"
        assert ENTITY_VENUES in cfg.database_mappings
        assert ENTITY_SESSIONS in cfg.database_mappings
        assert ENTITY_VOLUNTEERS in cfg.database_mappings
