"""Unit tests for auth providers and dependencies (S0-T4.1)."""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from packages.contracts.auth import AuthProvider, AuthUser
from services.api.auth.dependencies import get_current_user
from services.api.auth.providers import (
    DevLoginProvider,
    OIDCProviderStub,
    _DEFAULT_ALGORITHM,
    _DEFAULT_SECRET,
)
from services.api.auth.router import router as auth_router


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _dev_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure APP_ENV=development for all tests in this module."""
    monkeypatch.setenv("APP_ENV", "development")


@pytest.fixture()
def provider() -> DevLoginProvider:
    return DevLoginProvider()


@pytest.fixture()
def app() -> FastAPI:
    _app = FastAPI()
    _app.include_router(auth_router)

    @_app.get("/protected")
    async def protected(user: AuthUser = pytest.importorskip("fastapi").Depends(get_current_user)):  # type: ignore[assignment]
        return {"user_id": user.user_id, "email": user.email}

    return _app


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# AuthUser model tests
# ---------------------------------------------------------------------------

class TestAuthUser:
    def test_create_minimal(self) -> None:
        user = AuthUser(user_id="u1", email="a@b.com", name="A")
        assert user.user_id == "u1"
        assert user.roles == []
        assert user.event_id is None

    def test_create_full(self) -> None:
        user = AuthUser(
            user_id="u2",
            email="x@y.com",
            name="X",
            roles=["super_admin"],
            event_id="evt-1",
        )
        assert user.roles == ["super_admin"]
        assert user.event_id == "evt-1"


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

class TestProtocolConformance:
    def test_dev_provider_satisfies_protocol(self) -> None:
        assert isinstance(DevLoginProvider(), AuthProvider)

    def test_oidc_stub_satisfies_protocol(self) -> None:
        assert isinstance(OIDCProviderStub(), AuthProvider)


# ---------------------------------------------------------------------------
# DevLoginProvider tests
# ---------------------------------------------------------------------------

class TestDevLoginProvider:
    def test_create_token_returns_string(self, provider: DevLoginProvider) -> None:
        token = provider.create_token(email="dev@test.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_expected_claims(self, provider: DevLoginProvider) -> None:
        token = provider.create_token(
            email="dev@test.com",
            name="Dev",
            roles=["ops_lead"],
            event_id="evt-42",
        )
        payload = jwt.decode(token, _DEFAULT_SECRET, algorithms=[_DEFAULT_ALGORITHM])
        assert payload["email"] == "dev@test.com"
        assert payload["name"] == "Dev"
        assert payload["roles"] == ["ops_lead"]
        assert payload["event_id"] == "evt-42"
        assert payload["iss"] == "korex-dev"

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, provider: DevLoginProvider) -> None:
        token = provider.create_token(email="v@t.com", roles=["volunteer"])
        user = await provider.verify_token(token)
        assert user.email == "v@t.com"
        assert "volunteer" in user.roles

    @pytest.mark.asyncio
    async def test_expired_token_returns_error(self, provider: DevLoginProvider) -> None:
        # Issue a token that is already expired
        token = provider.create_token(email="x@t.com", expiry_minutes=-1)
        with pytest.raises(ValueError, match="Invalid or expired token"):
            await provider.verify_token(token)

    @pytest.mark.asyncio
    async def test_tampered_token_returns_error(self, provider: DevLoginProvider) -> None:
        token = provider.create_token(email="t@t.com")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(ValueError, match="Invalid or expired token"):
            await provider.verify_token(tampered)

    def test_blocked_in_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APP_ENV", "production")
        prod_provider = DevLoginProvider()
        with pytest.raises(RuntimeError, match="disabled outside development"):
            prod_provider.create_token(email="hack@evil.com")

    @pytest.mark.asyncio
    async def test_verify_blocked_in_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Create token in dev mode first
        provider = DevLoginProvider()
        token = provider.create_token(email="u@t.com")
        # Switch to production
        monkeypatch.setenv("APP_ENV", "production")
        with pytest.raises(RuntimeError, match="disabled outside development"):
            await provider.verify_token(token)

    def test_auto_generated_user_id(self, provider: DevLoginProvider) -> None:
        token = provider.create_token(email="a@b.com")
        payload = jwt.decode(token, _DEFAULT_SECRET, algorithms=[_DEFAULT_ALGORITHM])
        assert len(payload["sub"]) > 0  # UUID string

    def test_custom_expiry(self, provider: DevLoginProvider) -> None:
        token = provider.create_token(email="a@b.com", expiry_minutes=5)
        payload = jwt.decode(token, _DEFAULT_SECRET, algorithms=[_DEFAULT_ALGORITHM])
        iat = payload["iat"]
        exp = payload["exp"]
        assert (exp - iat) == 5 * 60


# ---------------------------------------------------------------------------
# OIDCProviderStub tests
# ---------------------------------------------------------------------------

class TestOIDCProviderStub:
    @pytest.mark.asyncio
    async def test_verify_raises(self) -> None:
        stub = OIDCProviderStub()
        with pytest.raises(NotImplementedError, match="OIDC_ISSUER_URL"):
            await stub.verify_token("any-token")

    @pytest.mark.asyncio
    async def test_login_url_raises(self) -> None:
        stub = OIDCProviderStub()
        with pytest.raises(NotImplementedError, match="OIDC_ISSUER_URL"):
            await stub.get_login_url("https://app/callback")


# ---------------------------------------------------------------------------
# FastAPI dependency + endpoint tests
# ---------------------------------------------------------------------------

class TestGetCurrentUser:
    def test_missing_token_returns_401(self, client: TestClient) -> None:
        resp = client.get("/protected")
        assert resp.status_code == 401

    def test_valid_token_returns_user(self, client: TestClient, provider: DevLoginProvider) -> None:
        token = provider.create_token(email="ok@t.com", roles=["ops_lead"])
        resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "ok@t.com"

    def test_invalid_token_returns_401(self, client: TestClient) -> None:
        resp = client.get("/protected", headers={"Authorization": "Bearer garbage.token.here"})
        assert resp.status_code == 401

    def test_expired_token_returns_401(self, client: TestClient, provider: DevLoginProvider) -> None:
        token = provider.create_token(email="exp@t.com", expiry_minutes=-1)
        resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401


class TestDevLoginEndpoint:
    def test_dev_login_success(self, client: TestClient) -> None:
        resp = client.post("/auth/dev/login", json={
            "email": "dev@test.com",
            "roles": ["event_commander"],
            "event_id": "evt-1",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_dev_login_blocked_in_production(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("APP_ENV", "production")
        resp = client.post("/auth/dev/login", json={"email": "x@t.com"})
        assert resp.status_code == 403
