from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.auth.dependencies import CurrentUser, get_current_user, require_role
from app.jma.writer import write_jma_bytes
from app.repositories import costing_store as store
from app.schemas.costing_store import CostingDetail, CostingListItem, CostingSaveRequest
from app.schemas.settings import EmailQuoteRequest
from app.services import email_templates
from app.services.email_service import EmailError, send_email_with_attachment
from app.services.pdf_service import generate_quote_pdf

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


@router.get("/{costing_id}/quote.pdf")
def download_quote_pdf(costing_id: int, _user: _user):
    row = store.get_costing(costing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Costing not found")
    customer = store.get_customer(row["customer_id"]) if row.get("customer_id") else None
    pdf = generate_quote_pdf(
        title=row["title"],
        quote_ref=row.get("quote_ref"),
        payload=row["payload"],
        customer=customer,
    )
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in row["title"])[:60]
    filename = f"{safe_name or 'quote'}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{costing_id}/export.jma")
def export_jma(costing_id: int, _user: _user):
    row = store.get_costing(costing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Costing not found")
    customer = store.get_customer(row["customer_id"]) if row.get("customer_id") else None
    data = write_jma_bytes(
        row["payload"],
        title=row["title"],
        quote_ref=row.get("quote_ref"),
        company_name=(customer or {}).get("company_name") or "",
    )
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in row["title"])[:60]
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{safe or "costing"}.jma"'},
    )


@router.post("/{costing_id}/email-quote", status_code=204)
def email_quote(costing_id: int, body: EmailQuoteRequest, _user: _editor):
    row = store.get_costing(costing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Costing not found")
    customer = store.get_customer(row["customer_id"]) if row.get("customer_id") else None
    recipient = body.to or (customer or {}).get("email")
    if not recipient:
        raise HTTPException(
            status_code=400, detail="No recipient — set customer email or provide to"
        )
    pdf = generate_quote_pdf(
        title=row["title"],
        quote_ref=row.get("quote_ref"),
        payload=row["payload"],
        customer=customer,
    )
    cust = customer or {}
    subject, text = email_templates.quote_email(
        customer_name=cust.get("contact_name") or cust.get("company_name") or "",
        title=row["title"],
        quote_ref=row.get("quote_ref"),
    )
    if body.message:
        text = f"{body.message.strip()}\n\n{text}"
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in row["title"])[:60]
    try:
        send_email_with_attachment(
            to=recipient,
            subject=subject,
            body=text,
            attachment_bytes=pdf,
            attachment_name=f"{safe or 'quote'}.pdf",
        )
    except EmailError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
