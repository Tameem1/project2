# routers/billing_router.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.billing_service import create_invoice, get_invoices, update_invoice_status
from middleware import get_current_user
from db.session import get_db
from sqlalchemy.orm import Session
import uuid

billing_router = APIRouter()

class InvoiceCreateRequest(BaseModel):
    amount: float
    due_date: str  # ISO format

@billing_router.post("/{customer_id}/invoices", tags=["Billing"])
def create_new_invoice(
    customer_id: str,
    request: InvoiceCreateRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["customer_id"] != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this customer data")
    
    invoice = create_invoice(
        db=db,
        customer_id=uuid.UUID(customer_id),
        amount=request.amount
    )
    return {"invoice_number": invoice.invoice_number, "status": invoice.status}

@billing_router.get("/{customer_id}/invoices", tags=["Billing"])
def list_invoices(
    customer_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["customer_id"] != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this customer data")
    
    invoices = get_invoices(db, uuid.UUID(customer_id))
    return {"invoices": invoices}

class InvoiceUpdateRequest(BaseModel):
    status: str

@billing_router.patch("/invoices/{invoice_id}", tags=["Billing"])
def update_invoice(
    invoice_id: str,
    request: InvoiceUpdateRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = update_invoice_status(db, uuid.UUID(invoice_id), request.status)
    return {"invoice_number": invoice.invoice_number, "status": invoice.status}