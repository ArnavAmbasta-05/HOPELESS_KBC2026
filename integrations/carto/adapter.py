"""KoreX CARTO GIS & MCP Server Adapter.

Connects KoreX Digital Twin to CARTO AI MCP Server for spatial queries,
isoline catchment analysis, transit routing, and AI workflows.
"""

from __future__ import annotations

import json
import os
from typing import Any
import httpx
from dotenv import load_dotenv

from packages.contracts.logging import get_logger

load_dotenv()
logger = get_logger(__name__)


class CartoMCPAdapter:
    """Client adapter for CARTO AI Workflows & Spatial MCP Server."""

    def __init__(
        self,
        mcp_url: str | None = None,
        api_key: str | None = None,
        account_id: str | None = None,
    ) -> None:
        self.mcp_url = mcp_url or os.environ.get(
            "CARTO_MCP_URL", "https://gcp-asia-northeast1.api.carto.com/mcp/ac_o657y8er"
        )
        self.api_key = api_key or os.environ.get("CARTO_API_KEY", "")
        self.account_id = account_id or os.environ.get("CARTO_ACCOUNT_ID", "ac_o657y8er")
        self._req_id = 0

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _parse_sse_or_json(self, raw_text: str) -> dict[str, Any]:
        """Parses SSE data payload or direct JSON response."""
        lines = [
            line[6:].strip()
            for line in raw_text.split("\n")
            if line.startswith("data:") and line[6:].strip()
        ]
        for line in lines:
            try:
                return json.loads(line)
            except Exception:
                continue
        try:
            return json.loads(raw_text)
        except Exception:
            return {"raw": raw_text}

    async def call_mcp_method(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Executes a JSON-RPC 2.0 call over HTTP POST to CARTO MCP Server."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            payload["params"] = params

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "KoreX-KIIT-AI/1.0",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.mcp_url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error(
                    "carto_mcp.http_error",
                    status_code=resp.status_code,
                    body=resp.text[:200],
                )
                return {
                    "error": {
                        "code": resp.status_code,
                        "message": f"CARTO MCP HTTP {resp.status_code}: {resp.text[:150]}",
                    }
                }

            return self._parse_sse_or_json(resp.text)

    async def initialize(self) -> dict[str, Any]:
        """Initializes MCP session handshake with CARTO."""
        return await self.call_mcp_method(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "KoreX-KIIT-Twin",
                    "version": "1.0.0",
                },
            },
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        """Discovers all available tools on the CARTO MCP Server."""
        resp = await self.call_mcp_method("tools/list", {})
        res = resp.get("result", {})
        return res.get("tools", [])

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Calls an MCP tool by name."""
        resp = await self.call_mcp_method(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments or {},
            },
        )
        result = resp.get("result", {})
        content = result.get("content", [])
        if content and isinstance(content, list) and len(content) > 0:
            first = content[0]
            if first.get("type") == "text":
                try:
                    return json.loads(first.get("text", "{}"))
                except Exception:
                    return {"text": first.get("text")}
        return result

    async def get_workspace_info(self) -> dict[str, Any]:
        """Retrieves CARTO organization workspace details and resource link templates."""
        return await self.call_tool("get_workspace_info", {})

    async def geocode(
        self,
        query: str,
        operation: str = "geocode",
    ) -> dict[str, Any]:
        """Geocodes a place name (e.g. KIIT University Bhubaneswar) via CARTO LDS."""
        return await self.call_tool("geocode", {"query": query, "operation": operation})

    async def get_status_overview(self) -> dict[str, Any]:
        """Returns connection and tool status for KoreX UI."""
        try:
            tools = await self.list_tools()
            workspace = await self.get_workspace_info()
            return {
                "connected": True,
                "mcp_url": self.mcp_url,
                "account_id": self.account_id,
                "tools_count": len(tools),
                "tools": [t.get("name") for t in tools],
                "workspace": workspace,
            }
        except Exception as exc:
            return {
                "connected": False,
                "error": str(exc),
                "mcp_url": self.mcp_url,
            }
