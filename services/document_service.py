# services/document_service.py

import os
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from models.document import Document
import uuid
from datetime import datetime

UPLOAD_DIRECTORY = "uploads"

def handle_file_upload(
    file: UploadFile,
    customer_id: str,
    chatbot_id: str,
    db: Session
) -> dict:
    """
    Handles uploading a document for a specific chatbot:
    1) Saves the file to disk in 'uploads/{customer_id}/{chatbot_id}'.
    2) Inserts a row in the Document table so it appears in the DB.
    """
    try:
        # 1) Create directories if they don't exist
        customer_dir = os.path.join(UPLOAD_DIRECTORY, customer_id, chatbot_id)
        os.makedirs(customer_dir, exist_ok=True)

        # 2) Build the full file path
        file_path = os.path.join(customer_dir, file.filename)

        # 3) Save file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # 4) Insert a new row into the 'documents' table
        new_document = Document(
            id=uuid.uuid4(),
            chatbot_id=chatbot_id,
            filename=file.filename,
            file_path=file_path,
            # 'uploaded_at' will automatically default to NOW if your model/migrations do that
            # otherwise you can set: uploaded_at=datetime.utcnow(),
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        return {"message": f"File '{file.filename}' uploaded and recorded in DB."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")