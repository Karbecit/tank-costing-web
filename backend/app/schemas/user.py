from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(..., min_length=3)
    display_name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=10)
    role: str = Field(default="editor", pattern="^(admin|editor|viewer)$")


class UserUpdate(BaseModel):
    display_name: str | None = None
    role: str | None = Field(default=None, pattern="^(admin|editor|viewer)$")
    is_active: bool | None = None


class PasswordReset(BaseModel):
    password: str = Field(..., min_length=10)
