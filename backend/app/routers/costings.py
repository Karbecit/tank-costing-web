from fastapi import APIRouter, HTTPException, Query

from app.repositories import costing_store as store
from app.schemas.costing_store import CostingDetail, CostingListItem, CostingSaveRequest

router = APIRouter(prefix="/api/costings", tags=["costings"])


@router.get("", response_model=list[CostingListItem])
def list_costings(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return store.list_costings(limit=limit, offset=offset)


@router.get("/{costing_id}", response_model=CostingDetail)
def get_costing(costing_id: int):
    row = store.get_costing(costing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Costing not found")
    return row


@router.post("", response_model=CostingDetail, status_code=201)
def create_costing(body: CostingSaveRequest):
    return store.save_costing(body.title, body.payload, body.customer_id)


@router.put("/{costing_id}", response_model=CostingDetail)
def update_costing(costing_id: int, body: CostingSaveRequest):
    row = store.save_costing(body.title, body.payload, body.customer_id, costing_id=costing_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Costing not found")
    return row


@router.delete("/{costing_id}", status_code=204)
def delete_costing(costing_id: int):
    if not store.delete_costing(costing_id):
        raise HTTPException(status_code=404, detail="Costing not found")
