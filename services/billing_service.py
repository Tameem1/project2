# services/billing_service.py
from sqlalchemy.orm import Session
from models.billing import Billing
from models.customer import Customer
from datetime import datetime, timedelta
import uuid

def create_invoice(db: Session, customer_id: uuid.UUID, amount: float):
    invoice = Billing(
        customer_id=customer_id,
        invoice_number=str(uuid.uuid4()),
        amount=amount,
        status="Pending",
        issued_at=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=30)
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

def get_invoices(db: Session, customer_id: uuid.UUID):
    return db.query(Billing).filter(Billing.customer_id == customer_id).all()

def update_invoice_status(db: Session, invoice_id: uuid.UUID, status: str):
    invoice = db.query(Billing).filter(Billing.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = status
    db.commit()
    db.refresh(invoice)
    return invoice