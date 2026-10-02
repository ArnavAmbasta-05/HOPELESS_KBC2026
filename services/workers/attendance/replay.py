"""Offline Scan Batch Replay Engine (Sprint 7, S7-T5, ATT-004, TAD §18).

Processes queued offline scans submitted when participant scanners reconnect to the network:
- Evaluates batches with strict duplicate suppression
- Replays valid scans into IngestService
- Returns summary of processed vs duplicate counts
"""

from __future__ import annotations

from typing import Any
from packages.contracts.attendance import AttendanceRecord, ScanIngestRequest
from services.workers.attendance.ingest import ScanIngestService


class OfflineScanReplayEngine:
    """Replays queued offline scans idempotently."""

    def __init__(self, ingest_service: ScanIngestService) -> None:
        self.ingest_service = ingest_service

    def replay_batch(self, scan_batch: list[ScanIngestRequest]) -> dict[str, Any]:
        """Replay a batch of offline scans with deduplication."""
        processed_records: list[AttendanceRecord] = []
        duplicate_count = 0
        error_count = 0

        for req in scan_batch:
            try:
                record, is_dup = self.ingest_service.ingest_scan(req)
                if is_dup:
                    duplicate_count += 1
                else:
                    processed_records.append(record)
            except Exception:
                error_count += 1

        return {
            "total_submitted": len(scan_batch),
            "new_records_created": len(processed_records),
            "duplicates_suppressed": duplicate_count,
            "errors_rejected": error_count,
            "status": "COMPLETED",
        }
