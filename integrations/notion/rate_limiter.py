"""Notion API Rate Limiter & Backoff Engine (Sprint 6, TAD §14, INT-NOT-009).

Enforces Notion API rate limits:
- Token bucket algorithm (~3.0 requests/sec average, burst capacity 5).
- Exponential backoff with jitter on 429 / 503 HTTP responses.
- Respects `Retry-After` headers if returned by Notion API.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    rate_per_sec: float = 3.0  # Notion recommended rate
    burst_capacity: float = 5.0
    max_retries: int = 4
    initial_backoff_sec: float = 0.5
    max_backoff_sec: float = 8.0


class NotionRateLimiter:
    """Async Token Bucket Rate Limiter with Exponential Backoff."""

    def __init__(self, config: RateLimitConfig | None = None) -> None:
        self.config = config or RateLimitConfig()
        self.tokens = self.config.burst_capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        self.total_requests = 0
        self.throttled_requests = 0

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.config.burst_capacity, self.tokens + elapsed * self.config.rate_per_sec)
        self.last_refill = now

    async def acquire(self) -> None:
        """Acquire a token from the bucket, sleeping if exhausted."""
        async with self._lock:
            self._refill()
            if self.tokens < 1.0:
                needed = 1.0 - self.tokens
                sleep_time = needed / self.config.rate_per_sec
                self.throttled_requests += 1
                await asyncio.sleep(sleep_time)
                self._refill()

            self.tokens -= 1.0
            self.total_requests += 1

    async def execute_with_retry(self, coro_func, *args, **kwargs):
        """Execute async function with token acquisition and exponential backoff on rate limit."""
        retries = 0
        backoff = self.config.initial_backoff_sec

        while True:
            await self.acquire()
            try:
                return await coro_func(*args, **kwargs)
            except Exception as exc:
                retries += 1
                if retries > self.config.max_retries:
                    raise exc

                # Check if exception has retry-after info
                retry_after = getattr(exc, "retry_after", None)
                sleep_duration = float(retry_after) if retry_after else backoff
                await asyncio.sleep(sleep_duration)
                backoff = min(backoff * 2.0, self.config.max_backoff_sec)
