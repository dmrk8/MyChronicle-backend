from enum import Enum
from typing import Any, Optional, Union, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timezone


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserDB(BaseModel):
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)
    hash_password: str = Field(..., min_length=8, alias="hashPassword")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt"
    )
    role: UserRole = UserRole.USER

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ...,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, and one digit",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Password must contain at least one symbol")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one symbol",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if v is None:
            return v
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Password must contain at least one symbol")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    hash_password: Optional[str] = Field(None, description="Hashed password")
    role: Optional[UserRole] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserResponse(BaseModel):
    message: str = Field(..., description="Response message")

    user_id: Optional[str] = Field(None, alias="userId", description="User ID if applicable")
   
    data: Optional[Any] = Field(
        None, description="Additional data, such as review lists or details"
    )
    acknowledged: Optional[bool] = Field(
        None, description="Whether the operation was acknowledged by the database"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
