"""Multi-Channel Notification Dispatcher & Adapters (Sprint 7, S7-T2, COM-005/006, TAD §19).

Provides channel abstraction:
- Email, SMS, Push, WhatsApp adapters
- Idempotency key per dispatch (change_id + cohort_id + recipient_id)
- Deduplication of notifications
- Delivery status tracking (SENT, DELIVERED, FAILED)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from packages.contracts.notifications import ChannelType, DeliveryStatus, DispatchRecord, GroundedMessageDraft


class ChannelAdapter:
    """Base channel adapter."""

    def __init__(self, channel_type: ChannelType) -> None:
        self.channel_type = channel_type

    async def send(self, recipient_id: str, message: str) -> bool:
        """Send message via channel (simulated delivery)."""
        return True


class MultiChannelDispatcher:
    """Orchestrates dispatches across Email, SMS, Push, and WhatsApp with deduplication."""

    def __init__(self) -> None:
        self.adapters = {
            ChannelType.EMAIL: ChannelAdapter(ChannelType.EMAIL),
            ChannelType.SMS: ChannelAdapter(ChannelType.SMS),
            ChannelType.PUSH: ChannelAdapter(ChannelType.PUSH),
            ChannelType.WHATSAPP: ChannelAdapter(ChannelType.WHATSAPP),
        }
        self.sent_idempotency_keys: set[str] = set()
        self.dispatch_log: list[DispatchRecord] = []

    async def dispatch_to_cohort(
        self,
        draft: GroundedMessageDraft,
        recipient_ids: list[str],
        channel: ChannelType = ChannelType.PUSH,
    ) -> list[DispatchRecord]:
        """Dispatch grounded draft to recipients with deduplication and delivery tracking."""
        records: list[DispatchRecord] = []
        adapter = self.adapters.get(channel, self.adapters[ChannelType.PUSH])

        for r_id in recipient_ids:
            idem_key = f"idem_notif_{draft.draft_id}_{r_id}_{channel.value}"

            # Dedup check (COM-005)
            if idem_key in self.sent_idempotency_keys:
                continue

            self.sent_idempotency_keys.add(idem_key)
            now = datetime.now(timezone.utc).isoformat()

            # Execute send
            success = await adapter.send(r_id, draft.message_text)

            record = DispatchRecord(
                draft_id=draft.draft_id,
                cohort_id=draft.cohort_id,
                channel=channel,
                recipient_id=r_id,
                status=DeliveryStatus.DELIVERED if success else DeliveryStatus.FAILED,
                idempotency_key=idem_key,
                sent_at=now,
                delivered_at=now if success else None,
            )
            records.append(record)
            self.dispatch_log.append(record)

        return records

    def get_delivery_metrics(self) -> dict[str, Any]:
        """Summary of delivery status across all dispatches."""
        total = len(self.dispatch_log)
        delivered = sum(1 for r in self.dispatch_log if r.status == DeliveryStatus.DELIVERED)
        failed = sum(1 for r in self.dispatch_log if r.status == DeliveryStatus.FAILED)
        return {
            "total_dispatched": total,
            "delivered_count": delivered,
            "failed_count": failed,
            "delivery_rate": (delivered / total * 100.0) if total > 0 else 100.0,
        }
