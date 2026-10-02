"""Correlation-ID middleware for FastAPI.

Extracts ``X-Correlation-ID`` from the incoming request (or generates a
new UUID-4), propagates it via :pydata:`contextvars` so that structured
logging and OTel spans can attach it, and echoes it back on the response.
"""

from __future__ import annotations

import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from opentelemetry import trace

from packages.contracts.correlation import correlation_id_var

_HEADER = "X-Correlation-ID"


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Injects and propagates a correlation ID per request."""

    async def dispatch(
        self, request: Request, call_next: Callable[..., Response]  # type: ignore[type-arg]
    ) -> Response:
        # Extract or generate
        cid = request.headers.get(_HEADER) or str(uuid.uuid4())

        # Store in contextvar (available to logging processors)
        token = correlation_id_var.set(cid)

        # Attach to the current OTel span as an attribute
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("correlation.id", cid)

        try:
            response: Response = await call_next(request)
        finally:
            correlation_id_var.reset(token)

        response.headers[_HEADER] = cid
        return response
