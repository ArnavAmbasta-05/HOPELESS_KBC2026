"""Standard API response envelopes, metadata, and pagination schemas (TAD §27.1).

All API endpoints return JSON conforming to ResponseEnvelope[T]:
{
    "data": ...,
    "meta": {
        "request_id": str,
        "correlation_id": str | None,
        "revision": int | None,
        "page": int | None,
        "limit": int | None,
        "total": int | None,
        "timestamp": str
    },
    "error": ErrorEnvelope | None
}
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaEnvelope(BaseModel):
    """Metadata included in every API response."""

    request_id: str = Field(..., description="Unique request identifier")
    correlation_id: str | None = Field(default=None, description="End-to-end correlation ID")
    revision: int | None = Field(default=None, description="Aggregate revision number for optimistic concurrency")
    page: int | None = Field(default=None, description="Current page index (1-based)")
    limit: int | None = Field(default=None, description="Items per page")
    total: int | None = Field(default=None, description="Total count matching filter")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp",
    )


class ErrorDetail(BaseModel):
    """Individual error or validation item."""

    field: str | None = None
    message: str
    code: str | None = None


class ErrorEnvelope(BaseModel):
    """Structured error payload when status != success."""

    code: str = Field(..., description="Standardized error code (e.g. STALE_REVISION, NOT_FOUND, PERMISSION_DENIED)")
    message: str = Field(..., description="Human-readable error description")
    details: list[ErrorDetail] = Field(default_factory=list, description="Specific field validation or constraint details")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Canonical response envelope for all KoreX REST endpoints."""

    data: T | None = Field(default=None, description="Response payload")
    meta: MetaEnvelope = Field(..., description="Response metadata")
    error: ErrorEnvelope | None = Field(default=None, description="Error payload if request failed")


def make_success_envelope(
    data: T,
    *,
    request_id: str,
    correlation_id: str | None = None,
    revision: int | None = None,
    page: int | None = None,
    limit: int | None = None,
    total: int | None = None,
) -> ResponseEnvelope[T]:
    """Factory helper to construct a successful ResponseEnvelope."""
    return ResponseEnvelope[T](
        data=data,
        meta=MetaEnvelope(
            request_id=request_id,
            correlation_id=correlation_id,
            revision=revision,
            page=page,
            limit=limit,
            total=total,
        ),
        error=None,
    )


def make_error_envelope(
    code: str,
    message: str,
    *,
    request_id: str,
    correlation_id: str | None = None,
    details: list[ErrorDetail] | None = None,
) -> ResponseEnvelope[None]:
    """Factory helper to construct an error ResponseEnvelope."""
    return ResponseEnvelope[None](
        data=None,
        meta=MetaEnvelope(
            request_id=request_id,
            correlation_id=correlation_id,
        ),
        error=ErrorEnvelope(
            code=code,
            message=message,
            details=details or [],
        ),
    )
