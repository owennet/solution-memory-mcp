"""SQLite storage layer with FTS5 full-text search support."""

import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..models.solution import Solution, SolutionCreate, SolutionSummary, Tag, TagWithCount


class SQLiteStore:
    """SQLite storage for solutions with FTS5 full-text search."""

    def __init__(self, db_path: str | Path):
        """Initialize SQLite store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        try:
            conn.executescript("""
                -- Solutions main table
                CREATE TABLE IF NOT EXISTS solutions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    problem TEXT NOT NULL,
                    root_cause TEXT,
                    solution TEXT NOT NULL,
                    error_messages TEXT,
                    project_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Tags table
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL CHECK(category IN ('tech_stack', 'problem_type', 'error_code'))
                );

                -- Solution-Tag junction table
                CREATE TABLE IF NOT EXISTS solution_tags (
                    solution_id TEXT REFERENCES solutions(id) ON DELETE CASCADE,
                    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (solution_id, tag_id)
                );

                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_solutions_created_at ON solutions(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category);

                -- FTS5 virtual table for full-text search
                CREATE VIRTUAL TABLE IF NOT EXISTS solutions_fts USING fts5(
                    title,
                    problem,
                    solution,
                    error_messages,
                    content='solutions',
                    content_rowid='rowid'
                );

                -- Triggers to keep FTS index in sync
                CREATE TRIGGER IF NOT EXISTS solutions_ai AFTER INSERT ON solutions BEGIN
                    INSERT INTO solutions_fts(rowid, title, problem, solution, error_messages)
                    VALUES (NEW.rowid, NEW.title, NEW.problem, NEW.solution, NEW.error_messages);
                END;

                CREATE TRIGGER IF NOT EXISTS solutions_ad AFTER DELETE ON solutions BEGIN
                    INSERT INTO solutions_fts(solutions_fts, rowid, title, problem, solution, error_messages)
                    VALUES ('delete', OLD.rowid, OLD.title, OLD.problem, OLD.solution, OLD.error_messages);
                END;

                CREATE TRIGGER IF NOT EXISTS solutions_au AFTER UPDATE ON solutions BEGIN
                    INSERT INTO solutions_fts(solutions_fts, rowid, title, problem, solution, error_messages)
                    VALUES ('delete', OLD.rowid, OLD.title, OLD.problem, OLD.solution, OLD.error_messages);
                    INSERT INTO solutions_fts(rowid, title, problem, solution, error_messages)
                    VALUES (NEW.rowid, NEW.title, NEW.problem, NEW.solution, NEW.error_messages);
                END;
            """)
            conn.commit()
        finally:
            conn.close()

    def save_solution(self, solution: Solution) -> str:
        """Save a solution to the database.
        
        Args:
            solution: Solution to save
            
        Returns:
            The solution ID
        """
        conn = self._get_connection()
        try:
            # Insert solution
            conn.execute(
                """
                INSERT INTO solutions (id, title, problem, root_cause, solution, error_messages, project_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    solution.id,
                    solution.title,
                    solution.problem,
                    solution.root_cause,
                    solution.solution,
                    json.dumps(solution.error_messages),
                    solution.project_name,
                    solution.created_at.isoformat(),
                    solution.updated_at.isoformat(),
                )
            )

            # Handle tags
            for tag_name in solution.tags:
                self._ensure_tag_and_link(conn, solution.id, tag_name)

            conn.commit()
            return solution.id
        finally:
            conn.close()

    def _ensure_tag_and_link(self, conn: sqlite3.Connection, solution_id: str, tag_name: str) -> None:
        """Ensure tag exists and link to solution."""
        # Determine category from tag name pattern
        category = self._infer_tag_category(tag_name)
        
        # Insert or ignore tag
        conn.execute(
            "INSERT OR IGNORE INTO tags (name, category) VALUES (?, ?)",
            (tag_name, category)
        )
        
        # Get tag id
        row = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
        if row:
            conn.execute(
                "INSERT OR IGNORE INTO solution_tags (solution_id, tag_id) VALUES (?, ?)",
                (solution_id, row["id"])
            )

    def _infer_tag_category(self, tag_name: str) -> str:
        """Infer tag category from tag name."""
        tech_keywords = ["react", "vue", "angular", "node", "python", "java", "go", "rust", 
                        "docker", "kubernetes", "aws", "gcp", "azure", "postgresql", "mysql",
                        "mongodb", "redis", "typescript", "javascript", "css", "html"]
        error_patterns = ["error", "exception", "fail", "http", "status", "code"]
        
        tag_lower = tag_name.lower()
        
        if any(kw in tag_lower for kw in tech_keywords):
            return "tech_stack"
        elif any(p in tag_lower for p in error_patterns) or tag_name.isdigit():
            return "error_code"
        else:
            return "problem_type"

    def get_solution(self, solution_id: str) -> Optional[Solution]:
        """Get a solution by ID.
        
        Args:
            solution_id: Solution UUID
            
        Returns:
            Solution if found, None otherwise
        """
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM solutions WHERE id = ?",
                (solution_id,)
            ).fetchone()
            
            if not row:
                return None

            # Get tags
            tags = conn.execute(
                """
                SELECT t.name FROM tags t
                JOIN solution_tags st ON t.id = st.tag_id
                WHERE st.solution_id = ?
                """,
                (solution_id,)
            ).fetchall()

            return Solution(
                id=row["id"],
                title=row["title"],
                problem=row["problem"],
                root_cause=row["root_cause"],
                solution=row["solution"],
                error_messages=json.loads(row["error_messages"]) if row["error_messages"] else [],
                project_name=row["project_name"],
                tags=[t["name"] for t in tags],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        finally:
            conn.close()

    def search_fts(self, query: str, limit: int = 20) -> list[tuple[str, float]]:
        """Search solutions using FTS5 full-text search.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of (solution_id, bm25_score) tuples
        """
        conn = self._get_connection()
        try:
            # Use BM25 ranking
            rows = conn.execute(
                """
                SELECT s.id, bm25(solutions_fts) as score
                FROM solutions_fts fts
                JOIN solutions s ON fts.rowid = s.rowid
                WHERE solutions_fts MATCH ?
                ORDER BY score
                LIMIT ?
                """,
                (query, limit)
            ).fetchall()
            
            # Normalize scores (BM25 returns negative values, lower is better)
            if not rows:
                return []
            
            results = [(row["id"], -row["score"]) for row in rows]
            max_score = max(r[1] for r in results) if results else 1
            return [(id, score / max_score if max_score > 0 else 0) for id, score in results]
        except sqlite3.OperationalError:
            # FTS query syntax error, return empty
            return []
        finally:
            conn.close()

    def get_solutions_by_ids(self, ids: list[str]) -> list[Solution]:
        """Get multiple solutions by IDs.
        
        Args:
            ids: List of solution UUIDs
            
        Returns:
            List of solutions
        """
        if not ids:
            return []
        
        solutions = []
        for solution_id in ids:
            solution = self.get_solution(solution_id)
            if solution:
                solutions.append(solution)
        return solutions

    def list_tags(self, category: Optional[str] = None) -> list[TagWithCount]:
        """List all tags with solution counts.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of tags with counts
        """
        conn = self._get_connection()
        try:
            if category:
                rows = conn.execute(
                    """
                    SELECT t.name, t.category, COUNT(st.solution_id) as count
                    FROM tags t
                    LEFT JOIN solution_tags st ON t.id = st.tag_id
                    WHERE t.category = ?
                    GROUP BY t.id
                    ORDER BY count DESC
                    """,
                    (category,)
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT t.name, t.category, COUNT(st.solution_id) as count
                    FROM tags t
                    LEFT JOIN solution_tags st ON t.id = st.tag_id
                    GROUP BY t.id
                    ORDER BY count DESC
                    """
                ).fetchall()

            return [
                TagWithCount(name=row["name"], category=row["category"], count=row["count"])
                for row in rows
            ]
        finally:
            conn.close()

    def filter_by_tags(self, solution_ids: list[str], tags: list[str]) -> list[str]:
        """Filter solution IDs by tags.
        
        Args:
            solution_ids: List of solution IDs to filter
            tags: Tags to filter by (OR logic)
            
        Returns:
            Filtered list of solution IDs
        """
        if not solution_ids or not tags:
            return solution_ids

        conn = self._get_connection()
        try:
            placeholders = ",".join("?" * len(solution_ids))
            tag_placeholders = ",".join("?" * len(tags))
            
            rows = conn.execute(
                f"""
                SELECT DISTINCT st.solution_id
                FROM solution_tags st
                JOIN tags t ON st.tag_id = t.id
                WHERE st.solution_id IN ({placeholders})
                AND t.name IN ({tag_placeholders})
                """,
                (*solution_ids, *tags)
            ).fetchall()

            return [row["solution_id"] for row in rows]
        finally:
            conn.close()

    def delete_solution(self, solution_id: str) -> bool:
        """Delete a solution by ID.
        
        Args:
            solution_id: Solution UUID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM solutions WHERE id = ?",
                (solution_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
