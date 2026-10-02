"""Integration and Golden Scenario Tests for Sprint 6 (Notion Live Integration & Golden Vertical Slice).

Validates:
- S6-T1: Notion Adapter contract (connect, pull, push, verify, health, error translation) (TAD §27.4)
- S6-T2: Inbound HMAC-SHA256 verified webhook sync + authoritative re-fetch (AT-01, INT-NOT-004)
- S6-T3: Outbound idempotent write plan execution (exact 32 golden writes) + post-write verification (Golden [6], INT-NOT-003/008)
- S6-T4: Refresh-before-commit conflict detection (AT-06, INT-NOT-005)
- S6-T5: Dead-letter queue (DLQ) & Operator-visible integration incidents (INT-NOT-007)
- S6-T6: Full End-to-end commit wiring & AT-08 zero-writes on rejection
"""

from __future__ import annotations

import hashlib
import hmac
import pytest
import httpx

from integrations.notion import (
    NotionAdapter,
    NotionCommitExecutor,
    NotionCommitPlanBuilder,
    NotionConflictDetector,
    NotionDLQManager,
    NotionRateLimiter,
    NotionWebhookReceiver,
    NotionWebhookVerificationError,
    StaleNotionProposalConflictError,
)
from packages.contracts.notion import (
    NotionOperationType,
    NotionWebhookPayload,
    NotionWriteOperation,
)
from services.api.auth.providers import DevLoginProvider
from services.api.main import app


class TestNotionAdapterContract:
    """Tests for S6-T1 (TAD §27.4)."""

    @pytest.mark.asyncio
    async def test_adapter_connect_and_health(self) -> None:
        adapter = NotionAdapter()
        assert await adapter.connect() is True

        health = await adapter.health()
        assert health.status == "HEALTHY"
        assert health.token_valid is True
        assert health.workspace_id == adapter.config.workspace_id

    @pytest.mark.asyncio
    async def test_adapter_pull_changes_and_cursor(self) -> None:
        adapter = NotionAdapter()
        changes, cursor = await adapter.pull_changes()

        assert len(changes) >= 4
        assert cursor.workspace_id == adapter.config.workspace_id
        assert cursor.last_synced_at is not None


    def test_adapter_error_translation(self) -> None:
        adapter = NotionAdapter()
        t1 = adapter.translate_error(Exception("401 Unauthorized API token"))
        assert t1["code"] == "NOTION_UNAUTHORIZED"
        assert t1["status"] == 401

        t2 = adapter.translate_error(Exception("429 Rate limit reached"))
        assert t2["code"] == "NOTION_RATE_LIMITED"
        assert t2["status"] == 429

        t3 = adapter.translate_error(Exception("Concurrency conflict on page"))
        assert t3["code"] == "NOTION_CONFLICT"
        assert t3["status"] == 409


class TestNotionWebhookInbound:
    """Tests for S6-T2 (AT-01, INT-NOT-004)."""

    @pytest.mark.asyncio
    async def test_webhook_signature_verification_and_refetch_disruption(self) -> None:
        receiver = NotionWebhookReceiver()
        raw_body = b'{"event_id": "evt_wh_01", "page_id": "page_ven_main_aud"}'
        secret = b"test_notion_webhook_secret"
        sig = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()

        # 1. Valid signature passes
        assert receiver.verify_signature(raw_body, sig) is True

        # 2. Process webhook -> re-fetch authoritative remote page state
        payload = NotionWebhookPayload(
            event_id="evt_wh_01",
            event_type="page.updated",
            page_id="page_ven_main_aud",
            workspace_id="ws_notion_kbc2026_sandbox",
        )
        result = await receiver.process_webhook(payload)

        assert result["processed"] is True
        assert result["disruption_detected"] is True
        assert result["disrupted_venue_id"] == "ven_main_aud"
        assert "Ceiling AC leak" in result["reason"]

    def test_webhook_tampered_signature_rejected(self) -> None:
        receiver = NotionWebhookReceiver()
        raw_body = b'{"event_id": "evt_wh_01", "page_id": "page_ven_main_aud"}'

        with pytest.raises(NotionWebhookVerificationError):
            receiver.verify_signature(raw_body, "tampered_invalid_signature")

        with pytest.raises(NotionWebhookVerificationError):
            receiver.verify_signature(raw_body, None)


