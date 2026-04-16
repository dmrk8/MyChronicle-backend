

from typing import Optional

from pydantic import BaseModel, Field


class Claims(BaseModel):
    sub: str = Field(..., description="Subject (e.g., user ID or username)")
    exp: int = Field(..., description="Expiration time (Unix timestamp)")
    iss: Optional[str] = Field(None, description="Issuer")
    aud: Optional[str] = Field(None, description="Audience")
    

