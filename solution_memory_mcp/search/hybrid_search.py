"""Hybrid search engine combining FTS5 keyword search and Chroma semantic search."""

from typing import Optional
from dataclasses import dataclass

from ..storage.sqlite_store import SQLiteStore
from ..storage.chroma_store import ChromaStore
from ..models.solution import SolutionSummary


@dataclass
class SearchResult:
    """Internal search result with scores."""
    solution_id: str
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    relevance: float = 0.0


class HybridSearchEngine:
    """Hybrid search engine combining keyword and semantic search."""

    def __init__(
        self,
        sqlite_store: SQLiteStore,
        chroma_store: ChromaStore,
        semantic_weight: float = 0.6
    ):
        """Initialize hybrid search engine.
        
        Args:
            sqlite_store: SQLite store for FTS5 search
            chroma_store: Chroma store for semantic search
            semantic_weight: Weight for semantic score (0-1), keyword weight = 1 - semantic_weight
        """
        self.sqlite_store = sqlite_store
        self.chroma_store = chroma_store
        self.semantic_weight = semantic_weight
        self.keyword_weight = 1 - semantic_weight

    def search(
        self,
        query: str,
        limit: int = 5,
        tags: Optional[list[str]] = None,
        search_mode: str = "hybrid"
    ) -> list[SolutionSummary]:
        """Search for solutions using hybrid search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            tags: Optional tags to filter by
            search_mode: 'hybrid', 'semantic', or 'keyword'
            
        Returns:
            List of solution summaries sorted by relevance
        """
        if search_mode == "semantic":
            results = self._semantic_search(query, limit * 2)
        elif search_mode == "keyword":
            results = self._keyword_search(query, limit * 2)
        else:
            results = self._hybrid_search(query, limit * 2)

        # Filter by tags if provided
        if tags and results:
            solution_ids = [r.solution_id for r in results]
            filtered_ids = set(self.sqlite_store.filter_by_tags(solution_ids, tags))
            results = [r for r in results if r.solution_id in filtered_ids]

        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance, reverse=True)
        results = results[:limit]

        # Convert to SolutionSummary
        return self._to_summaries(results)

    def _hybrid_search(self, query: str, limit: int) -> list[SearchResult]:
        """Perform hybrid search combining keyword and semantic."""
        # Get results from both sources
        semantic_results = dict(self.chroma_store.search(query, limit))
        keyword_results = dict(self.sqlite_store.search_fts(query, limit))

        # Merge results using Reciprocal Rank Fusion (RRF)
        all_ids = set(semantic_results.keys()) | set(keyword_results.keys())
        
        results = []
        for solution_id in all_ids:
            semantic_score = semantic_results.get(solution_id, 0.0)
            keyword_score = keyword_results.get(solution_id, 0.0)
            
            # Weighted combination
            relevance = (
                self.semantic_weight * semantic_score +
                self.keyword_weight * keyword_score
            )
            
            results.append(SearchResult(
                solution_id=solution_id,
                semantic_score=semantic_score,
                keyword_score=keyword_score,
                relevance=relevance
            ))

        return results

    def _semantic_search(self, query: str, limit: int) -> list[SearchResult]:
        """Perform semantic-only search."""
        semantic_results = self.chroma_store.search(query, limit)
        
        return [
            SearchResult(
                solution_id=id,
                semantic_score=score,
                keyword_score=0.0,
                relevance=score
            )
            for id, score in semantic_results
        ]

    def _keyword_search(self, query: str, limit: int) -> list[SearchResult]:
        """Perform keyword-only search."""
        keyword_results = self.sqlite_store.search_fts(query, limit)
        
        return [
            SearchResult(
                solution_id=id,
                semantic_score=0.0,
                keyword_score=score,
                relevance=score
            )
            for id, score in keyword_results
        ]

    def _to_summaries(self, results: list[SearchResult]) -> list[SolutionSummary]:
        """Convert search results to solution summaries."""
        if not results:
            return []

        # Get full solutions
        solution_ids = [r.solution_id for r in results]
        solutions = self.sqlite_store.get_solutions_by_ids(solution_ids)
        
        # Create lookup map
        solution_map = {s.id: s for s in solutions}
        
        summaries = []
        for result in results:
            solution = solution_map.get(result.solution_id)
            if solution:
                # Truncate problem to 200 chars
                problem_truncated = solution.problem[:200]
                if len(solution.problem) > 200:
                    problem_truncated += "..."
                
                summaries.append(SolutionSummary(
                    id=solution.id,
                    title=solution.title,
                    problem=problem_truncated,
                    relevance=round(result.relevance, 4),
                    semantic_score=round(result.semantic_score, 4),
                    keyword_score=round(result.keyword_score, 4),
                    project_name=solution.project_name,
                    created_at=solution.created_at,
                    tags=solution.tags
                ))

        return summaries
