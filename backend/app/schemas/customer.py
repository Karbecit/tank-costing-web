from pydantic import BaseModel, Field


class CustomerBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    billing_address: str | None = None
    delivery_address: str | None = None
    town: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = "Australia"
    notes: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    company_name: str | None = Field(None, min_length=1, max_length=200)
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    billing_address: str | None = None
    delivery_address: str | None = None
    town: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    notes: str | None = None


class CustomerResponse(CustomerBase):
    id: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
