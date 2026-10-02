"""Correlation-ID context variable — shared across middleware and logging.

This module owns the ``contextvars.ContextVar`` so that both the FastAPI
middleware and the structured-logging processors can import from a
single canonical location without circular imports.
"""

from __future__ import annotations

from contextvars import ContextVar

# Thread-/async-safe correlation ID propagated through the request lifecycle.
correlation_id_var: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)
