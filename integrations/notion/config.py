"""Notion workspace adapter configuration for KoreX (S0-T6.3).

Defines NotionWorkspaceConfig schema and sandbox database mapping placeholders.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True)
class NotionWorkspaceConfig:
    """Configuration for a Notion workspace integration.

    Attributes:
        workspace_id: Unique identifier for the Notion workspace.
        token_env_var: Environment variable holding the integration token.
        schema_version: Version of the Notion schema map.
        database_mappings: Mapping of domain entity type to Notion database ID.
    """

    workspace_id: str = "ws_notion_kbc2026_sandbox"
    token_env_var: str = "NOTION_API_TOKEN"
    schema_version: str = "v1.0"
    database_mappings: dict[str, str] = field(default_factory=dict)

    @property
    def api_token(self) -> str | None:
        """Retrieve token from configured environment variable or fallback."""
        return os.environ.get(self.token_env_var) or os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_API_TOKEN")


# Canonical entity types for Notion synchronization
ENTITY_VENUES: Final[str] = "venues"
ENTITY_SESSIONS: Final[str] = "sessions"
ENTITY_VOLUNTEERS: Final[str] = "volunteers"
ENTITY_SPEAKERS: Final[str] = "speakers"
ENTITY_EQUIPMENT: Final[str] = "equipment"
ENTITY_TASKS: Final[str] = "tasks"
ENTITY_INCIDENTS: Final[str] = "incidents"
ENTITY_PROPOSALS: Final[str] = "proposals"

# Sandbox placeholder database mappings (to be updated with actual Notion DB IDs)
SANDBOX_DATABASE_MAPPINGS: Final[dict[str, str]] = {
    ENTITY_VENUES: "db_notion_sandbox_venues_placeholder",
    ENTITY_SESSIONS: "db_notion_sandbox_sessions_placeholder",
    ENTITY_VOLUNTEERS: "db_notion_sandbox_volunteers_placeholder",
    ENTITY_SPEAKERS: "db_notion_sandbox_speakers_placeholder",
    ENTITY_EQUIPMENT: "db_notion_sandbox_equipment_placeholder",
    ENTITY_TASKS: "db_notion_sandbox_tasks_placeholder",
    ENTITY_INCIDENTS: "db_notion_sandbox_incidents_placeholder",
    ENTITY_PROPOSALS: "db_notion_sandbox_proposals_placeholder",
}

# Sandbox workspace configuration
SANDBOX_NOTION_CONFIG: Final[NotionWorkspaceConfig] = NotionWorkspaceConfig(
    workspace_id="ws_notion_kbc2026_sandbox",
    token_env_var="NOTION_API_TOKEN",
    schema_version="v1.0",
    database_mappings=SANDBOX_DATABASE_MAPPINGS,
)


def get_sandbox_notion_config() -> NotionWorkspaceConfig:
    """Return the default sandbox Notion workspace configuration."""
    return SANDBOX_NOTION_CONFIG


