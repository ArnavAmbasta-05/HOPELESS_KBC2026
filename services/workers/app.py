"""KoreX Worker — Celery application entry point."""

from __future__ import annotations

import os

from celery import Celery

# Broker and result backend from environment
broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
result_backend = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "korex_worker",
    broker=broker_url,
    backend=result_backend,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    worker_hijack_root_logger=False,
)


@app.task(name="korex.health_check")
def health_check() -> dict[str, str]:
    """Celery health check task — verifies the worker is alive."""
    return {"status": "ok", "worker": "korex"}


@app.task(name="korex.seed_placeholder")
def seed_placeholder() -> dict[str, str]:
    """Placeholder task — will be replaced in S0-T6 with real seeding logic."""
    return {"status": "seeded"}
