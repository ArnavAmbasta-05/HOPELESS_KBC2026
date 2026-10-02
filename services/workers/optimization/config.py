"""Versioned Rules and Optimization Configuration (S3-T1.2, NFR-MNT-001).

Configures rule parameters, capacity margins, walking durations between buildings,
setup buffer times, and role escalation matrices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True)
class RuleConfig:
    """Configurable parameters for the Rules Engine and Solvers."""

    version: str = "v1.0"
    min_capacity_headroom: float = 0.0  # Fraction of extra capacity required (0.0 = exact capacity allowed)
    building_walk_minutes: dict[tuple[str, str], int] = field(
        default_factory=lambda: {
            ("Bldg A", "Bldg B"): 5,
            ("Bldg A", "Bldg C"): 8,
            ("Bldg A", "Bldg D"): 7,
            ("Bldg B", "Bldg C"): 6,
            ("Bldg B", "Bldg D"): 4,
            ("Bldg C", "Bldg D"): 8,
        }
    )
    av_setup_buffer_minutes: int = 30
    stage_setup_buffer_minutes: int = 45
    min_volunteer_rest_minutes: int = 30
    at_risk_slack_threshold_minutes: int = 0  # 0 or negative slack is AT RISK
    solver_timeout_seconds: int = 5


DEFAULT_RULE_CONFIG: Final[RuleConfig] = RuleConfig()


def get_rule_config() -> RuleConfig:
    """Return default rule and threshold configuration."""
    return DEFAULT_RULE_CONFIG
