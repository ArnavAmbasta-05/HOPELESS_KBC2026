"""Prompt-Injection Defense, Tool Allow-Listing & Mutating Tool Security Gate (S5-T5, AI-006, TAD §21).

Enforces:
1. Tool allow-listing: arbitrary tool execution is strictly prohibited.
2. User text isolation: untrusted user/attendee input cannot inject system instructions or invoke tools.
3. Mutating tool protection: state mutations cannot occur without verified human approval.
"""

from __future__ import annotations

import re
from typing import Any
from ai.tools import ALLOWLISTED_TOOLS, TOOL_MAP


class UnauthorizedToolExecutionError(Exception):
    """Raised when an unapproved or disallowed tool is invoked."""
    pass


class PromptInjectionDetectedError(Exception):
    """Raised when suspicious prompt-injection payloads are detected in user input."""
    pass


class MutatingToolRequiresApprovalError(Exception):
    """Raised when a state-mutating tool is executed without an approved proposal."""
    pass


# Disallowed system prompt override patterns
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt\s+override",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"bypass\s+all\s+rules",
    r"execute\s+arbitrary\s+python",
    r"drop\s+table\s+audit_records",
]


class PromptSecurityGuard:
    """Validates tool execution permissions and inspects user input for injection attempts."""

    @staticmethod
    def validate_tool_name(tool_name: str) -> None:
        """Check tool against the strict allow-list."""
        if tool_name not in TOOL_MAP:
            raise UnauthorizedToolExecutionError(
                f"Tool '{tool_name}' is not in the authorized tool allow-list"
            )

    @staticmethod
    def sanitize_and_inspect_user_text(text: str) -> str:
        """Scan user text for adversarial injection attempts."""
        cleaned = text.strip()
        for pattern in _INJECTION_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise PromptInjectionDetectedError(
                    f"Adversarial prompt injection pattern detected matching '{pattern}'"
                )
        return cleaned

    @staticmethod
    def verify_mutating_tool_gate(tool_name: str, is_approved: bool) -> None:
        """Ensure state-mutating operations require human approval (AI-006)."""
        mutating_tools = {"commit_plan", "execute_writes", "notion_update_page", "send_live_notifications"}
        if tool_name in mutating_tools and not is_approved:
            raise MutatingToolRequiresApprovalError(
                f"Tool '{tool_name}' mutates operational state and requires verified human approval before execution"
            )
