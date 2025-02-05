import os
from chromadb.config import Settings
from langchain.document_loaders import CSVLoader, PDFMinerLoader, TextLoader, UnstructuredExcelLoader, Docx2txtLoader
from langchain.document_loaders import UnstructuredFileLoader, UnstructuredMarkdownLoader
from langchain.document_loaders import UnstructuredHTMLLoader

# Adjust the root directory based on your current project structure
ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# Directory paths
# Assuming you moved source documents to `data/source_documents/` at the project root:
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIRECTORY, "..", ".."))
SOURCE_DIRECTORY = os.path.join(PROJECT_ROOT, "data", "source_documents")
CHROMA_BASE_DIRECTORY = "chroma_dbs"

MODELS_PATH = os.path.join(PROJECT_ROOT, "models")

# Ingest threads
INGEST_THREADS = 4  # Number of threads for document ingestion

# Chroma settings
CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)

# Document type mapping - loaders need to be defined somewhere
# Replace "TextLoader", "PDFLoader", "DocxLoader" with actual loader classes when integrated
DOCUMENT_MAP = {
    ".html": UnstructuredHTMLLoader,
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
    ".py": TextLoader,
    # ".pdf": PDFMinerLoader,
    ".pdf": UnstructuredFileLoader,
    ".csv": CSVLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
}

# LLM Model configuration (If needed, adjust paths/names)
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"

# Fireworks.ai model configuration
MODEL_ID = "accounts/fireworks/models/qwen2p5-coder-32b-instruct"
MODEL_BASENAME = None

# Context Window Settings
CONTEXT_WINDOW_SIZE = 8096
MAX_NEW_TOKENS = CONTEXT_WINDOW_SIZE

# GPU and batch settings for LLM inference
N_GPU_LAYERS = 100  
N_BATCH = 512
def get_vectorstore_path(customer_id: str, chatbot_id: str) -> str:
    """
    Construct the path for the vector store where embeddings are stored
    for a given customer and chatbot.
    """
    return os.path.join(CHROMA_BASE_DIRECTORY, customer_id, str(chatbot_id))