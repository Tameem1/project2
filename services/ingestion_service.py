# services/ingestion_service.py

import os
import logging
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from utils.constants import CHROMA_SETTINGS, get_vectorstore_path, DOCUMENT_MAP
from utils.embedding_utils import get_embeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def ingest_documents_for_chatbot(customer_id: str, chatbot_id: str) -> bool:
    """
    Ingest all documents for a given customer_id and chatbot_id into the vector store.

    This uses the directory structure: uploads/{customer_id}/{chatbot_id}/
    and stores embeddings in chroma_dbs/{customer_id}/{chatbot_id}.

    Returns:
        bool: True if ingestion was successful, otherwise False.
    """
    upload_path = os.path.join("uploads", customer_id, chatbot_id)
    if not os.path.isdir(upload_path):
        logging.error(f"No directory found for customer={customer_id}, chatbot={chatbot_id} at {upload_path}")
        return False

    loaded_docs = []

    # 1. Collect all files in the chatbot’s directory
    for filename in os.listdir(upload_path):
        full_path = os.path.join(upload_path, filename)
        if not os.path.isfile(full_path):
            continue

        # Determine the file extension
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower()

        # Identify the proper loader from DOCUMENT_MAP
        loader_class = DOCUMENT_MAP.get(file_extension)
        if not loader_class:
            logging.warning(f"No loader found for extension '{file_extension}'. Skipping file: {filename}")
            continue

        try:
            # Instantiate the loader (depends on the loader class requirements)
            loader = loader_class(full_path)
            docs = loader.load()
            if not docs:
                logging.warning(f"No documents returned by loader for '{filename}'")
                continue

            loaded_docs.extend(docs)
            logging.info(f"Loaded {len(docs)} document(s) from {filename}")

        except Exception as e:
            logging.error(f"Error loading {filename} with {loader_class.__name__}: {e}", exc_info=True)
            continue

    if not loaded_docs:
        logging.warning(f"No valid documents found for ingestion in {upload_path}")
        return False

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(loaded_docs)
    logging.info(f"Splitting into chunks produced {len(chunks)} total chunks.")

    # 3. Load embeddings
    embeddings = get_embeddings()
    logging.info("Embeddings initialized successfully.")

    # 4. Determine the vector store path
    persist_dir = get_vectorstore_path(customer_id, chatbot_id)
    os.makedirs(persist_dir, exist_ok=True)

    # 5. Initialize Chroma vector store
    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        client_settings=CHROMA_SETTINGS
    )
    logging.info(f"Chroma vector store created/loaded for {customer_id}/{chatbot_id} at {persist_dir}.")

    # 6. Add documents to the vector store
    db.add_documents(chunks)
    db.persist()
    logging.info(f"Ingestion complete for customer={customer_id}, chatbot={chatbot_id}. Vector store updated.")

    return True