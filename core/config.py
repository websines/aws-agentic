import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Azure Settings
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")

    # LLM Settings
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "hf.co/Mazino0/phi4-azure")

    # Qdrant Settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

    # API Settings
    API_HOST = os.getenv("API_HOST", "localhost")
    API_PORT = int(os.getenv("API_PORT", "8000"))
