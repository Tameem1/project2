# routers/document_router.py

from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from db.session import get_db
from middleware import get_current_user

# Models & Services
from models.chatbot import Chatbot
from models.document import Document
from services.document_service import handle_file_upload

document_router = APIRouter()

@document_router.post("/upload/{chatbot_id}")
def upload_document(
    chatbot_id: UUID,
    file: UploadFile,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /api/upload/{chatbot_id}
    1) Validate that the chatbot belongs to the current user's customer.
    2) Call handle_file_upload to save file & insert a DB record.
    """
    customer_id = user.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID not found in token")

    # Check if chatbot belongs to this customer
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot or str(chatbot.customer_id) != customer_id:
        raise HTTPException(status_code=404, detail="Chatbot not found or not yours")

    return handle_file_upload(
        file=file,
        customer_id=customer_id,
        chatbot_id=str(chatbot_id),
        db=db
    )

@document_router.get("/chatbots/{chatbot_id}/documents")
def list_documents(
    chatbot_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/chatbots/{chatbot_id}/documents
    Returns a list of documents for this chatbot, verifying ownership.
    """
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot or str(chatbot.customer_id) != user["customer_id"]:
        raise HTTPException(status_code=404, detail="Chatbot not found or not owned by you")

    docs = db.query(Document).filter(Document.chatbot_id == chatbot_id).all()
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "file_path": d.file_path,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None
        }
        for d in docs
    ]


@document_router.delete("/chatbots/{chatbot_id}/documents/{document_id}")
def delete_document(
    chatbot_id: UUID,
    document_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DELETE /api/chatbots/{chatbot_id}/documents/{document_id}
    Removes a document from DB (and optionally from disk).
    """
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot or str(chatbot.customer_id) != user["customer_id"]:
        raise HTTPException(status_code=404, detail="Chatbot not found or not owned by you")

    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.chatbot_id == chatbot_id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Optionally remove file from disk
    import os
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}