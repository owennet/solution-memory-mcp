"""save_solution MCP tool implementation."""

from typing import Any
from ..models.solution import Solution, SolutionCreate
from ..storage.sqlite_store import SQLiteStore
from ..storage.chroma_store import ChromaStore


async def save_solution(
    sqlite_store: SQLiteStore,
    chroma_store: ChromaStore,
    title: str,
    problem: str,
    solution: str,
    root_cause: str | None = None,
    error_messages: list[str] | None = None,
    tags: list[str] | None = None,
    project_name: str | None = None,
) -> dict[str, Any]:
    """Save a new solution to the memory system.
    
    Args:
        sqlite_store: SQLite storage instance
        chroma_store: Chroma storage instance
        title: Problem title
        problem: Problem description
        solution: Solution description
        root_cause: Optional root cause analysis
        error_messages: Optional list of error messages
        tags: Optional list of tags
        project_name: Optional source project name
        
    Returns:
        Dict with id and success message
    """
    # Create solution model
    solution_obj = Solution(
        title=title,
        problem=problem,
        solution=solution,
        root_cause=root_cause,
        error_messages=error_messages or [],
        tags=tags or [],
        project_name=project_name,
    )
    
    # Save to SQLite
    solution_id = sqlite_store.save_solution(solution_obj)
    
    # Save to Chroma for vector search
    chroma_store.add_solution(
        solution_id=solution_id,
        problem=problem,
        error_messages=error_messages or [],
        title=title
    )
    
    return {
        "id": solution_id,
        "message": f"Solution '{title}' saved successfully with ID {solution_id}"
    }


TOOL_DEFINITION = {
    "name": "save_solution",
    "description": "Save a problem solution to the memory system for future reference. Use this after successfully solving a bug, configuration issue, or technical problem.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "A concise title describing the problem (max 500 chars)"
            },
            "problem": {
                "type": "string",
                "description": "Detailed description of the problem"
            },
            "solution": {
                "type": "string",
                "description": "The solution that resolved the problem"
            },
            "root_cause": {
                "type": "string",
                "description": "Optional root cause analysis"
            },
            "error_messages": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of error messages encountered"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags for categorization (e.g., 'React', 'Docker', 'bug')"
            },
            "project_name": {
                "type": "string",
                "description": "Optional name of the project where this was solved"
            }
        },
        "required": ["title", "problem", "solution"]
    }
}
