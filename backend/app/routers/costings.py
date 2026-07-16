from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import CurrentUser, get_current_user, require_role
from app.repositories import costing_store as store
from app.schemas.costing_store import CostingDetail, CostingListItem, CostingSaveRequest

router = APIRouter(prefix="/api/costings", tags=["costings"])
_user = Annotated[CurrentUser, Depends(get_current_user)]
_editor = Annotated[CurrentUser, Depends(require_role("editor"))]


@router.get("", response_model=list[CostingListItem])
def list_costings(
    _user: _user,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return store.list_costings(limit=limit, offset=offset)


@router.get("/{costing_id}", response_model=CostingDetail)
def get_costing(costing_id: int, _user: _user):
    row = store.get_costing(costing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Costing not found")
    return row


@router.post("", response_model=CostingDetail, status_code=201)
def create_costing(body: CostingSaveRequest, _user: _editor):
    return store.save_costing(
        body.title, body.payload, body.customer_id, quote_ref=body.quote_ref
    )


@router.put("/{costing_id}", response_model=CostingDetail)
def update_costing(costing_id: int, body: CostingSaveRequest, _user: _editor):
    row = store.save_costing(
        body.title,
        body.payload,
        body.customer_id,
        costing_id=costing_id,
        quote_ref=body.quote_ref,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Costing not found")
    return row


@router.delete("/{costing_id}", status_code=204)
def delete_costing(costing_id: int, _user: _editor):
    if not store.delete_costing(costing_id):
        raise HTTPException(status_code=404, detail="Costing not found")
