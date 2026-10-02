"""Attendance Credentials Issuer & Verifier (Sprint 7, S7-T4, ATT-001/002, TAD §18).

Issues and validates privacy-conscious, signed opaque QR / NFC tokens:
- HMAC-SHA256 signed payload
- Short-lived expiration (e.g. 12 hours)
- Rejects expired or forged signatures (threat: token forgery)
- Exposes no unnecessary participant PII in the token payload
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone

from packages.contracts.attendance import AttendanceCredential, CredentialType


class InvalidCredentialTokenError(Exception):
    """Raised when token signature is invalid, forged, or malformed."""
    pass


class ExpiredCredentialTokenError(Exception):
    """Raised when credential token has expired."""
    pass


class AttendanceCredentialService:
    """Issues and validates cryptographically signed event pass tokens."""

    def __init__(self, secret_env_var: str = "ATTENDANCE_SECRET_KEY") -> None:
        self.secret = os.environ.get(secret_env_var, "korex_attendance_token_secret_key").encode("utf-8")

    def issue_credential(
        self,
        participant_id: str,
        event_id: str = "evt_kbc2026",
        session_id: str | None = None,
        lifetime_hours: int = 12,
        credential_type: CredentialType = CredentialType.QR,
    ) -> AttendanceCredential:
        """Issue a short-lived signed credential."""
        expires_at_epoch = int(time.time()) + (lifetime_hours * 3600)
        expires_at_iso = datetime.fromtimestamp(expires_at_epoch, timezone.utc).isoformat()

        payload = {
            "pid": participant_id,
            "eid": event_id,
            "sid": session_id,
            "exp": expires_at_epoch,
            "typ": credential_type.value,
        }

        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        sig = hmac.new(self.secret, payload_bytes, hashlib.sha256).hexdigest()
        token = f"{base64.urlsafe_b64encode(payload_bytes).decode('utf-8')}.{sig}"

        return AttendanceCredential(
            token=token,
            event_id=event_id,
            session_id=session_id,
            participant_id=participant_id,
            expires_at=expires_at_iso,
            credential_type=credential_type,
        )

    def verify_token(self, token: str) -> dict:
        """Verify token cryptographic authenticity and expiration."""
        try:
            raw_payload_b64, signature = token.split(".")
            payload_bytes = base64.urlsafe_b64decode(raw_payload_b64.encode("utf-8"))
        except Exception as exc:
            raise InvalidCredentialTokenError("Malformed credential token format") from exc

        # Check signature
        expected_sig = hmac.new(self.secret, payload_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            raise InvalidCredentialTokenError("Forged or invalid credential token signature")

        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiry
        if payload.get("exp", 0) < int(time.time()):
            raise ExpiredCredentialTokenError("Credential token has expired")

        return payload
