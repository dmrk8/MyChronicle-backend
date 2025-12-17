from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = Field(description="Environment (e.g., DEV, PROD)")
    log_level: str = Field(description="Logging level (e.g., DEBUG, INFO)")
    service_name: str = Field(description="Name of the service/application")

    mongodb_uri: str = Field(description="MongoDB connection URI for the database cluster")
    database_name: str = Field(description="Name of the MongoDB database to use")
    review_collection: str = Field(description="Name of the MongoDB collection for storing reviews")
    user_collection: str = Field(description="Name of the MongoDB collection for storing user data")
    user_media_entry_collection: str = Field(
        description="Name of the MongoDB collection for storing user media entries"
    )

    jwt_secret_key: str = Field(description="Secret key used for signing JWT tokens")
    jwt_algorithm: str = Field(description="Algorithm used for JWT encoding and decoding")
    jwt_access_token_expire_minutes: int = Field(
        description="Expiration time for JWT tokens in minutes"
    )
    jwt_issuer: str = Field(description="Issuer claim for JWT tokens")
    jwt_audience: str = Field(description="Audience claim for JWT tokens")
    jwt_refresh_token_expire_days_default: int = Field(
        description="Default expiration for refresh tokens in days (non-remember me)"
    )
    jwt_refresh_token_expire_days_remember: int = Field(
        description="Expiration for refresh tokens in days (with remember me)"
    )

    redis_host: str = Field(description="Hostname for the Redis server")
    redis_port: int = Field(description="Port number for the Redis server")
    redis_username: str = Field(description="Username for Redis authentication")
    redis_password: str = Field(description="Password for Redis authentication")

    api_url: str = Field(description="Base URL for the API endpoints")
    tmdb_api_key: str = Field(description="API key for The Movie Database (TMDB)")
    tmdb_access_token: str = Field(description="Access token for TMDB API")
    twitch_client_id: str = Field(description="Client ID for Twitch API")
    twitch_client_secret: str = Field(description="Client secret for Twitch API")
    igdb_access_token: str = Field(description="Access token for IGDB API")
    igdb_expires_in: int = Field(description="Expiration time for IGDB access token in seconds")
    steam_web_api_key: str = Field(description="API key for Steam Web API")
    omdb_api_key: str = Field(description="API key for Open Movie Database (OMDB)")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore
    return _settings
