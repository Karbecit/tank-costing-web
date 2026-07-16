from pydantic import BaseModel, EmailStr, Field


class SmtpSettingsPublic(BaseModel):
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True
    app_base_url: str = ""
    password_set: bool = False
    configured: bool = False


class SmtpSettingsUpdate(BaseModel):
    smtp_host: str = Field(..., min_length=1)
    smtp_port: int = Field(587, ge=1, le=65535)
    smtp_user: str = ""
    smtp_password: str | None = None
    smtp_from: str = Field(..., min_length=3)
    smtp_use_tls: bool = True
    app_base_url: str = ""


class SmtpTestRequest(BaseModel):
    to: EmailStr


class SendInviteRequest(BaseModel):
    password: str | None = None


class EmailQuoteRequest(BaseModel):
    to: EmailStr | None = None
    message: str | None = None
