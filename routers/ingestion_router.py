from fastapi import APIRouter, HTTPException, Depends
from services.ingestion_service import ingest_documents_for_chatbot
from uuid import UUID
from services.chatbot_service import get_chatbot_by_id
from middleware import get_current_user
from db.session import get_db
from sqlalchemy.orm import Session

ingestion_router = APIRouter()

@ingestion_router.post("/{customer_id}/{chatbot_id}/ingest")
def ingest_docs(
    customer_id: str,
    chatbot_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Ingest documents for a given chatbot. The path includes both
    customer_id and chatbot_id. The route is typically called as:
    POST /api/{customer_id}/{chatbot_id}/ingest
    """

    # 1) Validate the token's customer vs the route's customer_id
    token_customer_id = user.get("customer_id")
    if not token_customer_id:
        raise HTTPException(status_code=400, detail="Customer ID not found in token")

    if token_customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Token mismatch for this customer_id")

    # 2) Validate that the chatbot belongs to that customer
    chatbot = get_chatbot_by_id(chatbot_id=chatbot_id, db=db)
    if not chatbot or str(chatbot.customer_id) != customer_id:
        raise HTTPException(status_code=404, detail="Chatbot not found for this customer")

    # 3) Proceed with ingestion
    success = ingest_documents_for_chatbot(customer_id, str(chatbot_id))
    if success:
        return {"message": f"Documents ingested for customer '{customer_id}', chatbot '{chatbot_id}'"}
    else:
        raise HTTPException(status_code=500, detail="Ingestion failed")