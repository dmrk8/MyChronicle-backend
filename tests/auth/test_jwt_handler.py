from datetime import datetime, timedelta, timezone
import pytest
from jose import JWTError
from app.auth.jwt_handler import JWTHandler


@pytest.fixture
def jwt_handler():
    return JWTHandler(
        secret="test_secret_key",
        algorithm="HS256",
        issuer="test_issuer",
        audience="test_audience",
        expire_days=7,
    )


def test_jwt_handler_init_valid():
    handler = JWTHandler(
        secret="test_secret",
        algorithm="HS256",
        issuer="issuer",
        audience="audience",
        expire_days=7,
    )
    assert handler.secret_key == "test_secret"
    assert handler.algorithm == "HS256"


def test_jwt_handler_init_missing_secret_raises():
    with pytest.raises(ValueError, match="SECRET_KEY is required"):
        JWTHandler(
            secret="",
            algorithm="HS256",
            issuer="issuer",
            audience="audience",
            expire_days=7,
        )


def test_jwt_handler_init_missing_algorithm_raises():
    with pytest.raises(ValueError, match="ALGORITHM is required"):
        JWTHandler(
            secret="test_secret",
            algorithm="",
            issuer="issuer",
            audience="audience",
            expire_days=7,
        )


def test_jwt_handler_init_missing_issuer_raises():
    with pytest.raises(ValueError, match="ISSUER is required"):
        JWTHandler(
            secret="test_secret",
            algorithm="HS256",
            issuer="",
            audience="audience",
            expire_days=7,
        )


def test_jwt_handler_init_missing_audience_raises():
    with pytest.raises(ValueError, match="AUDIENCE is required"):
        JWTHandler(
            secret="test_secret",
            algorithm="HS256",
            issuer="issuer",
            audience="",
            expire_days=7,
        )


def test_create_access_token_returns_string(jwt_handler):
    token = jwt_handler.create_access_token("user123")
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid(jwt_handler):
    user_id = "user123"
    token = jwt_handler.create_access_token(user_id)
    verified_user_id = jwt_handler.verify_token(token)
    assert verified_user_id == user_id


def test_verify_token_empty_token_returns_none(jwt_handler):
    result = jwt_handler.verify_token("")
    assert result is None


def test_verify_token_invalid_token_returns_none(jwt_handler):
    result = jwt_handler.verify_token("invalid.token.here")
    assert result is None


def test_verify_token_tampered_token_returns_none(jwt_handler):
    user_id = "user123"
    token = jwt_handler.create_access_token(user_id)
    tampered_token = token[:-5] + "xxxxx"
    result = jwt_handler.verify_token(tampered_token)
    assert result is None


def test_generate_claims_with_default_expiry(jwt_handler):
    user_id = "user123"
    claims = jwt_handler.generate_claims(user_id)
    
    assert claims.sub == user_id
    assert claims.iss == jwt_handler.issuer
    assert claims.aud == jwt_handler.audience
    assert isinstance(claims.exp, int)
    assert claims.exp > 0


def test_generate_claims_with_custom_expiry(jwt_handler):
    user_id = "user123"
    expires_delta = timedelta(minutes=60)
    claims = jwt_handler.generate_claims(user_id, expires_delta=expires_delta)
    
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    expected_exp = now_timestamp + (60 * 60)
    
    assert abs(claims.exp - expected_exp) < 2


def test_generate_claims_with_different_users(jwt_handler):
    claims1 = jwt_handler.generate_claims("user123")
    claims2 = jwt_handler.generate_claims("user456")
    
    assert claims1.sub == "user123"
    assert claims2.sub == "user456"
    assert claims1.sub != claims2.sub


def test_multiple_handlers_independent(jwt_handler):
    other_handler = JWTHandler(
        secret="different_secret",
        algorithm="HS256",
        issuer="other_issuer",
        audience="other_audience",
        expire_days=14,
    )
    
    token = jwt_handler.create_access_token("user123")
    result = other_handler.verify_token(token)
    assert result is None
