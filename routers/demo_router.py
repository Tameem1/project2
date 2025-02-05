# routers/demo_router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from db.session import get_db
from middleware import get_current_user
from services.chatbot_service import get_chatbot_by_id
# If using Option B (demo_usage table):
from models.demo_usage import DemoUsage

demo_router = APIRouter()

class DemoQueryRequest(BaseModel):
    chatbot_id: UUID
    question: str

class DemoQueryResponse(BaseModel):
    answer: str
    limit_reached: bool = False

@demo_router.post("/demo/query", response_model=DemoQueryResponse)
def demo_query(
    request: DemoQueryRequest,
    user: dict = Depends(get_current_user),  # must be logged in
    db: Session = Depends(get_db)
):
    """
    Allows user to test a specific chatbot in demo mode for up to 10 messages.
    """
    # 1) Validate that the chatbot belongs to them or is accessible.
    chatbot = get_chatbot_by_id(request.chatbot_id, db)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    # Optional: check if the user is the owner of the chatbot
    # if str(chatbot.customer_id) != user["customer_id"]:
    #     raise HTTPException(status_code=403, detail="Not your chatbot")

    # 2) Track or retrieve the usage count
    # ---- Option A (demo_message_count on Chatbot):
    # if chatbot.demo_message_count >= 10:
    #     return DemoQueryResponse(
    #         answer="You have reached the 10-message limit for this chatbot demo.",
    #         limit_reached=True
    #     )

    # ---- Increment if < 10
    # chatbot.demo_message_count += 1
    # db.commit()
    # db.refresh(chatbot)

    # ---- Option B (demo_usage table):
    user_id = user["user_id"]
    usage_record = (db.query(DemoUsage)
                      .filter(DemoUsage.user_id == user_id,
                              DemoUsage.chatbot_id == request.chatbot_id)
                      .first())

    if not usage_record:
        usage_record = DemoUsage(user_id=user_id, chatbot_id=request.chatbot_id, message_count=0)
        db.add(usage_record)
        db.commit()
        db.refresh(usage_record)

    # If usage_record.message_count >= 10, they've hit limit for this chatbot
    if usage_record.message_count >= 10:
        return DemoQueryResponse(
            answer="You have reached the 10-message limit for this chatbot demo.",
            limit_reached=True
        )

    # 3) If under limit, process the question
    #    (Use a smaller LLM or partial logic for your demo, or just a placeholder response.)
    bot_answer = f"[DEMO] Answer to '{request.question}' for chatbot {chatbot.name}"

    # 4) Increment usage
    usage_record.message_count += 1
    db.commit()
    db.refresh(usage_record)

    return DemoQueryResponse(
        answer=bot_answer,
        limit_reached=False
    )