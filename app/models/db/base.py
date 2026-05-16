from datetime import datetime
from typing import Optional


from pydantic import BaseModel, Field, field_validator
from uuid import UUID
import uuid


class DBBase(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: datetime
    updated_at: datetime


class SoftDeleteDBBase(DBBase):
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class MongoBase(BaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime
    
    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)
    
    
