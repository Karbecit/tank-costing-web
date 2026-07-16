from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class UserPublic(BaseModel):
    id: int
    email: str
    display_name: str
    role: str
    is_active: bool
    mfa_enabled: bool = False
    created_at: str
    updated_at: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class MfaRequiredResponse(BaseModel):
    mfa_required: bool = True
    mfa_token: str
    trust_allowed: bool = True


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    code: str
    trust_device: bool = False


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=10)


class MfaConfirmRequest(BaseModel):
    code: str


class MfaSetupResponse(BaseModel):
    secret: str
    otpauth_uri: str


class AuditEntry(BaseModel):
    id: int
    actor_id: int | None = None
    actor_email: str | None = None
    action: str
    target_type: str | None = None
    target_id: str | None = None
    detail: str | None = None
    created_at: str
