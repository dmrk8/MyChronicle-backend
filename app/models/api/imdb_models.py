from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class IMDBAggregateRating(BaseModel):
    rating_count: int = Field(..., alias="ratingCount")
    rating_value: float = Field(..., alias="ratingValue")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IMDBShortResponse(BaseModel):
    aggregate_rating: Optional[IMDBAggregateRating] = Field(None, alias="aggregateRating")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IMDBResponse(BaseModel):
    ok: bool
    error_code: int = Field(..., alias="errorCode")
    description: str
    short: IMDBShortResponse

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
