"""Unit tests for Observability components (S0-T5).

Tests correlation-ID middleware, structured logging, telemetry bootstrap,
and Prometheus metrics exposition.
"""

from __future__ import annotations

import json
import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from packages.contracts.correlation import correlation_id_var
from packages.contracts.logging import configure_logging, get_logger
from packages.contracts.telemetry import setup_telemetry
from services.api.metrics import PrometheusMiddleware, metrics_route
from services.api.middleware.correlation import CorrelationIDMiddleware


@pytest.fixture()
def app_with_observability() -> FastAPI:
    _app = FastAPI()
    _app.add_middleware(CorrelationIDMiddleware)
    _app.add_middleware(PrometheusMiddleware)
    _app.routes.append(metrics_route)

    @_app.get("/test-endpoint")
    async def test_endpoint() -> dict[str, str | None]:
        # Context variable should be populated
        cid = correlation_id_var.get(None)
        return {"correlation_id": cid}

    return _app


@pytest.fixture()
def client(app_with_observability: FastAPI) -> TestClient:
    return TestClient(app_with_observability)


class TestCorrelationIDMiddleware:
    def test_generates_id_when_not_provided(self, client: TestClient) -> None:
        response = client.get("/test-endpoint")
        assert response.status_code == 200
        header_cid = response.headers.get("X-Correlation-ID")
        assert header_cid is not None
        # Should be a valid UUID
        parsed_uuid = uuid.UUID(header_cid)
        assert str(parsed_uuid) == header_cid
        body = response.json()
        assert body["correlation_id"] == header_cid

    def test_preserves_provided_id(self, client: TestClient) -> None:
        custom_id = "test-custom-correlation-12345"
        response = client.get(
            "/test-endpoint",
            headers={"X-Correlation-ID": custom_id},
        )
        assert response.status_code == 200
        assert response.headers.get("X-Correlation-ID") == custom_id
        body = response.json()
        assert body["correlation_id"] == custom_id


class TestTelemetryAndLogging:
    def test_setup_telemetry_idempotent(self) -> None:
        setup_telemetry("korex-test-service")
        # Second call should not raise
        setup_telemetry("korex-test-service")

    def test_configure_logging_idempotent(self) -> None:
        configure_logging("korex-test-service")
        logger = get_logger("test.logger")
        assert logger is not None


class TestPrometheusMetrics:
    def test_metrics_endpoint_returns_prometheus_text(self, client: TestClient) -> None:
        # Trigger an endpoint to record metrics
        client.get("/test-endpoint")
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "korex_http_requests_total" in response.text
