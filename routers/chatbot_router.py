# routers/chatbot_router.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.chatbot_service import (
    create_chatbot, list_chatbots, get_chatbot_by_id
)
from middleware import get_current_user
from sqlalchemy.orm import Session
from db.session import get_db
from uuid import UUID
import secrets
import os

# Import models so we can delete associated data
from models.chatbot import Chatbot
from models.document import Document
from models.chat_history import ChatHistory

# If you have references to snippet responses, etc.
class ChatbotCreateRequest(BaseModel):
    name: str
    description: str = None  # Optional description

class ChatbotResponse(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: str

class ChatbotSnippetResponse(BaseModel):
    snippet: str

chatbot_router = APIRouter()

@chatbot_router.post("/chatbots", response_model=ChatbotResponse, tags=["Chatbots"])
def create_new_chatbot(
    request: ChatbotCreateRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    customer_id = user.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID not found in token")

    chatbot = create_chatbot(
        name=request.name,
        description=request.description,
        customer_id=customer_id,
        db=db
    )
    return ChatbotResponse(
        id=chatbot.id,
        name=chatbot.name,
        description=chatbot.description,
        created_at=chatbot.created_at.isoformat()
    )

@chatbot_router.get("/chatbots", response_model=list[ChatbotResponse], tags=["Chatbots"])
def get_chatbots(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    customer_id = user.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID not found in token")

    chatbots = list_chatbots(customer_id=customer_id, db=db)
    return [
        ChatbotResponse(
            id=cb.id,
            name=cb.name,
            description=cb.description,
            created_at=cb.created_at.isoformat()
        )
        for cb in chatbots
    ]

@chatbot_router.get("/chatbots/{chatbot_id}/snippet", response_model=ChatbotSnippetResponse, tags=["Chatbots"])
def get_chatbot_snippet(
    chatbot_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chatbot = get_chatbot_by_id(chatbot_id, db=db)
    if not chatbot or str(chatbot.customer_id) != user["customer_id"]:
        raise HTTPException(status_code=404, detail="Chatbot not found or not owned by you")
    if not chatbot.api_key:
        raise HTTPException(status_code=400, detail="Chatbot does not have an API key")

    snippet = f"""
<!-- Start of My Production Chatbot Embed -->
<script>
(function() {{
    window.myChatBotConfig = {{
        chatbotId: "{chatbot.id}",
        apiKey: "{chatbot.api_key}",
        design: {{
            position: "bottom-right",
            buttonColor: "#2c8ada"
        }}
    }};
    var s = document.createElement('script');
    s.src = "https://YOUR_DOMAIN.com/static/chatbot.js";
    document.head.appendChild(s);
}})();
</script>
<!-- End of My Production Chatbot Embed -->
"""
    return ChatbotSnippetResponse(snippet=snippet)

@chatbot_router.post("/chatbots/{chatbot_id}/rotate_key", tags=["Chatbots"])
def rotate_chatbot_api_key(
    chatbot_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chatbot = get_chatbot_by_id(chatbot_id, db)
    if not chatbot or str(chatbot.customer_id) != user["customer_id"]:
        raise HTTPException(status_code=404, detail="Chatbot not found or not owned by you")

    new_key = secrets.token_urlsafe(32)
    chatbot.api_key = new_key
    db.commit()
    db.refresh(chatbot)

    return {
        "chatbot_id": str(chatbot.id),
        "api_key": chatbot.api_key
    }

#
# NEW: DELETE A CHATBOT
#

@chatbot_router.delete("/chatbots/{chatbot_id}", tags=["Chatbots"])
def delete_chatbot(
    chatbot_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DELETE /api/chatbots/{chatbot_id}
    1) Checks chatbot belongs to user's customer_id
    2) Deletes the chatbot + all associated docs, chat history, vector store
    """
    # 1) Check ownership
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    if str(chatbot.customer_id) != user["customer_id"]:
        raise HTTPException(status_code=403, detail="Not your chatbot")

    # 2) Delete documents from DB (and disk)
    docs = db.query(Document).filter(Document.chatbot_id == chatbot_id).all()
    for doc in docs:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        db.delete(doc)

    # 3) Delete chat history
    db.query(ChatHistory).filter(ChatHistory.chatbot_id == chatbot_id).delete()

    # 4) Remove vector store on disk
    from utils.constants import get_vectorstore_path
    vector_path = get_vectorstore_path(str(chatbot.customer_id), str(chatbot_id))
    if os.path.isdir(vector_path):
        import shutil
        shutil.rmtree(vector_path)

    # 5) Finally delete the chatbot record
    db.delete(chatbot)
    db.commit()

    return {"message": "Chatbot deleted successfully."}