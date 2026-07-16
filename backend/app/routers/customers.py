from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import CurrentUser, get_current_user, require_role
from app.repositories import costing_store as store
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(prefix="/api/customers", tags=["customers"])
_user = Annotated[CurrentUser, Depends(get_current_user)]
_editor = Annotated[CurrentUser, Depends(require_role("editor"))]


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    _user: _user,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    q: str | None = None,
):
    return store.list_customers(limit=limit, offset=offset, q=q)


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(body: CustomerCreate, _user: _editor):
    return store.create_customer(body.model_dump())


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, _user: _user):
    row = store.get_customer(customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, body: CustomerUpdate, _user: _editor):
    row = store.update_customer(customer_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, _user: _editor):
    if not store.delete_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
