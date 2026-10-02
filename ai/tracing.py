"""AI Run Tracing and Metadata Logger (S5-T6, AI-003, NFR-OBS-001).

Attaches unique trace identifiers, run ids, model metadata, and latency metrics to every AI execution.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class AIRunTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"trc_{uuid.uuid4().hex[:12]}")
    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:12]}")
    event_id: str
    proposal_id: str | None = None
    model_name: str = "gemini-1.5-pro"
    prompt_version: str = "v1.0"
    tool_calls: list[str] = Field(default_factory=list)
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None
    duration_ms: float = 0.0
    status: str = "COMPLETED"


class AITraceManager:
    """Manages AI execution trace life-cycles."""

    def __init__(self) -> None:
        self._traces: dict[str, AIRunTrace] = {}

    def start_trace(self, event_id: str, proposal_id: str | None = None) -> AIRunTrace:
        trace = AIRunTrace(event_id=event_id, proposal_id=proposal_id)
        self._traces[trace.trace_id] = trace
        return trace

    def finish_trace(self, trace_id: str, tool_calls: list[str], duration_ms: float = 45.0) -> AIRunTrace | None:
        trace = self._traces.get(trace_id)
        if trace:
            trace.tool_calls = tool_calls
            trace.duration_ms = duration_ms
            trace.completed_at = datetime.now(timezone.utc).isoformat()
            trace.status = "COMPLETED"
        return trace

    def get_trace(self, trace_id: str) -> AIRunTrace | None:
        return self._traces.get(trace_id)
