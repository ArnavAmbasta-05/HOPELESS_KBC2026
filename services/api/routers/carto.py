"""KoreX API — CARTO GIS & Spatial MCP Router.

Exposes live CARTO AI Workflows, LDS routing, catchment isolines,
and spatial SQL tools to KoreX frontend and Gemini Copilot.
"""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from integrations.carto.adapter import CartoMCPAdapter
from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.logging import get_logger
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/carto", tags=["CARTO GIS & Spatial MCP"])

_carto_adapter = CartoMCPAdapter()


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="CARTO MCP tool name")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")


class GeocodeRequest(BaseModel):
    query: str = Field(default="KIIT University, Patia, Bhubaneswar", description="Address or landmark to geocode")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/status",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Get CARTO MCP Server connection status, active tools, and workspace URL",
)
async def get_carto_status(
    current_user: AuthUser = Depends(require_permission(Permission.VENUE_READ)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Returns live connection health to CARTO AI MCP Server."""
    status_data = await _carto_adapter.get_status_overview()
    return make_success_envelope(data=status_data, request_id=str(uuid.uuid4()))


@router.get(
    "/tools",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="List all 14 CARTO MCP spatial tools and workflows",
)
async def list_carto_tools(
    current_user: AuthUser = Depends(require_permission(Permission.VENUE_READ)),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Returns all available CARTO MCP spatial analysis tools."""
    tools = await _carto_adapter.list_tools()
    return make_success_envelope(data=tools, request_id=str(uuid.uuid4()))


@router.post(
    "/call",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Execute a CARTO MCP spatial tool dynamically",
)
async def execute_carto_tool(
    request: ToolCallRequest,
    current_user: AuthUser = Depends(require_permission(Permission.VENUE_WRITE)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Calls a CARTO MCP tool (e.g. geocode, route, calculate_isolines, explore_data)."""

    try:
        result = await _carto_adapter.call_tool(request.tool_name, request.arguments)
        return make_success_envelope(data={"tool": request.tool_name, "result": result}, request_id=str(uuid.uuid4()))
    except Exception as exc:
        logger.error("carto.tool_call_failed", tool=request.tool_name, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CARTO MCP tool '{request.tool_name}' failed: {exc}",
        )
