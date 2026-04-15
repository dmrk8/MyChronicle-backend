from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.auth.password_validation import validate_password_strength


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserInsert(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER
    hash_password: str = Field(..., description="Hashed password")
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values):
        now = datetime.now(timezone.utc)
        values.setdefault("created_at", now)
        values.setdefault("updated_at", now)
        return values


class UserDB(BaseModel):
    id: str = Field(..., alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER
    hash_password: str
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    hash_password: Optional[str] = Field(None, description="Hashed password")

    def to_update_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True, by_alias=False)
        if not data:
            raise ValueError("No fields provided for update")
        data["updated_at"] = datetime.now(timezone.utc)
        return data


class UpdatePassword(BaseModel):
    current_password: str = Field(..., alias="currentPassword")
    new_password: str = Field(..., alias="newPassword")

    @field_validator("new_password")
    def validate_password(cls, v: str):
        return validate_password_strength(v)

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UpdateUsername(BaseModel):
    username: str = Field(...)


class User(BaseModel):
    id: str
    username: str
    role: UserRole
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    @classmethod
    def from_db(cls, user: UserDB) -> "User":
        return cls(**user.model_dump())
