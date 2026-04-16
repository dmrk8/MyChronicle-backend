from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.auth.password_validation import validate_password_strength


class CredentialsBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RegisterRequest(CredentialsBase):
    @field_validator("password")
    def validate_password(cls, v: str):
        return validate_password_strength(v)
