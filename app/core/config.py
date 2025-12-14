from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongodb_uri: str = Field(description="MongoDB connection URI for the database cluster")
    database_name: str = Field(description="Name of the MongoDB database to use")
    review_collection: str = Field(description="Name of the MongoDB collection for storing reviews")
    user_collection: str = Field(description="Name of the MongoDB collection for storing user data")

    jwt_secret_key: str = Field(description="Secret key used for signing JWT tokens")
    jwt_algorithm: str = Field(description="Algorithm used for JWT encoding and decoding")
    jwt_expire_minutes: int = Field(description="Expiration time for JWT tokens in minutes")
    jwt_issuer: str = Field(description="Issuer claim for JWT tokens")
    jwt_audience: str = Field(description="Audience claim for JWT tokens")

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


def get_settings() -> Settings:
    return Settings()

