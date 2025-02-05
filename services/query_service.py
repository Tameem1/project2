# services/query_service.py

import logging
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_fireworks import ChatFireworks

from utils.constants import CHROMA_SETTINGS, get_vectorstore_path, MODEL_ID
from utils.embedding_utils import get_embeddings
from services.usage_service import consume_tokens
from services.chat_history_service import log_chat
from sqlalchemy.orm import Session
from db.session import get_db
from fastapi import Depends

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def initialize_prompt() -> tuple[PromptTemplate, ConversationBufferMemory]:
    """
    Creates a PromptTemplate and a ConversationBufferMemory instance.
    """
    template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, 
    don't try to make up an answer.

    {context}

    {history}
    Question: {question}
    Helpful Answer:"""

    prompt = PromptTemplate(
        input_variables=["history", "context", "question"], 
        template=template
    )
    memory = ConversationBufferMemory(
        input_key="question", 
        memory_key="history"
    )
    return prompt, memory

def process_query(question: str, customer_id: str, chatbot_id: str, user_id: str, db: Session) -> dict:
    """
    Retrieves relevant chunks from the vector store, consumes tokens, logs chat, and generates a response.
    """
    try:
        logging.info(f"Processing query: {question}")

        # 1. Consume tokens (assuming each query consumes a fixed number of tokens)
        tokens_per_query = 100  # Define based on your usage policy
        consume_tokens(db, customer_id, tokens_per_query)

        # 2. Use the same embeddings as ingestion.
        embeddings = get_embeddings()

        # 3. Build the path to the correct vector store
        persist_dir = get_vectorstore_path(customer_id, chatbot_id)
        logging.info(f"Using vector store at: {persist_dir}")

        # 4. Initialize Chroma with the correct directory
        db_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
            client_settings=CHROMA_SETTINGS,
        )
        retriever = db_store.as_retriever()
        logging.info("Retriever loaded successfully.")

        # 5. Initialize Fireworks LLM
        llm = ChatFireworks(
            api_key="fw_3ZfGXeDhjJfUxVHUVRBDfMeU",  # Securely store API keys
            model=MODEL_ID,
            temperature=0.7,
            max_tokens=1500,
            top_p=1.0,
        )
        logging.info("Fireworks.ai LLM initialized successfully.")

        # 6. Set up the RetrievalQA chain with a prompt and memory
        prompt, memory = initialize_prompt()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )

        # 7. Run the query
        response = qa_chain(question)
        answer = response.get("result", "No answer available.")
        source_docs = response.get("source_documents", [])

        logging.info("Query processed successfully.")

        # 8. Log the chat history
        log_chat(db, chatbot_id, user_id, question, answer)

        return {
            "answer": answer,
            "sources": [doc.metadata.get("source", "Unknown") for doc in source_docs],
        }

    except Exception as e:
        logging.error(f"Error processing query: {e}", exc_info=True)
        return {"answer": "An error occurred while processing the query.", "sources": []}