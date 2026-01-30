"""Tests for storage layer."""

import pytest
import tempfile
from pathlib import Path

from solution_memory_mcp.models.solution import Solution
from solution_memory_mcp.storage.sqlite_store import SQLiteStore
from solution_memory_mcp.storage.chroma_store import ChromaStore


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sqlite_store(temp_dir):
    """Create a SQLite store for testing."""
    return SQLiteStore(temp_dir / "test.db")


@pytest.fixture
def chroma_store(temp_dir):
    """Create a Chroma store for testing."""
    return ChromaStore(temp_dir / "chroma")


class TestSQLiteStore:
    """Tests for SQLiteStore."""

    def test_save_and_get_solution(self, sqlite_store):
        """Test saving and retrieving a solution."""
        solution = Solution(
            title="Test Problem",
            problem="This is a test problem description",
            solution="This is the solution",
            root_cause="Root cause analysis",
            error_messages=["Error 1", "Error 2"],
            tags=["Python", "bug"],
            project_name="test-project"
        )
        
        # Save
        solution_id = sqlite_store.save_solution(solution)
        assert solution_id == solution.id
        
        # Get
        retrieved = sqlite_store.get_solution(solution_id)
        assert retrieved is not None
        assert retrieved.title == "Test Problem"
        assert retrieved.problem == "This is a test problem description"
        assert retrieved.solution == "This is the solution"
        assert "Python" in retrieved.tags
        assert "bug" in retrieved.tags

    def test_search_fts(self, sqlite_store):
        """Test FTS5 full-text search."""
        # Save some solutions
        solution1 = Solution(
            title="Docker Network Issue",
            problem="ECONNREFUSED when connecting to container",
            solution="Fix network configuration"
        )
        solution2 = Solution(
            title="React State Bug",
            problem="Component not re-rendering on state change",
            solution="Use useEffect hook"
        )
        
        sqlite_store.save_solution(solution1)
        sqlite_store.save_solution(solution2)
        
        # Search
        results = sqlite_store.search_fts("Docker ECONNREFUSED", limit=10)
        assert len(results) >= 1
        assert solution1.id in [r[0] for r in results]

    def test_list_tags(self, sqlite_store):
        """Test listing tags."""
        solution = Solution(
            title="Test",
            problem="Test problem",
            solution="Test solution",
            tags=["Python", "Docker", "bug"]
        )
        sqlite_store.save_solution(solution)
        
        tags = sqlite_store.list_tags()
        tag_names = [t.name for t in tags]
        assert "Python" in tag_names
        assert "Docker" in tag_names

    def test_delete_solution(self, sqlite_store):
        """Test deleting a solution."""
        solution = Solution(
            title="To Delete",
            problem="Problem",
            solution="Solution"
        )
        solution_id = sqlite_store.save_solution(solution)
        
        # Delete
        result = sqlite_store.delete_solution(solution_id)
        assert result is True
        
        # Verify deleted
        retrieved = sqlite_store.get_solution(solution_id)
        assert retrieved is None


class TestChromaStore:
    """Tests for ChromaStore."""

    def test_add_and_search(self, chroma_store):
        """Test adding and searching solutions."""
        # Add solutions
        chroma_store.add_solution(
            solution_id="test-1",
            problem="Docker container network connection refused",
            error_messages=["ECONNREFUSED"],
            title="Docker Network Issue"
        )
        chroma_store.add_solution(
            solution_id="test-2",
            problem="React component not updating",
            error_messages=[],
            title="React State Bug"
        )
        
        # Search
        results = chroma_store.search("network connection refused", limit=5)
        assert len(results) >= 1
        
        # First result should be the Docker issue
        ids = [r[0] for r in results]
        assert "test-1" in ids

    def test_delete(self, chroma_store):
        """Test deleting a solution."""
        chroma_store.add_solution(
            solution_id="to-delete",
            problem="Test problem",
            error_messages=[],
            title="Test"
        )
        
        result = chroma_store.delete_solution("to-delete")
        assert result is True

    def test_get_count(self, chroma_store):
        """Test getting solution count."""
        initial_count = chroma_store.get_count()
        
        chroma_store.add_solution(
            solution_id="count-test",
            problem="Test",
            error_messages=[],
            title="Test"
        )
        
        assert chroma_store.get_count() == initial_count + 1
