from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = Field(description="Environment (e.g., DEV, PROD)")
    log_level: str = Field(description="Logging level (e.g., DEBUG, INFO)")
    service_name: str = Field(description="Name of the service/application")

    mongodb_uri: str = Field(
        description="MongoDB connection URI for the database cluster"
    )
    database_name: str = Field(description="Name of the MongoDB database to use")
    review_collection: str = Field(
        description="Name of the MongoDB collection for storing reviews"
    )
    user_collection: str = Field(
        description="Name of the MongoDB collection for storing user data"
    )
    user_media_entry_collection: str = Field(
        description="Name of the MongoDB collection for storing user media entries"
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL (format: redis://[:password]@host:port/db)",
    )

    jwt_secret_key: str = Field(description="Secret key used for signing JWT tokens")
    jwt_algorithm: str = Field(
        description="Algorithm used for JWT encoding and decoding"
    )
    jwt_issuer: str = Field(description="Issuer claim for JWT tokens")
    jwt_audience: str = Field(description="Audience claim for JWT tokens")
    jwt_access_token_expire_days: int = Field(
        description="Default expiration for refresh tokens in days"
    )

    tmdb_api_key: str = Field(description="API key for The Movie Database (TMDB)")
    tmdb_access_token: str = Field(description="Access token for TMDB API")

    # twitch_client_id: str = Field(description="Client ID for Twitch API")
    # twitch_client_secret: str = Field(description="Client secret for Twitch API")
    # igdb_access_token: str = Field(description="Access token for IGDB API")
    # igdb_expires_in: int = Field(
    #    description="Expiration time for IGDB access token in seconds"
    # )#
    # steam_web_api_key: str = Field(description="API key for Steam Web API")
    # omdb_api_key: str = Field(description="API key for Open Movie Database (OMDB)")

    allow_origins: str = Field(
        default="http://localhost:5173",
        description="Allowed origin for CORS",
    )

    samesite: Literal["lax", "strict", "none"] = Field(
        default="none", description="SameSite attribute for cookies (none, lax, strict)"
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore
    return _settings
