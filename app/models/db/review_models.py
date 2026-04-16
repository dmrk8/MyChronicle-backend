from datetime import datetime, timezone
from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class ReviewBase(BaseModel):
    review: Optional[str] = Field(
        None,
        max_length=5000,
    )
    rating: Optional[float] = Field(
        None,
        ge=0,
        le=10,
    )
    review_progress: Optional[int] = Field(
        None,
        ge=0,
        alias="reviewProgress",
        description="The chapter or episode progress at the time the review was written",
    )
    written_at: Optional[datetime] = Field(
        None,
        alias="writtenAt",
        description="The date when the user wrote the review",
    )

    @field_validator("written_at")
    @classmethod
    def validate_written_at(cls, v: datetime | None):
        if v is None:
            return v
        now = datetime.now(timezone.utc)
        candidate = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if candidate > now:
            raise ValueError("Written at date cannot be in the future")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewUpdate(ReviewBase):
    def to_update_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True, by_alias=False)

        if not data:
            raise ValueError("No fields provided for update")
        data["updated_at"] = datetime.now(timezone.utc)
        return data


class ReviewCreate(ReviewBase):
    pass


class ReviewInsert(ReviewBase):
    user_media_entry_id: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str = Field(...)
    
    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values):
        now = datetime.now(timezone.utc)
        values.setdefault("created_at", now)
        values.setdefault("updated_at", now)
        return values


class ReviewDB(ReviewBase):
    id: str = Field(..., alias="_id")
    user_media_entry_id: str = Field(...)
    user_id: str = Field(...)

    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)


class Review(ReviewBase):
    id: str
    user_media_entry_id: str = Field(..., alias="userMediaEntryId")
    user_id: str = Field(..., alias="userId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    @classmethod
    def from_db(cls, review: ReviewDB) -> "Review":
        return cls(**review.model_dump())
