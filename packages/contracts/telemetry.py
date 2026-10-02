"""OpenTelemetry setup — traces, metrics, and logs for KoreX services.

Provides ``setup_telemetry(service_name)`` which initialises a
TracerProvider (OTLP exporter), MeterProvider (Prometheus exporter) and
LoggerProvider in one call.  Import this module early in the service
entry point.
"""

from __future__ import annotations

import os
from typing import Optional

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # type: ignore[import-not-found]
        OTLPSpanExporter,
    )
except ImportError:
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # type: ignore[import-not-found]
            OTLPSpanExporter,
        )
    except ImportError:
        OTLPSpanExporter = None  # type: ignore[assignment,misc]

# Prometheus exporter for metrics — exposes /metrics via prometheus_client
try:
    from opentelemetry.exporter.prometheus import PrometheusMetricReader  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover — optional at import time
    PrometheusMetricReader = None  # type: ignore[assignment,misc]

_INITIALISED: bool = False


def setup_telemetry(
    service_name: str,
    *,
    service_version: str = "0.1.0",
    environment: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
) -> None:
    """Bootstrap OpenTelemetry for *service_name*.

    Parameters
    ----------
    service_name:
        Populates the ``service.name`` resource attribute.
    service_version:
        Populates ``service.version``.
    environment:
        Populates ``deployment.environment``; falls back to
        ``DEPLOYMENT_ENVIRONMENT`` env-var, then ``"development"``.
    otlp_endpoint:
        gRPC endpoint for the OTLP exporter.  Falls back to
        ``OTEL_EXPORTER_OTLP_ENDPOINT``, then ``"http://localhost:4317"``.
    """
    global _INITIALISED  # noqa: PLW0603
    if _INITIALISED:
        return
    _INITIALISED = True

    env = environment or os.getenv("DEPLOYMENT_ENVIRONMENT", "development")
    endpoint = otlp_endpoint or os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
    )

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": env,
        }
    )

    # --- Traces ----------------------------------------------------------
    tracer_provider = TracerProvider(resource=resource)
    if OTLPSpanExporter is not None:
        span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    elif env == "development":
        # In dev without OTLP collector, don't spam stdout unless configured
        pass
    trace.set_tracer_provider(tracer_provider)

    # --- Metrics ---------------------------------------------------------
    readers: list[PeriodicExportingMetricReader | PrometheusMetricReader] = []  # type: ignore[type-arg]
    if PrometheusMetricReader is not None:
        readers.append(PrometheusMetricReader())  # type: ignore[no-untyped-call]
    meter_provider = MeterProvider(resource=resource, metric_readers=readers)  # type: ignore[arg-type]
    metrics.set_meter_provider(meter_provider)
