"""Prometheus metrics endpoint and application-level metrics for KoreX API.

Exposes ``/metrics`` via ``prometheus_client`` and provides counters /
histograms that middleware or route handlers can update.
"""

from __future__ import annotations

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Route
import time
from typing import Callable

# ---------------------------------------------------------------------------
# Metric instruments
# ---------------------------------------------------------------------------

REQUEST_COUNT = Counter(
    "korex_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "korex_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

ACTIVE_REQUESTS = Gauge(
    "korex_http_active_requests",
    "Number of in-flight HTTP requests",
    ["method"],
)


# ---------------------------------------------------------------------------
# Middleware that records metrics per request
# ---------------------------------------------------------------------------

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Record request count, latency and active-request gauge."""

    async def dispatch(
        self, request: Request, call_next: Callable[..., Response]  # type: ignore[type-arg]
    ) -> Response:
        method = request.method
        path = request.url.path

        ACTIVE_REQUESTS.labels(method=method).inc()
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            REQUEST_COUNT.labels(method=method, path=path, status="500").inc()
            raise
        finally:
            elapsed = time.perf_counter() - start
            REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)
            ACTIVE_REQUESTS.labels(method=method).dec()

        REQUEST_COUNT.labels(
            method=method, path=path, status=str(response.status_code)
        ).inc()
        return response


# ---------------------------------------------------------------------------
# /metrics endpoint
# ---------------------------------------------------------------------------

async def metrics_endpoint(_request: Request) -> Response:
    """Return Prometheus text exposition."""
    body = generate_latest()
    return Response(content=body, media_type=CONTENT_TYPE_LATEST)


# Route object that can be added to the FastAPI/Starlette router
metrics_route = Route("/metrics", endpoint=metrics_endpoint, methods=["GET"])
