"""Password hashing (PBKDF2) and HS256 JWT access tokens using only the standard library."""
import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict

PBKDF2_ITERATIONS = 200_000


class InvalidTokenError(Exception):
    pass


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${_b64e(salt)}${_b64e(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _b64d(salt), int(iterations))
    return hmac.compare_digest(_b64e(digest), expected)


def create_access_token(subject: str, secret: str, ttl_seconds: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + ttl_seconds}
    signing_input = ".".join(
        _b64e(json.dumps(part, separators=(",", ":")).encode()) for part in (header, payload)
    )
    signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64e(signature)}"


def decode_access_token(token: str, secret: str) -> Dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        raise InvalidTokenError("Malformed token")
    expected = hmac.new(
        secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256
    ).digest()
    if not hmac.compare_digest(_b64e(expected), signature_b64):
        raise InvalidTokenError("Invalid token signature")
    try:
        header = json.loads(_b64d(header_b64))
        payload = json.loads(_b64d(payload_b64))
    except (ValueError, json.JSONDecodeError):
        raise InvalidTokenError("Malformed token")
    if header.get("alg") != "HS256":
        raise InvalidTokenError("Unsupported token algorithm")
    if int(payload.get("exp", 0)) < int(time.time()):
        raise InvalidTokenError("Token expired")
    return payload
