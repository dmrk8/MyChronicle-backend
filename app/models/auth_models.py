from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Literal


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ...,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, and one digit",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        ..., description="Refresh token to generate new access token", alias="refreshToken"
    )
    user_id: str = Field(
        ..., description="User ID associated with the refresh token", alias="userId"
    )

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


class UserInfo(BaseModel):
    id: str = Field(description="The unique ID of the user")
    username: str = Field(description="The username of the user")
    role: str = Field(description="The role of the user")
    created_at: datetime = Field(
        alias="createdAt", description="The date when the user was created"
    )
    updated_at: datetime = Field(
        alias="updatedAt", description="The date when the user was last updated"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
