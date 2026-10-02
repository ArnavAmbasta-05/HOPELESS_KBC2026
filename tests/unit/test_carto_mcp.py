"""Unit tests for CARTO GIS & Spatial MCP adapter."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from integrations.carto.adapter import CartoMCPAdapter


@pytest.mark.asyncio
async def test_carto_adapter_initialization() -> None:
    adapter = CartoMCPAdapter(
        mcp_url="https://gcp-asia-northeast1.api.carto.com/mcp/ac_o657y8er",
        api_key="test_token",
        account_id="ac_o657y8er",
    )
    assert adapter.account_id == "ac_o657y8er"
    assert "carto.com" in adapter.mcp_url


@pytest.mark.asyncio
async def test_carto_adapter_parse_sse() -> None:
    adapter = CartoMCPAdapter()
    raw_sse = 'event: message\ndata: {"result":{"content":[{"type":"text","text":"{\\"status\\":\\"ok\\"}"}]},"jsonrpc":"2.0","id":1}\n\n'
    parsed = adapter._parse_sse_or_json(raw_sse)
    assert parsed.get("jsonrpc") == "2.0"
    assert "result" in parsed


@pytest.mark.asyncio
async def test_carto_adapter_call_tool_mock() -> None:
    adapter = CartoMCPAdapter()
    with patch.object(
        adapter,
        "call_mcp_method",
        new=AsyncMock(
            return_value={
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": '{"accountId": "ac_o657y8er", "workspaceUrl": "https://gcp-asia-northeast1.app.carto.com"}',
                        }
                    ]
                }
            }
        ),
    ):
        workspace = await adapter.get_workspace_info()
        assert workspace.get("accountId") == "ac_o657y8er"
        assert "gcp-asia-northeast1" in workspace.get("workspaceUrl")
