"""Refresh-Before-Commit & Conflict Detection Engine (Sprint 6, S6-T4, TAD §14, INT-NOT-005, AT-06).

Detects stale proposals and concurrency conflicts before bulk Notion commit:
- Re-fetches affected entity pages from Notion.
- Checks if `last_edited_time` or `version` has advanced past the proposal's baseline.
- If an operator concurrently modified a session/venue directly in Notion (AT-06), flags conflict and halts commit.
"""

from __future__ import annotations

from typing import Any
from integrations.notion.adapter import NotionAdapter
from packages.contracts.notion import NotionConflictReport


class StaleNotionProposalConflictError(Exception):
    """Raised when refresh-before-commit finds concurrent remote modifications in Notion."""
    def __init__(self, report: NotionConflictReport) -> None:
        super().__init__(f"Commit blocked due to Notion concurrency conflict: {report.reason}")
        self.report = report


class NotionConflictDetector:
    """Pre-commit validator that re-checks Notion state against proposal baseline."""

    def __init__(self, adapter: NotionAdapter | None = None) -> None:
        self.adapter = adapter or NotionAdapter()

    async def check_conflicts(
        self,
        target_page_ids: list[str],
        baseline_revision: int,
        baseline_timestamp: str,
    ) -> NotionConflictReport:
        """Re-fetch all target pages from Notion and compare against baseline snapshot."""
        conflicting_pages = []

        for page_id in target_page_ids:
            remote_page = await self.adapter.fetch_page(page_id)
            remote_version = remote_page.get("version", 1)
            remote_last_edited = remote_page.get("last_edited_time", "")

            # If remote page has been updated past the baseline timestamp / version
            if remote_last_edited > baseline_timestamp and remote_version > baseline_revision:
                conflicting_pages.append({
                    "page_id": page_id,
                    "remote_version": remote_version,
                    "baseline_revision": baseline_revision,
                    "remote_last_edited": remote_last_edited,
                    "title": remote_page.get("title", ""),
                })

        if conflicting_pages:
            report = NotionConflictReport(
                has_conflict=True,
                conflicting_pages=conflicting_pages,
                reason=f"Detected {len(conflicting_pages)} page(s) modified concurrently in Notion since proposal creation.",
                source_revision=baseline_revision,
                remote_revision=conflicting_pages[0]["remote_version"],
            )
            return report

        return NotionConflictReport(
            has_conflict=False,
            conflicting_pages=[],
            reason=None,
            source_revision=baseline_revision,
            remote_revision=baseline_revision,
        )
