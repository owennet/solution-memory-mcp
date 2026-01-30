"""search_solutions MCP tool implementation."""

from typing import Any
from ..search.hybrid_search import HybridSearchEngine


async def search_solutions(
    search_engine: HybridSearchEngine,
    query: str,
    limit: int = 5,
    tags: list[str] | None = None,
    search_mode: str = "hybrid",
) -> dict[str, Any]:
    """Search for similar solutions in the memory system.
    
    Args:
        search_engine: Hybrid search engine instance
        query: Search query (problem description or error message)
        limit: Maximum number of results (default 5, max 20)
        tags: Optional tags to filter by
        search_mode: 'hybrid', 'semantic', or 'keyword'
        
    Returns:
        Dict with results list and total count
    """
    # Validate limit
    limit = min(max(1, limit), 20)
    
    # Validate search mode
    if search_mode not in ("hybrid", "semantic", "keyword"):
        search_mode = "hybrid"
    
    # Perform search
    results = search_engine.search(
        query=query,
        limit=limit,
        tags=tags,
        search_mode=search_mode
    )
    
    # Convert to serializable format
    results_data = [
        {
            "id": r.id,
            "title": r.title,
            "problem": r.problem,
            "relevance": r.relevance,
            "semantic_score": r.semantic_score,
            "keyword_score": r.keyword_score,
            "project_name": r.project_name,
            "created_at": r.created_at.isoformat(),
            "tags": r.tags
        }
        for r in results
    ]
    
    return {
        "results": results_data,
        "total": len(results_data)
    }


TOOL_DEFINITION = {
    "name": "search_solutions",
    "description": "Search for similar solutions in the memory system. Use this when encountering a problem to find relevant historical solutions.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query - describe the problem or paste error messages"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results (default 5, max 20)",
                "default": 5,
                "minimum": 1,
                "maximum": 20
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags to filter results"
            },
            "search_mode": {
                "type": "string",
                "enum": ["hybrid", "semantic", "keyword"],
                "description": "Search mode: 'hybrid' (default), 'semantic', or 'keyword'",
                "default": "hybrid"
            }
        },
        "required": ["query"]
    }
}
