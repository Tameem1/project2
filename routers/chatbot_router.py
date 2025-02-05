# routers/chatbot_router.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.chatbot_service import create_chatbot, list_chatbots, get_chatbot_by_id
from middleware import get_current_user
from sqlalchemy.orm import Session
from db.session import get_db
from uuid import UUID
import secrets
chatbot_router = APIRouter()

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
    
@chatbot_router.post("/chatbots", response_model=ChatbotResponse, tags=["Chatbots"])
def create_new_chatbot(
    request: ChatbotCreateRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new chatbot for the authenticated user's customer.
    """
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
    """
    Retrieves all chatbots associated with the authenticated user's customer.
    """
    customer_id = user.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID not found in token")
    
    chatbots = list_chatbots(customer_id=customer_id, db=db)
    
    return [
        ChatbotResponse(
            id=chatbot.id,
            name=chatbot.name,
            description=chatbot.description,
            created_at=chatbot.created_at.isoformat()
        )
        for chatbot in chatbots
    ]

# routers/chatbot_router.py

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
        chatbotId: "{chatbot.id}",  // <-- Add the chatbot ID here
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

@chatbot_router.post("/chatbots/{chatbot_id}/rotate_key")
def rotate_chatbot_api_key(
    chatbot_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows the authenticated user (owner) to rotate the chatbot's API key.
    Returns the new key in response.
    """
    chatbot = get_chatbot_by_id(chatbot_id, db)
    if not chatbot or str(chatbot.customer_id) != user["customer_id"]:
        raise HTTPException(status_code=404, detail="Chatbot not found or not owned by you")
    
    # Generate new key
    new_key = secrets.token_urlsafe(32)
    chatbot.api_key = new_key
    db.commit()
    db.refresh(chatbot)

    return {
        "chatbot_id": str(chatbot.id),
        "api_key": chatbot.api_key
    }