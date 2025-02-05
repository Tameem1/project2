# routers/document_router.py
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from middleware import get_current_user
from services.document_service import handle_file_upload
from services.chatbot_service import get_chatbot_by_id
from db.session import get_db
from sqlalchemy.orm import Session
from uuid import UUID

document_router = APIRouter()

@document_router.post("/upload/{chatbot_id}")
def upload_document(
    chatbot_id: UUID,
    file: UploadFile,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an individual file for a specific chatbot. Validates that the chatbot
    belongs to the authenticated user's customer before proceeding.
    """
    customer_id = user.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID not found in token")

    # Validate that the chatbot belongs to the customer
    chatbot = get_chatbot_by_id(chatbot_id=chatbot_id, db=db)
    if not chatbot or str(chatbot.customer_id) != customer_id:
        raise HTTPException(status_code=404, detail="Chatbot not found for this customer")

    # Proceed with file upload
    return handle_file_upload(file, customer_id, str(chatbot_id))