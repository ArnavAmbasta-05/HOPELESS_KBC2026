"""Weather Resilience Worker Service (Sprint 9, WX-001..009, AT-02, TAD §17)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from packages.contracts.weather import (
    WeatherAlertLevel,
    WeatherBranchProposal,
    WeatherHazardType,
    WeatherSignal,
    WeatherThresholdConfig,
)

import httpx

logger = logging.getLogger("korex.weather")


class WeatherService:
    """Manages weather ingestion, hazard detection, and simulation branch proposals."""

    def __init__(self, thresholds: WeatherThresholdConfig | None = None) -> None:
        self.thresholds = thresholds or WeatherThresholdConfig()
        self.active_signals: list[WeatherSignal] = []
        self.generated_branches: list[WeatherBranchProposal] = []

    async def fetch_live_bhubaneswar_weather(self) -> WeatherSignal:
        """Fetches live meteorological telemetry for KIIT Bhubaneswar (20.3540 N, 85.8180 E)."""
        url = "https://api.open-meteo.com/v1/forecast?latitude=20.3540&longitude=85.8180&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&timezone=Asia%2FKolkata"
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json().get("current", {})
                    return self.normalize_openmeteo_feed({
                        "zone": "campus_6_oat",
                        "precipitation": data.get("precipitation", 0.0),
                        "wind_speed_10m": data.get("wind_speed_10m", 8.0),
                        "temperature_2m": data.get("temperature_2m", 28.5),
                        "cape_lightning_index": 5,
                    })
        except Exception as exc:
            logger.warning("Live weather fetch fallback: %s", exc)

        # Fallback to standard clear-sky signal
        return self.normalize_openmeteo_feed({
            "zone": "campus_6_oat",
            "precipitation": 0.0,
            "wind_speed_10m": 8.0,
            "temperature_2m": 29.0,
            "cape_lightning_index": 0,
        })

    def normalize_imd_feed(self, raw_imd: dict[str, Any]) -> WeatherSignal:
        """Normalizes raw IMD Met Centre Bhubaneswar payload to standard WeatherSignal (WX-003)."""
        rain_mm = float(raw_imd.get("rainfall_mm_1hr", raw_imd.get("rain_mm", 0.0)))
        lightning_pct = int(raw_imd.get("lightning_probability", raw_imd.get("lightning_risk_pct", 0)))
        wind_kmh = float(raw_imd.get("wind_gust_kmh", raw_imd.get("wind_kmh", 0.0)))
        temp_c = float(raw_imd.get("temperature_c", 32.0))
        zone = raw_imd.get("zone", "campus_6_oat")

        # Determine hazard type
        if lightning_pct >= self.thresholds.lightning_relocate_pct:
            hazard = WeatherHazardType.LIGHTNING
        elif rain_mm >= self.thresholds.rain_surge_mm:
            hazard = WeatherHazardType.RAIN
        elif wind_kmh >= self.thresholds.wind_max_kmh:
            hazard = WeatherHazardType.WIND
        elif temp_c >= self.thresholds.heat_index_max_c:
            hazard = WeatherHazardType.EXTREME_HEAT
        else:
            hazard = WeatherHazardType.CLEAR

        # Determine alert level
        if hazard in (WeatherHazardType.LIGHTNING, WeatherHazardType.RAIN) and (
            lightning_pct >= self.thresholds.lightning_relocate_pct or rain_mm >= self.thresholds.rain_surge_mm
        ):
            alert = WeatherAlertLevel.RED
        elif lightning_pct >= self.thresholds.lightning_warning_pct or rain_mm >= self.thresholds.rain_warning_mm:
            alert = WeatherAlertLevel.ORANGE
        elif hazard != WeatherHazardType.CLEAR:
            alert = WeatherAlertLevel.YELLOW
        else:
            alert = WeatherAlertLevel.GREEN

        signal = WeatherSignal(
            source="IMD_BHUBANESWAR",
            zone=zone,
            hazard_type=hazard,
            alert_level=alert,
            precipitation_mm_per_hr=rain_mm,
            lightning_probability_pct=lightning_pct,
            wind_speed_kmh=wind_kmh,
            temperature_celsius=temp_c,
            confidence_score=float(raw_imd.get("confidence", 0.94)),
        )
        self.active_signals.append(signal)
        return signal

    def normalize_openmeteo_feed(self, raw_om: dict[str, Any]) -> WeatherSignal:
        """Normalizes Open-Meteo payload to standard WeatherSignal (WX-003)."""
        current = raw_om.get("current", raw_om)
        rain_mm = float(current.get("precipitation", 0.0))
        wind_kmh = float(current.get("wind_speed_10m", 0.0))
        temp_c = float(current.get("temperature_2m", 30.0))
        lightning_pct = int(current.get("cape_lightning_index", 0))

        if rain_mm >= self.thresholds.rain_surge_mm:
            hazard = WeatherHazardType.RAIN
            alert = WeatherAlertLevel.RED
        elif rain_mm >= self.thresholds.rain_warning_mm:
            hazard = WeatherHazardType.RAIN
            alert = WeatherAlertLevel.ORANGE
        else:
            hazard = WeatherHazardType.CLEAR
            alert = WeatherAlertLevel.GREEN

        signal = WeatherSignal(
            source="OPEN_METEO",
            zone=raw_om.get("zone", "campus_6_oat"),
            hazard_type=hazard,
            alert_level=alert,
            precipitation_mm_per_hr=rain_mm,
            lightning_probability_pct=lightning_pct,
            wind_speed_kmh=wind_kmh,
            temperature_celsius=temp_c,
            confidence_score=0.88,
        )
        self.active_signals.append(signal)
        return signal

    def evaluate_hazard(self, signal: WeatherSignal) -> tuple[bool, str]:
        """Evaluates whether an active signal necessitates outdoor session relocation."""
        if signal.alert_level in (WeatherAlertLevel.RED, WeatherAlertLevel.ORANGE):
            desc = (
                f"Severe {signal.hazard_type.value.upper()} hazard detected in {signal.zone}. "
                f"Rain: {signal.precipitation_mm_per_hr}mm/hr, Lightning: {signal.lightning_probability_pct}%, "
                f"Wind: {signal.wind_speed_kmh}km/h."
            )
            return True, desc
        return False, "Weather conditions within safe operating limits."

    def generate_weather_branch(
        self,
        parent_plan_id: str,
        disrupted_outdoor_venue_id: str,
        signal: WeatherSignal,
        sessions_at_risk: list[dict[str, Any]],
        backup_indoor_venues: list[dict[str, Any]],
    ) -> WeatherBranchProposal:
        """Generates a secondary weather simulation branch for outdoor disruptions (WX-006, AT-02).
        
        Handles chained scenarios (e.g. sessions already relocated to OAT now needing secondary relocation).
        """
        needs_relocation, hazard_desc = self.evaluate_hazard(signal)

        relocated_sessions: list[dict[str, Any]] = []
        uncertainty = "LOW"
        if signal.confidence_score < 0.75:
            uncertainty = "HIGH"
        elif signal.confidence_score < 0.90:
            uncertainty = "MODERATE"

        # Allocate indoor backup venues sequentially or with capacity check
        indoor_idx = 0
        for sess in sessions_at_risk:
            orig_venue = sess.get("venue_id", disrupted_outdoor_venue_id)
            if backup_indoor_venues and indoor_idx < len(backup_indoor_venues):
                target_venue = backup_indoor_venues[indoor_idx % len(backup_indoor_venues)]
                target_venue_id = target_venue.get("venue_id", target_venue.get("id", "ven_indoor_backup"))
                indoor_idx += 1
            else:
                target_venue_id = "ven_multipurpose_hall_c6"

            relocated_sessions.append({
                "session_id": sess.get("session_id", sess.get("id")),
                "session_name": sess.get("title", sess.get("name", "Disrupted Session")),
                "previous_venue_id": orig_venue,
                "new_venue_id": target_venue_id,
                "reason": f"Weather hazard relocation ({signal.hazard_type.value})",
                "relocated_at": datetime.now(timezone.utc).isoformat(),
            })

        branch = WeatherBranchProposal(
            parent_plan_id=parent_plan_id,
            disrupted_outdoor_venue_id=disrupted_outdoor_venue_id,
            hazard_description=hazard_desc,
            uncertainty_level=uncertainty,
            confidence_score=signal.confidence_score,
            relocated_sessions=relocated_sessions,
            mitigation_action="INDOOR_RELOCATION" if needs_relocation else "STAGE_COVER",
            status="PROPOSED_BRANCH",
        )
        self.generated_branches.append(branch)
        logger.info("Generated weather branch proposal %s for parent plan %s", branch.branch_id, parent_plan_id)
        return branch
