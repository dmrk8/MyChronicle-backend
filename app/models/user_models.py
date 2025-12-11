from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserDB(BaseModel):
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)
    hash_password: str = Field(..., min_length=8, alias="hashPassword")
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")
    role: UserRole = UserRole.USER

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ...,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, and one digit",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ...,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, and one digit",
    )
    role: UserRole = UserRole.USER

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


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one symbol",
    )
    role: Optional[UserRole] = None

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
