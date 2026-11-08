from typing import Optional
from pydantic import BaseModel


class DBOpContext(BaseModel):
    user_id: Optional[str] = None
    review_id : Optional[str] = None
    entry_id: Optional[str] = None
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    media_type: Optional[str] = None
    username: Optional[str] = None
    payload_type: Optional[str] = None
    
    operation: str 
    collection: str
