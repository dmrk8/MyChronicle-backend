# tests/test_config.py
import pytest
from pydantic import ValidationError
from app.core.config import Settings

def test_valid_settings():
    settings = Settings(
        env="TEST",
        log_level="DEBUG",
        service_name="TestService",
        mongodb_uri="mongodb://localhost:27017",
        database_name="testdb",
        review_collection="Reviews",
        user_collection="Users",
        user_media_entry_collection="UserMediaEntries",
        jwt_secret_key="supersecretkey",
        jwt_algorithm="HS256",
        jwt_access_token_expire_days=60,
        jwt_issuer="TESTISSUER",
        jwt_audience="TESTAUDIENCE",
        tmdb_api_key="key",
        tmdb_access_token="token",
    )
    assert settings.env == "TEST"
    assert settings.service_name == "TestService"
    assert settings.database_name == "testdb"

def test_invalid_samesite_raises():
    with pytest.raises(ValidationError):
        Settings(
            env="TEST",
            log_level="DEBUG",
            service_name="TestService",
            mongodb_uri="mongodb://localhost:27017",
            database_name="testdb",
            review_collection="Reviews",
            user_collection="Users",
            user_media_entry_collection="UserMediaEntries",
            jwt_secret_key="supersecretkey",
            jwt_algorithm="HS256",
            jwt_access_token_expire_days=60,
            jwt_issuer="TESTISSUER",
            jwt_audience="TESTAUDIENCE",
            tmdb_api_key="key",
            tmdb_access_token="token",
            samesite="invalid",  # type: ignore
        )

def test_allow_origins_parsed_correctly():
    settings = Settings(
        env="TEST",
        log_level="DEBUG",
        service_name="TestService",
        mongodb_uri="mongodb://localhost:27017",
        database_name="testdb",
        review_collection="Reviews",
        user_collection="Users",
        user_media_entry_collection="UserMediaEntries",
        jwt_secret_key="supersecretkey",
        jwt_algorithm="HS256",
        jwt_access_token_expire_days=60,
        jwt_issuer="TESTISSUER",
        jwt_audience="TESTAUDIENCE",
        tmdb_api_key="key",
        tmdb_access_token="token",
        allow_origins_str="https://linazze.com,http://localhost:5173",
        samesite="lax",
    )
    assert "https://linazze.com" in settings.allow_origins
    assert "http://localhost:5173" in settings.allow_origins
