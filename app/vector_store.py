import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from app.config import settings

class VectorStore:
    def __init__(self):
        # Initialize QDrant
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        # Initialize Local Embeddings (free, no API cost, runs on CPU)
        # BAAI/bge-small-en-v1.5 is efficient and high quality for RAG
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self._ensure_collection()

    def _ensure_collection(self):
        """Creates collection if it doesn't exist."""
        if not self.client.collection_exists(settings.COLLECTION_NAME):
            self.client.create_collection(
                collection_name=settings.COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=384,  # Size matches BAAI/bge-small-en-v1.5
                    distance=models.Distance.COSINE
                )
            )

    async def ingest_text(self, text: str, metadata: Dict[str, Any] = None):
        """
        Embeds the text and uploads it to QDrant Cloud.
        """
        # Generate embedding (fastembed returns a generator, we convert to list)
        embeddings = list(self.embedding_model.embed([text]))[0]
        
        # Prepare payload
        payload = {"text": text}
        if metadata:
            payload.update(metadata)

        # Upsert to QDrant
        self.client.upsert(
            collection_name=settings.COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embeddings.tolist(),
                    payload=payload
                )
            ]
        )

    async def search(self, query: str, limit: int = 3) -> str:
        """Searches for relevant context based on query similarity."""
        query_embedding = list(self.embedding_model.embed([query]))[0]
        
        results = self.client.search(
            collection_name=settings.COLLECTION_NAME,
            query_vector=query_embedding.tolist(),
            limit=limit
        )

        if not results:
            return "No relevant context found in the coursebook."

        # Format context for the LLM
        context_str = "\n\n".join([
            f"--- Excerpt (Score: {hit.score:.2f}) ---\n{hit.payload.get('text', '')}"
            for hit in results
        ])
        return context_str

# Singleton instance
vector_store = VectorStore()