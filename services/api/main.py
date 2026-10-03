from __future__ import annotations

import os
import uuid
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from packages.contracts.envelope import ErrorDetail, ErrorEnvelope, make_error_envelope
from packages.contracts.logging import configure_logging, get_logger
from packages.contracts.telemetry import setup_telemetry
from services.api.auth.router import router as auth_router
from services.api.metrics import PrometheusMiddleware, metrics_route
from services.api.middleware.correlation import CorrelationIDMiddleware
from services.api.routers import (
    ai_router,
    attendance_router,
    audit_router,
    crowd_router,
    dependencies_router,
    events_router,
    knowledge_router,
    notifications_router,
    notion_router,
    participants_router,
    planning_router,
    proposals_router,
    resources_router,
    sessions_router,
    transport_router,
    venues_router,
    weather_router,
    carto_router,
    scenario_router,
    governance_router,
    itinerary_router,
)


# ---------------------------------------------------------------------------
# Bootstrap observability before the app object is used
# ---------------------------------------------------------------------------
setup_telemetry("korex-api")
configure_logging("korex-api")

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="KoreX API",
    description="KIIT EventOps AI Command Center API — Digital Twin & Operation Engine",
    version="0.1.0",
)

# CORS — allow local dev and deployed frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation-ID middleware (runs after CORS, before route handlers)
app.add_middleware(CorrelationIDMiddleware)

# Prometheus request metrics middleware
app.add_middleware(PrometheusMiddleware)

# /metrics endpoint (Prometheus scrape target)
app.routes.append(metrics_route)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(venues_router)
app.include_router(sessions_router)
app.include_router(participants_router)
app.include_router(resources_router)
app.include_router(audit_router)
app.include_router(dependencies_router)
app.include_router(planning_router)
app.include_router(proposals_router)
app.include_router(ai_router)
app.include_router(notion_router)
app.include_router(notifications_router)
app.include_router(attendance_router)
app.include_router(transport_router)
app.include_router(crowd_router)
app.include_router(weather_router)
app.include_router(knowledge_router)
app.include_router(carto_router)
app.include_router(scenario_router)
app.include_router(governance_router)
app.include_router(itinerary_router)



# ---------------------------------------------------------------------------
# Standard Error Handlers (TAD §27.1)
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = str(uuid.uuid4())
    correlation_id = request.headers.get("X-Correlation-ID")
    code = "HTTP_ERROR"
    if exc.status_code == status.HTTP_409_CONFLICT:
        code = "STALE_REVISION_CONFLICT"
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "NOT_FOUND"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        code = "PERMISSION_DENIED"
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        code = "UNAUTHORIZED"

    envelope = make_error_envelope(
        code=code,
        message=str(exc.detail),
        request_id=request_id,
        correlation_id=correlation_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=envelope.model_dump(mode="json"),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = str(uuid.uuid4())
    correlation_id = request.headers.get("X-Correlation-ID")
    details = [
        ErrorDetail(
            field=" -> ".join(str(loc) for loc in err.get("loc", [])),
            message=err.get("msg", ""),
            code=err.get("type"),
        )
        for err in exc.errors()
    ]
    envelope = make_error_envelope(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        request_id=request_id,
        correlation_id=correlation_id,
        details=details,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=envelope.model_dump(mode="json"),
    )


# OTel automatic instrumentation for FastAPI
FastAPIInstrumentor.instrument_app(app)

logger.info("app.started", version=app.version)


# ---------------------------------------------------------------------------
# Root, Health & Static SPA Routes (Supports 1-Service Cloud Deployment)
# ---------------------------------------------------------------------------
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

WEB_DIST = Path(__file__).resolve().parent.parent.parent / "apps" / "web" / "dist"

@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}

if WEB_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(WEB_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("metrics"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = WEB_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(WEB_DIST / "index.html")
else:
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root redirect hint."""
        return {"message": "KoreX API is running. See /docs for OpenAPI spec."}

