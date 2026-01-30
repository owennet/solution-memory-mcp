"""Data models for Solution Memory."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class SolutionCreate(BaseModel):
    """Input model for creating a new solution."""
    
    title: str = Field(..., min_length=1, max_length=500, description="Problem title")
    problem: str = Field(..., min_length=1, description="Problem description")
    solution: str = Field(..., min_length=1, description="Solution description")
    root_cause: Optional[str] = Field(None, description="Root cause analysis")
    error_messages: Optional[list[str]] = Field(default_factory=list, description="Related error messages")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags for categorization")
    project_name: Optional[str] = Field(None, description="Source project name")


class Solution(BaseModel):
    """Full solution model with all fields."""
    
    model_config = {"from_attributes": True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    title: str
    problem: str
    solution: str
    root_cause: Optional[str] = None
    error_messages: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    project_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))


class SolutionSummary(BaseModel):
    """Lightweight solution summary for search results."""
    
    id: str
    title: str
    problem: str = Field(..., description="Truncated to 200 chars")
    relevance: float = Field(..., ge=0, le=1, description="Combined relevance score")
    semantic_score: float = Field(default=0.0, ge=0, le=1, description="Semantic similarity score")
    keyword_score: float = Field(default=0.0, ge=0, le=1, description="Keyword match score")
    project_name: Optional[str] = None
    created_at: datetime
    tags: list[str] = Field(default_factory=list)


class Tag(BaseModel):
    """Tag model."""
    
    id: Optional[int] = None
    name: str
    category: str = Field(..., pattern="^(tech_stack|problem_type|error_code)$")


class TagWithCount(BaseModel):
    """Tag with solution count."""
    
    name: str
    category: str
    count: int = 0
