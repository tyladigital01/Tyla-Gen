"""SQLite-based memory management system."""

import sqlite3
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent memory using SQLite."""

    def __init__(self, db_path: str = "./data/tyla.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database schema."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            cursor = self.conn.cursor()
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    session_id TEXT
                )
            """)
            
            # Agent executions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_executions (
                    id INTEGER PRIMARY KEY,
                    task TEXT NOT NULL,
                    result TEXT,
                    iterations INTEGER,
                    timestamp TEXT NOT NULL,
                    owner_id TEXT
                )
            """)
            
            # RAG documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    filename TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    doc_type TEXT,
                    indexed_at TEXT NOT NULL
                )
            """)
            
            # System logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY,
                    level TEXT,
                    message TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            self.conn.commit()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def log_message(self, role: str, content: str, session_id: str = "default"):
        """Log a conversation message."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO messages (role, content, timestamp, session_id) VALUES (?, ?, ?, ?)",
                (role, content, datetime.now().isoformat(), session_id)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log message: {e}")

    def log_agent_execution(self, execution_data: Dict[str, Any]):
        """Log an agent execution."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO agent_executions (task, result, iterations, timestamp, owner_id) 
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    execution_data.get("task"),
                    json.dumps(execution_data.get("final_state")),
                    execution_data.get("iterations"),
                    datetime.now().isoformat(),
                    execution_data.get("owner_id"),
                )
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log agent execution: {e}")

    def add_document(self, filename: str, content: str, doc_type: str = "unknown"):
        """Add a document for RAG."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO documents (filename, content, doc_type, indexed_at) 
                   VALUES (?, ?, ?, ?)""",
                (filename, content, doc_type, datetime.now().isoformat())
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search documents using simple text matching."""
        try:
            cursor = self.conn.cursor()
            query_pattern = f"%{query}%"
            cursor.execute(
                """SELECT id, filename, content, doc_type FROM documents 
                   WHERE content LIKE ? LIMIT ?""",
                (query_pattern, limit)
            )
            results = cursor.fetchall()
            return [
                {"id": r[0], "filename": r[1], "content": r[2], "type": r[3]}
                for r in results
            ]
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []

    def get_conversation_history(self, session_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """SELECT role, content, timestamp FROM messages 
                   WHERE session_id = ? ORDER BY id DESC LIMIT ?""",
                (session_id, limit)
            )
            results = cursor.fetchall()
            return [
                {"role": r[0], "content": r[1], "timestamp": r[2]}
                for r in reversed(results)
            ]
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    def clear_session(self, session_id: str = "default"):
        """Clear conversation history for a session."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            self.conn.commit()
            logger.info(f"Session cleared: {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
