# services/document_service.py
import os
from fastapi import UploadFile, HTTPException

UPLOAD_DIRECTORY = "uploads"

def handle_file_upload(file: UploadFile, customer_id: str, chatbot_id: str) -> dict:
    """
    Handles the process of uploading a document for a specific chatbot.

    Args:
        file (UploadFile): The file uploaded by the user.
        customer_id (str): The ID of the customer.
        chatbot_id (str): The ID of the chatbot.

    Returns:
        dict: A success message with the customer and chatbot IDs.
    """
    try:
        # Create directories if they don't exist
        customer_dir = os.path.join(UPLOAD_DIRECTORY, customer_id, chatbot_id)
        os.makedirs(customer_dir, exist_ok=True)

        # Full path to save the file
        file_path = os.path.join(customer_dir, file.filename)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        return {"message": f"File uploaded successfully for customer '{customer_id}' and chatbot '{chatbot_id}'"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")