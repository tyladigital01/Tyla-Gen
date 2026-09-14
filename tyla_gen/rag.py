"""RAG (Retrieval-Augmented Generation) system for local knowledge retrieval."""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any
from .memory import MemoryManager

logger = logging.getLogger(__name__)


class RAGEngine:
    """Manages document indexing and retrieval for local knowledge base."""

    def __init__(self, knowledge_path: str = "./knowledge", memory_manager: MemoryManager = None):
        self.knowledge_path = Path(knowledge_path)
        self.knowledge_path.mkdir(exist_ok=True)
        self.memory = memory_manager
        self.documents = {}
        self.load_documents()

    def load_documents(self):
        """Load all documents from knowledge directory."""
        try:
            for file_path in self.knowledge_path.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in [".txt", ".md", ".json"]:
                        self._load_file(file_path, ext)
            logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")

    def _load_file(self, file_path: Path, file_type: str):
        """Load and parse a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            doc_type = "markdown" if file_type == ".md" else "json" if file_type == ".json" else "text"
            
            self.documents[file_path.name] = {
                "path": str(file_path),
                "content": content,
                "type": doc_type,
                "size": len(content),
            }
            
            # Store in memory if available
            if self.memory:
                self.memory.add_document(file_path.name, content, doc_type)
            
            logger.info(f"Loaded document: {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant documents."""
        try:
            # Try memory search first
            if self.memory:
                results = self.memory.search_documents(query, limit)
                if results:
                    return results
            
            # Fallback to simple text matching
            query_lower = query.lower()
            matches = []
            
            for filename, doc in self.documents.items():
                if query_lower in doc["content"].lower():
                    # Find relevant excerpts
                    excerpt = self._extract_excerpt(doc["content"], query_lower, 200)
                    matches.append({
                        "filename": filename,
                        "type": doc["type"],
                        "excerpt": excerpt,
                        "relevance": doc["content"].lower().count(query_lower),
                    })
            
            # Sort by relevance
            matches.sort(key=lambda x: x["relevance"], reverse=True)
            return matches[:limit]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _extract_excerpt(self, content: str, query: str, context_length: int = 200) -> str:
        """Extract relevant excerpt from document."""
        try:
            idx = content.lower().find(query.lower())
            if idx == -1:
                return content[:context_length] + "..."
            
            start = max(0, idx - context_length // 2)
            end = min(len(content), idx + context_length // 2)
            return content[start:end] + ("..." if end < len(content) else "")
        except:
            return content[:context_length] + "..."

    def add_document(self, filename: str, content: str, doc_type: str = "text"):
        """Add a new document to knowledge base."""
        try:
            file_path = self.knowledge_path / filename
            file_path.write_text(content, encoding="utf-8")
            
            self.documents[filename] = {
                "path": str(file_path),
                "content": content,
                "type": doc_type,
                "size": len(content),
            }
            
            if self.memory:
                self.memory.add_document(filename, content, doc_type)
            
            logger.info(f"Added document: {filename}")
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    def get_context(self, query: str, max_context_length: int = 2000) -> str:
        """Get formatted context from RAG search results."""
        results = self.search(query, limit=3)
        
        if not results:
            return ""
        
        context = "### Knowledge Base Context:\n"
        total_length = 0
        
        for result in results:
            excerpt = result.get("excerpt", result.get("content", ""))
            if total_length + len(excerpt) > max_context_length:
                break
            
            context += f"\n**{result['filename']}** ({result['type']}):\n{excerpt}\n"
            total_length += len(excerpt)
        
        return context

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all loaded documents."""
        return [
            {
                "filename": name,
                "type": doc["type"],
                "size": doc["size"],
                "path": doc["path"],
            }
            for name, doc in self.documents.items()
        ]
