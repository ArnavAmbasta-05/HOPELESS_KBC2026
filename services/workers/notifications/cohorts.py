"""Cohort Derivation Engine (Sprint 7, S7-T1, COM-001, TAD §19).

Derives audience cohorts from impacted sessions, venues, transport routes, and volunteer roles.
"""

from __future__ import annotations

from packages.contracts.notifications import CohortDefinition


class CohortDerivationEngine:
    """Computes targeted participant cohorts based on operational changes."""

    def derive_golden_disruption_cohorts(self) -> list[CohortDefinition]:
        """Derive the 4 primary session cohorts for the golden Main Auditorium disruption."""
        cohorts = [
            CohortDefinition(
                cohort_id="coh_ses_opening",
                name="Opening Ceremony Attendees",
                target_entity_type="session",
                target_entity_id="ses_opening",
                recipient_count=380,
                participant_ids=[f"part_op_{i:03d}" for i in range(1, 381)],
            ),
            CohortDefinition(
                cohort_id="coh_ses_keynote_ai",
                name="AI in EventOps Keynote Attendees",
                target_entity_type="session",
                target_entity_id="ses_keynote_ai",
                recipient_count=230,
                participant_ids=[f"part_kn_{i:03d}" for i in range(1, 231)],
            ),
            CohortDefinition(
                cohort_id="coh_ses_panel_tech",
                name="Tech Panel Attendees",
                target_entity_type="session",
                target_entity_id="ses_panel_tech",
                recipient_count=180,
                participant_ids=[f"part_pn_{i:03d}" for i in range(1, 181)],
            ),
            CohortDefinition(
                cohort_id="coh_ses_valedictory",
                name="Valedictory & Awards Attendees",
                target_entity_type="session",
                target_entity_id="ses_valedictory",
                recipient_count=390,
                participant_ids=[f"part_val_{i:03d}" for i in range(1, 391)],
            ),
            CohortDefinition(
                cohort_id="coh_volunteers_disrupted",
                name="Disrupted Venue Volunteers",
                target_entity_type="volunteer_role",
                target_entity_id="ven_main_aud",
                recipient_count=5,
                participant_ids=["vol_v01", "vol_v02", "vol_v03", "vol_v04", "vol_v05"],
            ),
        ]
        return cohorts
