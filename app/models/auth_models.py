from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ...,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, and one digit",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class AuthResponse(BaseModel):
    message: str = Field(..., description="Response message")
    access_token: str = Field(..., description="token")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)