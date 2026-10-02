"""Idempotency management for API mutation operations (S1-T3.2, NFR-REL-002).

Ensures requests containing an Idempotency-Key header are executed at most once,
returning cached results on replay.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import Header, HTTPException, Request, Response, status


class IdempotencyStore:
    """In-memory idempotency store with TTL (backed by Redis in production)."""

    def __init__(self, ttl_seconds: int = 86400) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, int, dict[str, Any]]] = {}

    def get(self, key: str) -> tuple[int, dict[str, Any]] | None:
        if key in self._store:
            expiry, status_code, body = self._store[key]
            if time.time() < expiry:
                return status_code, body
            del self._store[key]
        return None

    def set(self, key: str, status_code: int, body: dict[str, Any]) -> None:
        expiry = time.time() + self.ttl_seconds
        self._store[key] = (expiry, status_code, body)


_idempotency_store = IdempotencyStore()


def get_idempotency_store() -> IdempotencyStore:
    """Return singleton idempotency store."""
    return _idempotency_store
