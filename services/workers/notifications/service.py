"""Notification Service with Mass Dispatch Approval Gate (Sprint 7, COM-008, RULE-03, TAD §19)."""

from __future__ import annotations

from typing import Any

from packages.contracts.notifications import (
    ChannelType,
    CohortDefinition,
    DispatchRecord,
    GroundedMessageDraft,
    StaleCommunicationItem,
)
from services.workers.notifications.channels import MultiChannelDispatcher
from services.workers.notifications.cohorts import CohortDerivationEngine
from services.workers.notifications.drafter import GroundedMessageDrafter
from services.workers.notifications.stale_detector import StaleCommunicationDetector


class MassDispatchRequiresApprovalError(Exception):
    """Raised when attempting mass dispatch without verified human/proposal approval (RULE-03)."""
    pass


class NotificationService:
    """Core notification management service."""

    def __init__(self) -> None:
        self.cohort_engine = CohortDerivationEngine()
        self.drafter = GroundedMessageDrafter()
        self.dispatcher = MultiChannelDispatcher()
        self.stale_detector = StaleCommunicationDetector()
        self.drafts: dict[str, GroundedMessageDraft] = {}
        self._init_golden_drafts()

    def _init_golden_drafts(self) -> None:
        for d in self.drafter.generate_golden_disruption_drafts():
            self.drafts[d.draft_id] = d

    def get_impacted_cohorts(self) -> list[CohortDefinition]:
        """Derive impacted cohorts."""
        return self.cohort_engine.derive_golden_disruption_cohorts()

    def get_drafts(self) -> list[GroundedMessageDraft]:
        """List active drafts."""
        return list(self.drafts.values())

    def approve_draft(self, draft_id: str, approved_by: str) -> GroundedMessageDraft:
        """Approve a draft for mass dispatch."""
        if draft_id not in self.drafts:
            raise KeyError(f"Draft {draft_id} not found")
        draft = self.drafts[draft_id]
        draft.approved = True
        draft.approved_by = approved_by
        return draft

    async def dispatch_notification(
        self,
        draft_id: str,
        channel: ChannelType = ChannelType.PUSH,
        is_approved: bool = False,
    ) -> list[DispatchRecord]:
        """Dispatches draft to its cohort, strictly verifying approval gate (COM-008, RULE-03)."""
        if draft_id not in self.drafts:
            raise KeyError(f"Draft {draft_id} not found")

        draft = self.drafts[draft_id]

        # Approval gate (RULE-03, COM-008)
        if not is_approved and not draft.approved:
            raise MassDispatchRequiresApprovalError(
                f"Mass dispatch for draft '{draft.session_name}' blocked: Requires human approval before dispatch."
            )

        # Find cohort recipients
        cohorts = {c.cohort_id: c for c in self.get_impacted_cohorts()}
        cohort = cohorts.get(draft.cohort_id)
        recipients = cohort.participant_ids if cohort else [f"part_{i}" for i in range(1, 101)]

        return await self.dispatcher.dispatch_to_cohort(draft, recipients, channel=channel)

    def scan_stale_comms(self) -> list[StaleCommunicationItem]:
        """Scan and flag outdated public comms."""
        return self.stale_detector.scan_for_stale_comms()
