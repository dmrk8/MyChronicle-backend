from enum import Enum
from typing import Any, Optional, Union, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timezone


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserDB(BaseModel):
    id: str
    username: str 
    hash_password: str
    created_at: datetime
    updated_at: datetime
    role: UserRole

class UserInsert(BaseModel):
    username: str
    hash_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    role: UserRole = UserRole.USER


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

class User(BaseModel):
    id: str
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    role: UserRole

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True, 
    )

