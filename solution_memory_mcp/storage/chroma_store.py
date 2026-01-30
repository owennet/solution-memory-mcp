"""Chroma vector storage layer for semantic search."""

from pathlib import Path
from typing import Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


class ChromaStore:
    """Chroma vector database for semantic similarity search."""

    def __init__(self, persist_dir: str | Path, collection_name: str = "solution_embeddings"):
        """Initialize Chroma store.
        
        Args:
            persist_dir: Directory for Chroma persistence
            collection_name: Name of the collection
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Use sentence-transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def add_solution(self, solution_id: str, problem: str, error_messages: list[str], title: str) -> None:
        """Add a solution to the vector store.
        
        Args:
            solution_id: Unique solution ID
            problem: Problem description
            error_messages: List of error messages
            title: Solution title
        """
        # Combine problem and error messages for embedding
        document = self._create_document(problem, error_messages)
        
        # Add to collection
        self.collection.add(
            ids=[solution_id],
            documents=[document],
            metadatas=[{"solution_id": solution_id, "title": title}]
        )

    def _create_document(self, problem: str, error_messages: list[str]) -> str:
        """Create a document string for embedding.
        
        Args:
            problem: Problem description
            error_messages: List of error messages
            
        Returns:
            Combined document string
        """
        parts = [problem]
        if error_messages:
            parts.append("Error messages: " + " | ".join(error_messages))
        return " ".join(parts)

    def search(self, query: str, limit: int = 20) -> list[tuple[str, float]]:
        """Search for similar solutions.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of (solution_id, similarity_score) tuples, sorted by relevance
        """
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=min(limit, self.collection.count())
        )
        
        if not results["ids"] or not results["ids"][0]:
            return []
        
        # Convert distances to similarity scores (cosine distance -> similarity)
        # Chroma returns distances, lower is better for cosine
        ids = results["ids"][0]
        distances = results["distances"][0] if results["distances"] else [0] * len(ids)
        
        # Convert distance to similarity (1 - distance for cosine)
        similarities = [(id, 1 - dist) for id, dist in zip(ids, distances)]
        
        return similarities

    def delete_solution(self, solution_id: str) -> bool:
        """Delete a solution from the vector store.
        
        Args:
            solution_id: Solution ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            self.collection.delete(ids=[solution_id])
            return True
        except Exception:
            return False

    def update_solution(self, solution_id: str, problem: str, error_messages: list[str], title: str) -> None:
        """Update a solution in the vector store.
        
        Args:
            solution_id: Solution ID to update
            problem: New problem description
            error_messages: New error messages
            title: New title
        """
        document = self._create_document(problem, error_messages)
        
        self.collection.update(
            ids=[solution_id],
            documents=[document],
            metadatas=[{"solution_id": solution_id, "title": title}]
        )

    def get_count(self) -> int:
        """Get the number of solutions in the store.
        
        Returns:
            Number of solutions
        """
        return self.collection.count()
