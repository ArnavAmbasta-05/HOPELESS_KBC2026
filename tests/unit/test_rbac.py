"""Unit tests for the RBAC policy engine (S0-T4.2)."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from packages.contracts.auth import AuthUser
from services.api.auth.providers import DevLoginProvider
from services.api.auth.rbac import (
    ROLE_PERMISSIONS,
    Permission,
    Role,
    check_event_scope,
    has_permission,
    require_permission,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _dev_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")


@pytest.fixture()
def provider() -> DevLoginProvider:
    return DevLoginProvider()


def _make_user(
    roles: list[str],
    event_id: str | None = None,
    user_id: str = "u-test",
    email: str = "test@example.com",
) -> AuthUser:
    return AuthUser(
        user_id=user_id,
        email=email,
        name="Test User",
        roles=roles,
        event_id=event_id,
    )


# ---------------------------------------------------------------------------
# Role enum completeness
# ---------------------------------------------------------------------------

class TestRoleEnum:
    def test_eleven_roles_defined(self) -> None:
        assert len(Role) == 11

    def test_all_roles_have_permission_mapping(self) -> None:
        for role in Role:
            assert role.value in ROLE_PERMISSIONS, f"Missing mapping for {role}"


# ---------------------------------------------------------------------------
# Permission enum
# ---------------------------------------------------------------------------

class TestPermissionEnum:
    def test_permissions_are_colon_separated(self) -> None:
        for perm in Permission:
            assert ":" in perm.value, f"Permission {perm} should use 'resource:action' format"


# ---------------------------------------------------------------------------
# has_permission — default deny
# ---------------------------------------------------------------------------

class TestHasPermission:
    def test_super_admin_has_all_permissions(self) -> None:
        user = _make_user(roles=["super_admin"])
        for perm in Permission:
            assert has_permission(user, perm.value), f"super_admin should have {perm}"

    def test_volunteer_limited_permissions(self) -> None:
        user = _make_user(roles=["volunteer"])
        # Volunteer can read venues and sessions, and scan attendance
        assert has_permission(user, Permission.VENUE_READ)
        assert has_permission(user, Permission.SESSION_READ)
        assert has_permission(user, Permission.ATTENDANCE_SCAN)
        # Volunteer cannot write venues, approve proposals, or manage admin
        assert not has_permission(user, Permission.VENUE_WRITE)
        assert not has_permission(user, Permission.PROPOSAL_APPROVE)
        assert not has_permission(user, Permission.ADMIN_MANAGE)
        assert not has_permission(user, Permission.NOTIFICATION_SEND)

    def test_default_deny_unknown_role(self) -> None:
        user = _make_user(roles=["nonexistent_role"])
        assert not has_permission(user, Permission.VENUE_READ)

    def test_default_deny_unknown_permission(self) -> None:
        user = _make_user(roles=["volunteer"])
        assert not has_permission(user, "magic:power")

    def test_no_roles_denies_everything(self) -> None:
        user = _make_user(roles=[])
        for perm in Permission:
            assert not has_permission(user, perm.value)

    def test_multiple_roles_union_permissions(self) -> None:
        """A user with multiple roles gets the union of their permissions."""
        user = _make_user(roles=["registration_lead", "stage_manager"])
        # registration_lead has attendance:scan
        assert has_permission(user, Permission.ATTENDANCE_SCAN)
        # stage_manager has session:write
        assert has_permission(user, Permission.SESSION_WRITE)

    def test_event_commander_permissions(self) -> None:
        user = _make_user(roles=["event_commander"])
        assert has_permission(user, Permission.PROPOSAL_APPROVE)
        assert has_permission(user, Permission.NOTIFICATION_SEND)
        assert has_permission(user, Permission.CROWD_WRITE)
        # event_commander does not have admin:manage
        assert not has_permission(user, Permission.ADMIN_MANAGE)


# ---------------------------------------------------------------------------
# Event-scope isolation (BR-018)
# ---------------------------------------------------------------------------

class TestEventScope:
    def test_same_event_allowed(self) -> None:
        user = _make_user(roles=["ops_lead"], event_id="evt-A")
        assert check_event_scope(user, "evt-A") is True

    def test_different_event_denied(self) -> None:
        user = _make_user(roles=["ops_lead"], event_id="evt-A")
        assert check_event_scope(user, "evt-B") is False

    def test_super_admin_bypasses_event_scope(self) -> None:
        user = _make_user(roles=["super_admin"], event_id="evt-A")
        assert check_event_scope(user, "evt-B") is True

    def test_global_resource_no_event_id(self) -> None:
        user = _make_user(roles=["ops_lead"], event_id="evt-A")
        assert check_event_scope(user, None) is True

    def test_user_without_event_accessing_scoped_resource(self) -> None:
        user = _make_user(roles=["ops_lead"], event_id=None)
        # user.event_id is None, resource event is "evt-X" => None != "evt-X" => denied
        assert check_event_scope(user, "evt-X") is False


# ---------------------------------------------------------------------------
# require_permission FastAPI dependency (integration via TestClient)
# ---------------------------------------------------------------------------

class TestRequirePermission:
    @pytest.fixture()
    def app_with_rbac(self) -> FastAPI:
        _app = FastAPI()

        @_app.get("/venues", dependencies=[Depends(require_permission(Permission.VENUE_READ))])
        async def list_venues() -> dict[str, str]:
            return {"status": "ok"}

        @_app.post("/venues", dependencies=[Depends(require_permission(Permission.VENUE_WRITE))])
        async def create_venue() -> dict[str, str]:
            return {"status": "created"}

        @_app.get(
            "/scoped",
            dependencies=[Depends(require_permission(Permission.VENUE_READ, resource_event_id="evt-A"))],
        )
        async def scoped_resource() -> dict[str, str]:
            return {"status": "ok"}

        return _app

    @pytest.fixture()
    def rbac_client(self, app_with_rbac: FastAPI) -> TestClient:
        return TestClient(app_with_rbac)

    def _token(self, provider: DevLoginProvider, roles: list[str], event_id: str | None = None) -> str:
        return provider.create_token(email="u@t.com", roles=roles, event_id=event_id)

    def test_allowed_permission(self, rbac_client: TestClient, provider: DevLoginProvider) -> None:
        token = self._token(provider, ["ops_lead"])
        resp = rbac_client.get("/venues", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_denied_permission_returns_403(self, rbac_client: TestClient, provider: DevLoginProvider) -> None:
        token = self._token(provider, ["volunteer"])
        # Volunteer cannot write venues
        resp = rbac_client.post("/venues", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_no_token_returns_401(self, rbac_client: TestClient) -> None:
        resp = rbac_client.get("/venues")
        assert resp.status_code == 401

    def test_event_scope_match_allowed(self, rbac_client: TestClient, provider: DevLoginProvider) -> None:
        token = self._token(provider, ["ops_lead"], event_id="evt-A")
        resp = rbac_client.get("/scoped", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_event_scope_mismatch_denied(self, rbac_client: TestClient, provider: DevLoginProvider) -> None:
        token = self._token(provider, ["ops_lead"], event_id="evt-B")
        resp = rbac_client.get("/scoped", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_super_admin_bypasses_event_scope(self, rbac_client: TestClient, provider: DevLoginProvider) -> None:
        token = self._token(provider, ["super_admin"], event_id="evt-Z")
        resp = rbac_client.get("/scoped", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_unknown_permission_denied(self, provider: DevLoginProvider) -> None:
        """Default-deny: an unmapped permission is always denied."""
        user = _make_user(roles=["volunteer"])
        assert not has_permission(user, "does_not:exist")
