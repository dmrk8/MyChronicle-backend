from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.uuid_helpers import new_uuid


class DBBase(BaseModel):
    id: UUID = Field(default_factory=new_uuid, alias="_id")
    created_at: datetime
    updated_at: datetime


class SoftDeleteDBBase(DBBase):
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
