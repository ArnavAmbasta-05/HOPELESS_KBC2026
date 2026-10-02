"""Weather Resilience & Monitoring Contracts (Sprint 9, WX-001..009, AT-02, TAD §17)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class WeatherHazardType(StrEnum):
    RAIN = "rain"
    LIGHTNING = "lightning"
    WIND = "wind"
    EXTREME_HEAT = "extreme_heat"
    CLEAR = "clear"


class WeatherAlertLevel(StrEnum):
    GREEN = "green"    # Safe
    YELLOW = "yellow"  # Advisory / Monitor
    ORANGE = "orange"  # Warning / Prepare
    RED = "red"        # Immediate Hazard / Relocate


class WeatherSignal(BaseModel):
    """Normalized weather forecast/nowcast signal (WX-003)."""
    signal_id: str = Field(default_factory=lambda: f"wsig_{uuid.uuid4().hex[:8]}")
    source: str = "IMD_BHUBANESWAR"  # IMD_BHUBANESWAR, OPEN_METEO
    zone: str = "campus_6_oat"
    hazard_type: WeatherHazardType
    alert_level: WeatherAlertLevel
    precipitation_mm_per_hr: float = 0.0
    lightning_probability_pct: int = 0
    wind_speed_kmh: float = 0.0
    temperature_celsius: float = 32.0
    confidence_score: float = 0.92  # 0.0 to 1.0 (WX-007)
    issued_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_until: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_fresh: bool = True


class WeatherThresholdConfig(BaseModel):
    """Configurable weather hazard thresholds (WX-004)."""
    rain_warning_mm: float = 5.0
    rain_surge_mm: float = 15.0
    lightning_warning_pct: int = 40
    lightning_relocate_pct: int = 70
    wind_max_kmh: float = 40.0
    heat_index_max_c: float = 42.0


class WeatherBranchProposal(BaseModel):
    """Simulation branch generated when outdoor venue faces weather hazards (WX-006/009, AT-02)."""
    branch_id: str = Field(default_factory=lambda: f"br_wx_{uuid.uuid4().hex[:8]}")
    parent_plan_id: str = "prop_kbc_disruption_001"
    disrupted_outdoor_venue_id: str
    hazard_description: str
    uncertainty_level: str  # LOW, MODERATE, HIGH
    confidence_score: float
    relocated_sessions: list[dict[str, Any]] = Field(default_factory=list)
    mitigation_action: str  # INDOOR_RELOCATION, TIME_SHIFT, STAGE_COVER
    status: str = "PROPOSED_BRANCH"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
