import chromadb
from chromadb.config import Settings
import logging
from typing import List
from src.config import DB_DIR, EMBEDDING_CACHE_DIR, EMBEDDING_MODEL_NAME
from src.models import DocumentChunk

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBClient:
    def __init__(self):
        """
        Initialize ChromaDB persistent client and embedding function.
        """
        logger.info(f"Initializing VectorDB at {DB_DIR}")
        self.client = chromadb.PersistentClient(path=DB_DIR)
        
        # Use sentence-transformers for embeddings
        from chromadb.utils import embedding_functions
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        self.collection = self.client.get_or_create_collection(
            name="bharat_edge_docs",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, chunks: List[str], metadatas: List[dict]):
        """
        Embed and store document chunks.
        
        Args:
            chunks: List of text strings
            metadatas: List of dicts with 'source', 'page'
        """
        ids = [f"id_{i}_{hash(c)}" for i, c in enumerate(chunks)]
        self.collection.upsert(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Upserted {len(chunks)} chunks.")

    def search(self, query: str, k: int = 3, sources: List[str] = None) -> List[DocumentChunk]:
        """
        Semantic search for relevant chunks with optional source filtering.
        """
        where_filter = None
        if sources and len(sources) > 0:
            if len(sources) == 1:
                where_filter = {"source": sources[0]}
            else:
                where_filter = {"$or": [{"source": s} for s in sources]}

        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=where_filter
        )
        
        # Parse results into DocumentChunk objects
        chunks = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                chunks.append(DocumentChunk(
                    text=results['documents'][0][i],
                    source=results['metadatas'][0][i]['source'],
                    page=results['metadatas'][0][i].get('page', 0),
                    score=results['distances'][0][i] if 'distances' in results else 0.0
                ))
        return chunks

    def get_all_chunks(self, sources: List[str], limit: int = 10) -> List[DocumentChunk]:
        """
        Fetch chunks directly by source filter without semantic search.
        Useful for summarization when query is vague.
        """
        where_filter = None
        if sources and len(sources) > 0:
            if len(sources) == 1:
                where_filter = {"source": sources[0]}
            else:
                where_filter = {"$or": [{"source": s} for s in sources]}
        
        results = self.collection.get(
            where=where_filter,
            limit=limit,
            include=['documents', 'metadatas']
        )
        
        chunks = []
        if results['documents']:
            for i in range(len(results['documents'])):
                chunks.append(DocumentChunk(
                    text=results['documents'][i],
                    source=results['metadatas'][i]['source'],
                    page=results['metadatas'][i].get('page', 0)
                ))
        return chunks

    def delete_document(self, filename: str):
        """
        Delete all chunks associated with a source file.
        """
        try:
            self.collection.delete(where={"source": filename})
            logger.info(f"Deleted chunks for {filename}")
        except Exception as e:
            logger.error(f"Failed to delete chunks for {filename}: {e}")
            raise e
