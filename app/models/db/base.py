from datetime import datetime
from typing import Optional


from pydantic import BaseModel, Field
from uuid import UUID
import uuid

class DBBase(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: datetime
    updated_at: datetime


class SoftDeleteDBBase(DBBase):
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
