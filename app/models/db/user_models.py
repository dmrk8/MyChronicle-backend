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


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    new_password: Optional[str] = Field(
        None, alias="newPassword", description="New hashed password"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: Optional[str]):
        if v is not None:
            return validate_password_strength(v)
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserDB(SoftDeleteDBBase):
    username: str
    role: UserRole
    hash_password: str


class User(BaseModel):
    username: str
    role: UserRole

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    @classmethod
    def from_db(cls, user: UserDB) -> "User":
        return cls(**user.model_dump())
