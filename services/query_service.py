# services/query_service.py

import logging
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage  # <-- add this import
from langchain_fireworks import ChatFireworks

from utils.constants import CHROMA_SETTINGS, get_vectorstore_path, MODEL_ID
from utils.embedding_utils import get_embeddings
from services.usage_service import consume_tokens
from services.chat_history_service import log_chat
from sqlalchemy.orm import Session
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

from uuid import UUID

def process_query(question: str, customer_id: str, chatbot_id: UUID, user_id: str, db: Session) -> dict:
    """
    Processes a user query by retrieving relevant documents, invoking the LLM,
    consuming tokens, logging chat history, and returning the answer.
    """
    try:
        logging.info(f"Processing query: {question}")

        # 1) Initialize embeddings & retriever
        embeddings = get_embeddings()
        persist_dir = get_vectorstore_path(customer_id, str(chatbot_id))
        db_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
            client_settings=CHROMA_SETTINGS,
        )
        retriever = db_store.as_retriever()

        # 2) Instantiate ChatFireworks
        llm = ChatFireworks(
            api_key="fw_3ZfGXeDhjJfUxVHUVRBDfMeU",  # Replace with secure storage in production
            model=MODEL_ID,
            temperature=0.7,
            max_tokens=1500,
            top_p=1.0,
        )

        # 3) Count tokens for the input
        input_tokens = llm.get_num_tokens_from_messages([HumanMessage(content=question)])
        
        # 4) Build the QA chain
        prompt, memory = initialize_prompt()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )

        # 5) Run the query to get the answer
        response = qa_chain(question)
        answer = response.get("result", "No answer available.")
        source_docs = response.get("source_documents", [])

        # 6) Count tokens in the answer
        output_tokens = len(llm.get_token_ids(answer))

        total_tokens_used = input_tokens + output_tokens
        logging.info(f"Question tokens={input_tokens}, Answer tokens={output_tokens}, Total={total_tokens_used}")

        # 7) Update usage in DB
        consume_tokens(db, customer_id, input_tokens, output_tokens)

        # 8) Log chat history (note: chatbot_id is now a UUID)
        log_chat(
            db=db,
            chatbot_id=chatbot_id,
            user_id=user_id, 
            question=question,
            answer=answer,
            input_tokens=input_tokens, 
            output_tokens=output_tokens,
            source_docs=[doc.metadata.get("source", "Unknown") for doc in source_docs]
        )

        return {
            "answer": answer,
            "sources": [doc.metadata.get("source", "Unknown") for doc in source_docs],
        }

    except Exception as e:
        logging.error(f"Error processing query: {e}", exc_info=True)
        return {"answer": "An error occurred while processing the query.", "sources": []}