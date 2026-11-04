"""
Unit tests for token_service. No database or HTTP client needed.
"""
import datetime
import uuid

import jwt
import pytest

from app.config import settings
from app.services.token_service import create_token, decode_token


# ---------------------------------------------------------------------------
# create_token
# ---------------------------------------------------------------------------


def test_create_token_returns_string_and_future_expiry() -> None:
    token, expires_at = create_token(uuid.uuid4())

    assert isinstance(token, str)
    assert len(token) > 0
    assert isinstance(expires_at, datetime.datetime)
    assert expires_at > datetime.datetime.now(tz=datetime.timezone.utc)


def test_create_token_expiry_matches_config() -> None:
    before = datetime.datetime.now(tz=datetime.timezone.utc)
    _, expires_at = create_token(uuid.uuid4())
    after = datetime.datetime.now(tz=datetime.timezone.utc)

    expected_delta = datetime.timedelta(hours=settings.jwt_expiry_hours)
    assert before + expected_delta <= expires_at <= after + expected_delta


def test_jti_is_unique_per_token() -> None:
    user_id = uuid.uuid4()
    token_a, _ = create_token(user_id)
    token_b, _ = create_token(user_id)

    payload_a = decode_token(token_a)
    payload_b = decode_token(token_b)

    assert payload_a["jti"] != payload_b["jti"]


# ---------------------------------------------------------------------------
# decode_token — happy path
# ---------------------------------------------------------------------------


def test_decode_returns_correct_sub() -> None:
    user_id = uuid.uuid4()
    token, _ = create_token(user_id)

    payload = decode_token(token)

    assert payload["sub"] == str(user_id)


def test_decode_payload_contains_required_claims() -> None:
    token, _ = create_token(uuid.uuid4())
    payload = decode_token(token)

    for claim in ("sub", "jti", "iat", "exp"):
        assert claim in payload, f"Missing claim: {claim}"


def test_jti_is_valid_uuid4() -> None:
    token, _ = create_token(uuid.uuid4())
    payload = decode_token(token)

    parsed = uuid.UUID(payload["jti"])
    assert parsed.version == 4


# ---------------------------------------------------------------------------
# decode_token — error cases
# ---------------------------------------------------------------------------


def test_decode_expired_token_raises() -> None:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    expired_payload = {
        "sub": str(uuid.uuid4()),
        "jti": str(uuid.uuid4()),
        "iat": now - datetime.timedelta(hours=2),
        "exp": now - datetime.timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired_token)


def test_decode_wrong_secret_raises() -> None:
    payload = {
        "sub": str(uuid.uuid4()),
        "jti": str(uuid.uuid4()),
        "iat": datetime.datetime.now(tz=datetime.timezone.utc),
        "exp": datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(hours=1),
    }
    token_wrong_secret = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token_wrong_secret)


def test_decode_tampered_token_raises() -> None:
    token, _ = create_token(uuid.uuid4())
    # Corrupt the signature (last segment)
    parts = token.split(".")
    parts[-1] = parts[-1][:-4] + "XXXX"
    tampered = ".".join(parts)

    with pytest.raises(jwt.InvalidTokenError):
        decode_token(tampered)


def test_decode_garbage_string_raises() -> None:
    with pytest.raises(jwt.InvalidTokenError):
        decode_token("not.a.jwt")
