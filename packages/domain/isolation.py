"""Multi-Tenant & Multi-Event Isolation Enforcer (Sprint 9, BR-018, TAD §13)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("korex.isolation")


class MultiEventIsolationError(Exception):
    """Raised when an operation attempts to access data outside authorized tenant/event scope."""
    pass


class EventContext:
    """Carries tenant and event execution scope for isolation verification."""

    def __init__(self, tenant_id: str = "kiit_fest_ops", event_id: str | None = None) -> None:
        self.tenant_id = tenant_id
        self.event_id = event_id

    def validate_access(self, target_tenant_id: str, target_event_id: str | None = None) -> None:
        """Validates that current context has authority to access target resource."""
        if self.tenant_id != target_tenant_id:
            logger.error("Tenant isolation breach attempted: context=%s, target=%s", self.tenant_id, target_tenant_id)
            raise MultiEventIsolationError(
                f"Cross-tenant access forbidden: {self.tenant_id} cannot access {target_tenant_id}"
            )

        if target_event_id is not None and self.event_id is not None and self.event_id != target_event_id:
            logger.error("Multi-event boundary breach attempted: context=%s, target=%s", self.event_id, target_event_id)
            raise MultiEventIsolationError(
                f"Cross-event access forbidden: event {self.event_id} cannot access event {target_event_id}"
            )

    def filter_records(self, records: list[dict[str, Any]], event_id_key: str = "event_id") -> list[dict[str, Any]]:
        """Filters a record collection strictly by active tenant and event context."""
        filtered = []
        for r in records:
            r_tenant = r.get("tenant_id", "kiit_fest_ops")
            r_event = r.get(event_id_key)

            if r_tenant != self.tenant_id:
                continue

            if self.event_id is not None and r_event is not None and r_event != self.event_id:
                continue

            filtered.append(r)
        return filtered
