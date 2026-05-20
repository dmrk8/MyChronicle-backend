from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.auth.password_validation import validate_password_strength
from app.models.db.base import SoftDeleteDBBase


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserInsert(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER
    hash_password: str = Field(..., description="Hashed password")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    hash_password: Optional[str] = Field(None, description="Hashed password")


class UsernameUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class PasswordUpdateRequest(BaseModel):
    current_password: str = Field(
        ..., alias="currentPassword", description="Current hashed password"
    )
    new_password: str = Field(
        ..., alias="newPassword", description="New hashed password"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str):
        return validate_password_strength(v)

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserDB(SoftDeleteDBBase):
    username: str
    role: UserRole
    hash_password: str


class User(BaseModel):
    username: str
    role: UserRole
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

   
