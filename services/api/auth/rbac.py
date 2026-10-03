"""Server-side RBAC policy engine with 11 roles (BRD section 6).

Implements default-deny authorization. Every permission must be explicitly
granted via the ROLE_PERMISSIONS mapping. Event-scoped access enforces
BR-018 tenant isolation.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, status

from packages.contracts.auth import AuthUser
from services.api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Roles (BRD section 6)
# ---------------------------------------------------------------------------

class Role(StrEnum):
    SUPER_ADMIN = "super_admin"
    EVENT_COMMANDER = "event_commander"
    OPS_LEAD = "ops_lead"
    TECH_LEAD = "tech_lead"
    VOLUNTEER_COORDINATOR = "volunteer_coordinator"
    REGISTRATION_LEAD = "registration_lead"
    MARKETING_LEAD = "marketing_lead"
    STAGE_MANAGER = "stage_manager"
    TRANSPORT_COORDINATOR = "transport_coordinator"
    SECURITY_LEAD = "security_lead"
    VOLUNTEER = "volunteer"


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

class Permission(StrEnum):
    # Venue / infrastructure
    VENUE_READ = "venue:read"
    VENUE_WRITE = "venue:write"

    # Sessions / schedule
    SESSION_READ = "session:read"
    SESSION_WRITE = "session:write"

    # Proposals / simulation
    PROPOSAL_READ = "proposal:read"
    PROPOSAL_APPROVE = "proposal:approve"
    PROPOSAL_REJECT = "proposal:reject"

    # Notifications
    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_SEND = "notification:send"

    # Attendance
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_SCAN = "attendance:scan"

    # Transport
    TRANSPORT_READ = "transport:read"
    TRANSPORT_WRITE = "transport:write"

    # Crowd / safety
    CROWD_READ = "crowd:read"
    CROWD_WRITE = "crowd:write"

    # Volunteer management
    VOLUNTEER_READ = "volunteer:read"
    VOLUNTEER_WRITE = "volunteer:write"

    # Admin / system
    ADMIN_MANAGE = "admin:manage"
    ADMIN_AUDIT = "admin:audit"

    # Marketing / communications
    MARKETING_READ = "marketing:read"
    MARKETING_WRITE = "marketing:write"


# ---------------------------------------------------------------------------
# Role -> Permission mapping (dict-based, default-deny)
# ---------------------------------------------------------------------------

# All defined permissions for convenience
_ALL_PERMISSIONS: frozenset[str] = frozenset(p.value for p in Permission)

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    Role.SUPER_ADMIN: _ALL_PERMISSIONS,

    Role.EVENT_COMMANDER: frozenset({
        Permission.VENUE_READ, Permission.VENUE_WRITE,
        Permission.SESSION_READ, Permission.SESSION_WRITE,
        Permission.PROPOSAL_READ, Permission.PROPOSAL_APPROVE, Permission.PROPOSAL_REJECT,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
        Permission.ATTENDANCE_READ,
        Permission.TRANSPORT_READ,
        Permission.CROWD_READ, Permission.CROWD_WRITE,
        Permission.VOLUNTEER_READ, Permission.VOLUNTEER_WRITE,
        Permission.MARKETING_READ,
        Permission.ADMIN_AUDIT,
    }),

    Role.OPS_LEAD: frozenset({
        Permission.VENUE_READ, Permission.VENUE_WRITE,
        Permission.SESSION_READ, Permission.SESSION_WRITE,
        Permission.PROPOSAL_READ, Permission.PROPOSAL_APPROVE, Permission.PROPOSAL_REJECT,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
        Permission.ATTENDANCE_READ,
        Permission.TRANSPORT_READ,
        Permission.CROWD_READ,
        Permission.VOLUNTEER_READ,
    }),

    Role.TECH_LEAD: frozenset({
        Permission.VENUE_READ, Permission.VENUE_WRITE,
        Permission.SESSION_READ, Permission.SESSION_WRITE,
        Permission.PROPOSAL_READ,
        Permission.NOTIFICATION_READ,
        Permission.ADMIN_AUDIT,
    }),

    Role.VOLUNTEER_COORDINATOR: frozenset({
        Permission.VENUE_READ,
        Permission.SESSION_READ,
        Permission.VOLUNTEER_READ, Permission.VOLUNTEER_WRITE,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
        Permission.ATTENDANCE_READ,
    }),

    Role.REGISTRATION_LEAD: frozenset({
        Permission.VENUE_READ,
        Permission.SESSION_READ,
        Permission.ATTENDANCE_READ, Permission.ATTENDANCE_SCAN,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
    }),

    Role.MARKETING_LEAD: frozenset({
        Permission.VENUE_READ,
        Permission.SESSION_READ,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
        Permission.MARKETING_READ, Permission.MARKETING_WRITE,
    }),

    Role.STAGE_MANAGER: frozenset({
        Permission.VENUE_READ, Permission.VENUE_WRITE,
        Permission.SESSION_READ, Permission.SESSION_WRITE,
        Permission.NOTIFICATION_READ,
        Permission.CROWD_READ,
    }),

    Role.TRANSPORT_COORDINATOR: frozenset({
        Permission.VENUE_READ,
        Permission.TRANSPORT_READ, Permission.TRANSPORT_WRITE,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
    }),

    Role.SECURITY_LEAD: frozenset({
        Permission.VENUE_READ,
        Permission.CROWD_READ, Permission.CROWD_WRITE,
        Permission.ATTENDANCE_READ,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
        Permission.TRANSPORT_READ,
    }),

    Role.VOLUNTEER: frozenset({
        Permission.VENUE_READ,
        Permission.SESSION_READ,
        Permission.ATTENDANCE_SCAN,
    }),
}


# ---------------------------------------------------------------------------
# Policy engine helpers
# ---------------------------------------------------------------------------

def has_permission(user: AuthUser, permission: str) -> bool:
    """Check whether a user holds a given permission via any of their roles.

    Default-deny: returns False for unknown roles or unmapped permissions.
    """
    for role in user.roles:
        role_perms = ROLE_PERMISSIONS.get(role, frozenset())
        if permission in role_perms:
            return True
    return False


def check_event_scope(user: AuthUser, resource_event_id: str | None) -> bool:
    """Enforce BR-018 event isolation.

    Returns True if the user may access the resource:
    - super_admin bypasses event scoping.
    - If the resource has no event_id, access is allowed (global resource).
    - Otherwise the user's event_id must match the resource's event_id.
    """
    if Role.SUPER_ADMIN in user.roles:
        return True
    if resource_event_id is None:
        return True
    return user.event_id == resource_event_id


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def require_permission(
    permission: str,
    resource_event_id: str | None = None,
):
    """Return a FastAPI dependency that enforces a permission check.

    Usage::

        @router.post("/venues")
        async def create_venue(
            user: AuthUser = Depends(require_permission("venue:write")),
        ):
            ...

    Args:
        permission: The permission string to require.
        resource_event_id: If provided, also enforces event-scope isolation.

    Returns:
        A FastAPI-compatible dependency function.
    """

    async def _check(
        user: Annotated[AuthUser, Depends(get_current_user)],
    ) -> AuthUser:
        allowed = has_permission(user, permission)

        # Log the authorization decision
        logger.info(
            "AuthZ decision: user=%s permission=%s allowed=%s event_id=%s resource_event=%s",
            user.user_id,
            permission,
            allowed,
            user.event_id,
            resource_event_id,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}",
            )

        # Event scope check
        if resource_event_id is not None and not check_event_scope(user, resource_event_id):
            logger.warning(
                "Event isolation violation: user=%s user_event=%s resource_event=%s",
                user.user_id,
                user.event_id,
                resource_event_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: event scope mismatch (BR-018)",
            )

        return user

    return _check


def require_super_admin():
    """FastAPI dependency: allow ONLY super_admin.

    Used for destructive, event-wide actions such as cancelling an event, which
    must never be performed by a functional lead without super-admin authority.
    """

    async def _check(
        user: Annotated[AuthUser, Depends(get_current_user)],
    ) -> AuthUser:
        is_super = Role.SUPER_ADMIN in user.roles
        logger.info(
            "AuthZ super-admin gate: user=%s allowed=%s roles=%s",
            user.user_id,
            is_super,
            user.roles,
        )
        if not is_super:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a super admin may perform this action (event cancellation is super-admin gated).",
            )
        return user

    return _check
