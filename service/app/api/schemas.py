from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.rules import PHONE_PATTERN, validate_password_strength


class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)

    @field_validator("password")
    @classmethod
    def _strong_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @field_validator("first_name", "last_name")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("phone")
    @classmethod
    def _valid_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not value.strip():
            return None
        if not PHONE_PATTERN.match(value.strip()):
            raise ValueError("must be a valid phone number")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class CustomerResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    customer: CustomerResponse


class ErrorResponse(BaseModel):
    detail: str
