import pandas as pd
import numpy as np
import faiss
from openai import AsyncOpenAI
from app.core.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class RAGService:
    def __init__(self):
        self.index = None
        self.documents = []
        self.is_initialized = False

    async def get_embedding(self, text: str, model="text-embedding-3-small") -> List[float]:
        """Generates embedding for a given text."""
        text = text.replace("\n", " ")
        response = await client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding

    async def load_and_index_csv(self, file_path: str):
        """
        Reverted to a simplified, robust RAG strategy. It creates one comprehensive
        document PER ROW. This provides clean, unambiguous context to the LLM, which is
        superior for this type of structured data.
        """
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.astype(str)
            df = df.fillna('') 
        except Exception as e:
            logger.error(f"Failed to read or process CSV file: {e}")
            return

        self.documents = []
        
        # Create one clear, comprehensive document for each row.
        for _, row in df.iterrows():
            doc_parts = []
            for col_name, cell_value in row.items():
                if str(cell_value): # Ensure value is a string and not empty
                    doc_parts.append(f"{col_name}: {cell_value}")
            doc = f"Property Listing -> {', '.join(doc_parts)}."
            self.documents.append(doc)

        if not self.documents:
            logger.warning("No documents were generated from the CSV.")
            return

        logger.info(f"Generating embeddings for {len(self.documents)} row-based documents...")
        
        batch_size = 100 
        embeddings = []
        for i in range(0, len(self.documents), batch_size):
            batch_docs = self.documents[i:i+batch_size]
            response = await client.embeddings.create(input=batch_docs, model="text-embedding-3-small")
            embeddings.extend([data.embedding for data in response.data])
        
        embeddings = np.array(embeddings).astype('float32')
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        self.is_initialized = True
        logger.info("FAISS index created successfully with clean, row-based documents.")

    async def retrieve_context(self, query: str, top_k: int = 15) -> str:
        """
        Increased top_k to 15 to ensure a wider net is cast, capturing all
        potential properties at a single address.
        """
        if not self.is_initialized:
            return "Knowledge base is not yet initialized."

        query_embedding = await self.get_embedding(query)
        query_embedding = np.array([query_embedding]).astype('float32')

        _, indices = self.index.search(query_embedding, top_k)
        
        # Use a set to avoid duplicate context entries, which can happen with similar rows
        unique_docs = set(self.documents[i] for i in indices[0])
        context = "\n- ".join(unique_docs)
        return context

# Create a single instance of the RAG service to act as an in-memory store
rag_service = RAGService()
