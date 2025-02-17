# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routers.auth_router import auth_router
from routers.oauth_router import router as oauth_router
from routers.demo_router import demo_router
from routers.document_router import document_router
from routers.health_router import health_router
from routers.query_router import query_router
from routers.ingestion_router import ingestion_router
from routers.billing_router import billing_router
from routers.usage_router import usage_router
from routers.chatbot_router import chatbot_router
from routers.chat_history_router import chat_history_router
from routers.pricing_router import router as pricing_router  # New pricing router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(oauth_router)  # OAuth endpoints
app.include_router(pricing_router)  # Pricing endpoints
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(chatbot_router, prefix="/api", tags=["Chatbots"])
app.include_router(document_router, prefix="/api", tags=["Documents"])
app.include_router(query_router, prefix="/api", tags=["Query"])
app.include_router(ingestion_router, prefix="/api", tags=["Ingestion"])
app.include_router(billing_router, prefix="/api", tags=["Billing"])
app.include_router(usage_router, prefix="/api", tags=["Usage"])
app.include_router(chat_history_router, prefix="/api", tags=["Chat History"])
app.include_router(demo_router, prefix="/api", tags=["Demo"])

app.mount("/static", StaticFiles(directory="static"), name="static")
# run the backend: uvicorn main:app --reload
# run the backend with new modifications on the .env file : uvicorn main:app --reload --env-file .env
# run the frontend: npm start in the frontend folder
# Database changes: alembic revision --autogenerate -m "COMMENT-HERE"
# Database update: alembic upgrade head 