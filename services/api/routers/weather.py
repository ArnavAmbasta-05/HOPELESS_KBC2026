"""Weather Resilience API Router (Sprint 9, WX-001..009, AT-02, TAD §17)."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from packages.contracts.weather import (
    WeatherBranchProposal,
    WeatherSignal,
    WeatherThresholdConfig,
)
from services.workers.weather.service import WeatherService

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])
weather_service = WeatherService()


class IMDIngestRequest(BaseModel):
    rainfall_mm_1hr: float = 0.0
    lightning_probability: int = 0
    wind_gust_kmh: float = 0.0
    temperature_c: float = 32.0
    zone: str = "campus_6_oat"
    confidence: float = 0.94


class OpenMeteoIngestRequest(BaseModel):
    zone: str = "campus_6_oat"
    precipitation: float = 0.0
    wind_speed_10m: float = 0.0
    temperature_2m: float = 30.0
    cape_lightning_index: int = 0


class GenerateWeatherBranchRequest(BaseModel):
    parent_plan_id: str = "prop_kbc_disruption_001"
    disrupted_outdoor_venue_id: str = "ven_campus_6_oat"
    signal: WeatherSignal
    sessions_at_risk: list[dict[str, Any]] = Field(default_factory=list)
    backup_indoor_venues: list[dict[str, Any]] = Field(default_factory=list)


@router.get("/live-bhubaneswar", response_model=WeatherSignal)
async def get_live_bhubaneswar_weather() -> WeatherSignal:
    """Fetches real-time live satellite weather telemetry for KIIT Campus 6 (Patia, Bhubaneswar)."""
    return await weather_service.fetch_live_bhubaneswar_weather()


@router.post("/ingest/imd", response_model=WeatherSignal)
async def ingest_imd_feed(req: IMDIngestRequest) -> WeatherSignal:
    """Ingests and normalizes an IMD Met Centre Bhubaneswar weather update (WX-003)."""
    return weather_service.normalize_imd_feed(req.model_dump())


@router.post("/ingest/openmeteo", response_model=WeatherSignal)
async def ingest_openmeteo_feed(req: OpenMeteoIngestRequest) -> WeatherSignal:
    """Ingests and normalizes an Open-Meteo weather update (WX-003)."""
    return weather_service.normalize_openmeteo_feed(req.model_dump())


@router.get("/signals", response_model=list[WeatherSignal])
async def list_active_signals(limit: int = Query(default=20, ge=1, le=100)) -> list[WeatherSignal]:
    """Lists recent weather signals."""
    return weather_service.active_signals[-limit:]


@router.post("/branch", response_model=WeatherBranchProposal)
async def generate_weather_branch(req: GenerateWeatherBranchRequest) -> WeatherBranchProposal:
    """Generates a secondary weather simulation branch for outdoor disruptions (WX-006, AT-02)."""
    return weather_service.generate_weather_branch(
        parent_plan_id=req.parent_plan_id,
        disrupted_outdoor_venue_id=req.disrupted_outdoor_venue_id,
        signal=req.signal,
        sessions_at_risk=req.sessions_at_risk,
        backup_indoor_venues=req.backup_indoor_venues,
    )


@router.get("/branches", response_model=list[WeatherBranchProposal])
async def list_branches() -> list[WeatherBranchProposal]:
    """Lists generated weather simulation branches."""
    return weather_service.generated_branches
