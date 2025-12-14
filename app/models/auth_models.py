from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional, Literal
from datetime import datetime


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ...,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, and one digit",
    )
    is_remember_me: bool = Field(
        default=False,
        description="Whether to remember the user for extended session",
        alias="isRememberMe",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token to generate new access token", alias="refreshToken")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AuthResponse(BaseModel):
    message: str = Field(..., description="Response message")
    access_token: str = Field(..., description="JWT access token", alias="accessToken")
    refresh_token: str = Field(..., description="JWT refresh token", alias="refreshToken")
    token_type: str = Field(default="bearer", description="Token type", alias="tokenType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Claims(BaseModel):
    sub: str = Field(..., description="Subject (e.g., user ID or username)")
    exp: int = Field(..., description="Expiration time (Unix timestamp)")
    iss: Optional[str] = Field(None, description="Issuer")
    aud: Optional[str] = Field(None, description="Audience")
    type: Literal["access", "refresh"] = Field(..., description="Token type: 'access' or 'refresh'")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