class TestNotionOutboundCommitAndVerification:
    """Tests for S6-T3 & S6-T6 (Golden Section [6], INT-NOT-003/008, AT-08)."""

    def test_golden_write_plan_contains_exact_32_operations(self) -> None:
        builder = NotionCommitPlanBuilder()
        plan = builder.build_golden_write_plan(
            proposal_id="prop_kbc_disruption_001",
            event_id="evt_kbc2026",
        )

        assert len(plan.operations) == 32

        # 4 session updates
        session_ops = [op for op in plan.operations if op.target_database == "db_sessions"]
        assert len(session_ops) == 4

        # 5 volunteer updates
        volunteer_ops = [op for op in plan.operations if op.target_database == "db_volunteers"]
        assert len(volunteer_ops) == 5

        # 17 task pages
        task_ops = [op for op in plan.operations if op.target_database == "db_tasks"]
        assert len(task_ops) == 17

        # 4 stale comms flags
        comm_ops = [op for op in plan.operations if op.target_database == "db_communications"]
        assert len(comm_ops) == 4

        # 1 Impact Report
        impact_ops = [op for op in plan.operations if op.target_database == "db_impact_reports"]
        assert len(impact_ops) == 1

        # 1 Change Proposal page
        prop_ops = [op for op in plan.operations if op.target_database == "db_proposals"]
        assert len(prop_ops) == 1

    @pytest.mark.asyncio
    async def test_execute_approved_commit_full_golden_slice(self) -> None:
        executor = NotionCommitExecutor()

        result = await executor.execute_commit(
            proposal_id="prop_kbc_disruption_001",
            is_approved=True,
            baseline_revision=1,
            baseline_timestamp="2026-03-15T07:45:00Z",
        )

        assert result.status == "COMPLETED"
        assert result.total_operations == 32
        assert result.successful_operations == 32
        assert result.failed_operations == 0
        assert len(result.operation_ids) == 32

        # Verify all committed operations
        verification = await executor.adapter.verify(result.operation_ids)
        assert verification.verified is True
        assert verification.verified_count == 32

    @pytest.mark.asyncio
    async def test_rejected_proposal_produces_zero_notion_writes(self) -> None:
        """AT-08: Reject produces zero external writes."""
        executor = NotionCommitExecutor()

        result = await executor.execute_commit(
            proposal_id="prop_kbc_disruption_001",
            is_approved=False,
        )

        assert result.total_operations == 0
        assert result.successful_operations == 0
        assert result.status == "REJECTED_ZERO_WRITES"


class TestNotionConflictDetection:
    """Tests for S6-T4 (AT-06, INT-NOT-005)."""

    @pytest.mark.asyncio
    async def test_concurrent_notion_session_edit_triggers_conflict(self) -> None:
        """AT-06: Operator edits session venue directly in Notion -> refresh-before-commit blocks commit."""
        adapter = NotionAdapter()
        # Simulate operator direct edit in Notion (advancing version & timestamp)
        adapter._mock_remote_pages["page_ses_01"]["version"] = 3
        adapter._mock_remote_pages["page_ses_01"]["last_edited_time"] = "2026-03-15T08:15:00Z"

        executor = NotionCommitExecutor(adapter=adapter)

        with pytest.raises(StaleNotionProposalConflictError) as exc:
            await executor.execute_commit(
                proposal_id="prop_kbc_disruption_001",
                is_approved=True,
                baseline_revision=1,
                baseline_timestamp="2026-03-15T07:45:00Z",
            )

        assert "Detected 1 page(s) modified concurrently in Notion" in str(exc.value)


class TestNotionRateLimitingAndDLQ:
    """Tests for S6-T5 (INT-NOT-007, INT-NOT-009)."""

    @pytest.mark.asyncio
    async def test_dlq_recording_and_incident_creation(self) -> None:
        dlq_manager = NotionDLQManager()
        dummy_op = NotionWriteOperation(
            op_type=NotionOperationType.UPDATE_PAGE,
            target_database="db_tasks",
            description="Update task N01",
        )

        entry = dlq_manager.record_failure(
            plan_id="nplan_fail_01",
            operation=dummy_op,
            error_message="Notion API 500 internal server error",
            event_id="evt_kbc2026",
        )

        assert entry.dlq_id.startswith("dlq_")
        assert entry.status == "PENDING"
        assert len(dlq_manager.list_entries()) == 1

        incidents = dlq_manager.list_incidents()
        assert len(incidents) == 1
        assert "Notion Outbound Sync Failed" in incidents[0].title


class TestNotionHTTPAPI:
    """HTTP API endpoint tests for Sprint 6 Notion routes."""

    @pytest.mark.asyncio
    async def test_notion_webhooks_and_commit_api(self) -> None:
        provider = DevLoginProvider()
        token = provider.create_token(email="admin@kiit.ac.in", roles=["event_commander"])
        headers = {"Authorization": f"Bearer {token}"}

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Health endpoint
            health_resp = await client.get("/api/v1/integrations/notion/health", headers=headers)
            assert health_resp.status_code == 200
            assert health_resp.json()["data"]["status"] == "HEALTHY"

            # 2. Webhook receiver
            webhook_body = {
                "event_id": "wh_001",
                "event_type": "page.updated",
                "page_id": "page_ven_main_aud",
                "workspace_id": "ws_notion_kbc2026_sandbox",
                "signature": "test_sig",
            }
            import json
            raw_bytes = json.dumps(webhook_body).encode("utf-8")
            valid_sig = hmac.new(b"test_notion_webhook_secret", raw_bytes, hashlib.sha256).hexdigest()

            wh_resp = await client.post(
                "/api/v1/integrations/notion/webhooks",
                content=raw_bytes,
                headers={"Content-Type": "application/json", "Notion-Signature": valid_sig},
            )
            assert wh_resp.status_code == 200
            assert wh_resp.json()["data"]["disruption_detected"] is True

            # 3. Commit endpoint (32 golden writes)
            commit_resp = await client.post(
                "/api/v1/integrations/notion/commit",
                json={
                    "proposal_id": "prop_kbc_disruption_001",
                    "is_approved": True,
                    "baseline_revision": 1,
                    "baseline_timestamp": "2026-03-15T07:45:00Z",
                },
                headers=headers,
            )
            assert commit_resp.status_code == 200
            commit_data = commit_resp.json()["data"]
            assert commit_data["status"] == "COMPLETED"
            assert commit_data["total_operations"] == 32
            assert commit_data["successful_operations"] == 32
