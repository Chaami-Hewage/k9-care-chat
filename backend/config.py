import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    PORT = int(os.getenv("PORT", 8000))
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # AI & Vector DB keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "k9-care-index")
    PINECONE_HOST = os.getenv("PINECONE_HOST", "")

    # Security settings
    MAX_INPUT_LENGTH = 1000
    RATE_LIMIT_DEFAULT = "30 per minute"

    # Google Auth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
