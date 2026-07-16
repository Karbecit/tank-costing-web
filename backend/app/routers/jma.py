from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth.dependencies import CurrentUser, get_current_user, require_role
from app.repositories import costing_store as store
from app.services.jma_service import jma_bytes_to_payload

router = APIRouter(prefix="/api/jma", tags=["jma"])
_user = Annotated[CurrentUser, Depends(get_current_user)]
_editor = Annotated[CurrentUser, Depends(require_role("editor"))]


@router.post("/parse")
async def parse_jma(_user: _user, file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".jma"):
        raise HTTPException(status_code=400, detail="File must have .jma extension")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        payload = jma_bytes_to_payload(content)
    except (ValueError, IndexError, OSError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid .jma file: {exc}") from exc
    return {
        "title": payload.get("title"),
        "quote_ref": payload.get("quote_ref"),
        "company_name": payload.get("company_name"),
        "payload": payload,
    }


@router.post("/import", status_code=201)
async def import_jma(_editor: _editor, file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".jma"):
        raise HTTPException(status_code=400, detail="File must have .jma extension")
    content = await file.read()
    try:
        parsed = jma_bytes_to_payload(content)
    except (ValueError, IndexError, OSError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid .jma file: {exc}") from exc

    customer_id = None
    company = (parsed.pop("company_name", "") or "").strip()
    if company:
        matches = store.list_customers(q=company, limit=5)
        exact = next((c for c in matches if c["company_name"].lower() == company.lower()), None)
        if exact:
            customer_id = exact["id"]

    payload = {k: v for k, v in parsed.items() if k not in ("title", "quote_ref", "company_name")}
    title = parsed.get("title") or file.filename.replace(".jma", "")
    quote_ref = parsed.get("quote_ref") or None
    return store.save_costing(title, payload, customer_id, quote_ref=quote_ref)
