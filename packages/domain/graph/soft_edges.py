"""Soft Edge Re-Evaluation Module (S2-T3, FR-GRAPH-005).

Re-evaluates deferred soft edges (speakers, staffing) after primary venue
and schedule resolution is proposed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packages.domain.seed import GoldenSeed, load_golden_seed


@dataclass(frozen=True)
class SpeakerEvaluationResult:
    speaker_id: str
    name: str
    session_id: str
    session_name: str
    arrival_building: str
    new_venue_name: str
    new_venue_building: str
    escort_needed: bool
    action_note: str


@dataclass(frozen=True)
class VolunteerEvaluationResult:
    staff_id: str
    name: str
    role: str
    action: str
    assigned_session: str | None
    assigned_venue: str | None
    note: str


def reevaluate_speakers_after_venue_resolution(
    venue_resolutions: dict[str, str],
    seed: GoldenSeed | None = None,
) -> list[SpeakerEvaluationResult]:
    """Re-evaluate speaker escort requirements based on new venue assignments.

    Args:
        venue_resolutions: Mapping of session_name -> new_venue_name.
        seed: Golden seed data (defaults to standard seed).

    Returns:
        List of SpeakerEvaluationResult indicating if escort is required.
    """
    if seed is None:
        seed = load_golden_seed()

    venue_building_map = {v.name: v.building for v in seed.venues}
    session_map = {s.session_id: s for s in seed.sessions}

    results: list[SpeakerEvaluationResult] = []
    for spk in seed.speakers:
        session = session_map.get(spk.session_id)
        session_name = session.name if session else spk.session_id
        new_venue = venue_resolutions.get(session_name, "Main Auditorium")
        new_venue_bldg = venue_building_map.get(new_venue, "Bldg A")

        escort_needed = spk.arrival_building != new_venue_bldg
        action_note = (
            f"Escort needed: arrives at {spk.arrival_building}, session moved to {new_venue} ({new_venue_bldg})"
            if escort_needed
            else f"No action needed: arrival building {spk.arrival_building} matches {new_venue} ({new_venue_bldg})"
        )

        results.append(
            SpeakerEvaluationResult(
                speaker_id=spk.participant_id,
                name=spk.name,
                session_id=spk.session_id,
                session_name=session_name,
                arrival_building=spk.arrival_building,
                new_venue_name=new_venue,
                new_venue_building=new_venue_bldg,
                escort_needed=escort_needed,
                action_note=action_note,
            )
        )

    return results
