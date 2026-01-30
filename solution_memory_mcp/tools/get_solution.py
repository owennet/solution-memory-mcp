"""get_solution MCP tool implementation."""

from typing import Any
from ..storage.sqlite_store import SQLiteStore


async def get_solution(
    sqlite_store: SQLiteStore,
    id: str,
) -> dict[str, Any]:
    """Get full details of a solution by ID.
    
    Args:
        sqlite_store: SQLite storage instance
        id: Solution UUID
        
    Returns:
        Full solution details or error message
    """
    solution = sqlite_store.get_solution(id)
    
    if not solution:
        return {
            "error": f"Solution with ID '{id}' not found"
        }
    
    return {
        "id": solution.id,
        "title": solution.title,
        "problem": solution.problem,
        "root_cause": solution.root_cause,
        "solution": solution.solution,
        "error_messages": solution.error_messages,
        "tags": solution.tags,
        "project_name": solution.project_name,
        "created_at": solution.created_at.isoformat(),
        "updated_at": solution.updated_at.isoformat()
    }


TOOL_DEFINITION = {
    "name": "get_solution",
    "description": "Get full details of a solution by its ID. Use this after search_solutions to get complete solution information.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "The solution UUID"
            }
        },
        "required": ["id"]
    }
}
