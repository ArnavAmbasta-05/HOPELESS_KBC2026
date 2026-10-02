"""Notion Dead-Letter Queue (DLQ) & Operator Incident Manager (Sprint 6, S6-T5, TAD §14).

Records failed outbound writes, isolates unrecoverable payloads, and raises operator-visible
integration incident records for the Command Center.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

from packages.contracts.notion import NotionWriteOperation


class DLQEntry(BaseModel):
    """Dead-letter queue item representing an unrecoverable Notion write."""
    dlq_id: str = Field(default_factory=lambda: f"dlq_{uuid.uuid4().hex[:8]}")
    plan_id: str
    operation: NotionWriteOperation
    error_message: str
    attempt_count: int
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "PENDING"  # PENDING, RESOLVED, IGNORED


class NotionIntegrationIncident(BaseModel):
    """Operator-visible integration incident raised when writes fail."""
    incident_id: str = Field(default_factory=lambda: f"inc_notion_{uuid.uuid4().hex[:8]}")
    event_id: str
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    failed_operations_count: int
    dlq_ids: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NotionDLQManager:
    """Manages Dead-Letter Queue records and incident alerts."""

    def __init__(self) -> None:
        self.dlq_records: dict[str, DLQEntry] = {}
        self.incidents: list[NotionIntegrationIncident] = []

    def record_failure(
        self,
        plan_id: str,
        operation: NotionWriteOperation,
        error_message: str,
        attempt_count: int = 3,
        event_id: str = "evt_kbc2026",
    ) -> DLQEntry:
        """Enqueue failed write operation into DLQ and create/update incident."""
        entry = DLQEntry(
            plan_id=plan_id,
            operation=operation,
            error_message=error_message,
            attempt_count=attempt_count,
        )
        self.dlq_records[entry.dlq_id] = entry

        # Create operator incident
        incident = NotionIntegrationIncident(
            event_id=event_id,
            title=f"Notion Outbound Sync Failed: {operation.op_type.value}",
            description=f"Operation {operation.operation_id} targeting {operation.target_database} failed after {attempt_count} attempts: {error_message}",
            failed_operations_count=1,
            dlq_ids=[entry.dlq_id],
        )
        self.incidents.append(incident)
        return entry

    def list_entries(self, status: str | None = None) -> list[DLQEntry]:
        """List DLQ entries."""
        if status:
            return [e for e in self.dlq_records.values() if e.status == status]
        return list(self.dlq_records.values())

    def list_incidents(self) -> list[NotionIntegrationIncident]:
        """List active integration incidents."""
        return self.incidents
