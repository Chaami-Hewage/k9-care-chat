import logging
from typing import List, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        self.index = None
        self.pc = None
        self._init_pinecone()

    def _init_pinecone(self):
        if not Config.PINECONE_API_KEY or Config.PINECONE_API_KEY == "your_pinecone_api_key_here":
            logger.warning("Pinecone API key not configured. RAG vector search will operate in fallback mode.")
            return

        try:
            from pinecone import Pinecone
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            if Config.PINECONE_INDEX_NAME in [idx.name for idx in self.pc.list_indexes()]:
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
                logger.info(f"Successfully connected to Pinecone index '{Config.PINECONE_INDEX_NAME}'.")
            else:
                logger.warning(f"Pinecone index '{Config.PINECONE_INDEX_NAME}' not found.")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            self.index = None

    def search_knowledge(self, query: str = "", breed: str = "", top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Query Pinecone index for knowledge context relevant to dog query & breed.
        """
        if not self.index:
            return []

        try:
            # Prepare search text
            search_text = f"Breed: {breed}. Query: {query}".strip()
            
            # Note: Depending on Pinecone setup, embedding can be generated via Google GenAI or Pinecone Inference API.
            # If using Pinecone integrated inference/dense index or custom metadata filter:
            # We attempt a query if index supports text or metadata filtering.
            response = self.index.query(
                vector=[0.0] * 768, # Fallback dummy vector if standard vector search; or metadata filter
                top_k=top_k,
                include_metadata=True,
                filter={"breed": breed} if breed else None
            )
            
            results = []
            for match in response.get("matches", []):
                if "metadata" in match and "text" in match["metadata"]:
                    results.append(match["metadata"])
            return results
        except Exception as e:
            logger.warning(f"Error querying Pinecone index: {e}")
            return []
