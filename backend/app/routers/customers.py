from fastapi import APIRouter, HTTPException, Query

from app.repositories import costing_store as store
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    q: str | None = None,
):
    return store.list_customers(limit=limit, offset=offset, q=q)


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(body: CustomerCreate):
    return store.create_customer(body.model_dump())


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    row = store.get_customer(customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, body: CustomerUpdate):
    row = store.update_customer(customer_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    if not store.delete_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
