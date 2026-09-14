"""FastAPI server for Tyla-Gen - Fixed version with CLI support."""

import os
import sys
import argparse
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import uvicorn

from .model import ModelManager
from .chat import ChatEngine
from .agent import AgentEngine
from .memory import MemoryManager
from .rag import RAGEngine
from .auth import verify_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tyla.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize components
logger.info("Initializing Tyla-Gen components...")
model_manager = ModelManager()
memory_manager = MemoryManager()
rag_engine = RAGEngine(memory_manager=memory_manager)
chat_engine = ChatEngine(model_manager, memory_manager=memory_manager)
agent_engine = AgentEngine(model_manager, memory_manager=memory_manager, owner_id=os.getenv("TYLA_OWNER_ID", "default"))

# Load model at startup
logger.info("Loading model configuration...")
model_manager.select_model()
logger.info(f"Selected model: {model_manager.model_config['name']}")

if model_manager.load_model():
    logger.info("Model loaded successfully")
else:
    logger.warning("Model failed to load - will attempt to load on first request")

# FastAPI app
app = FastAPI(
    title="Tyla-Gen",
    description="All-in-One AI Server Running in GitHub Codespaces",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ============================================================================
# Request/Response Models
# ============================================================================


class Message(BaseModel):
    """Conversation message."""
    role: str  # "user" or "assistant"
    content: str


class ChatCompletionRequest(BaseModel):
    """Chat completion request."""
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    top_p: Optional[float] = 0.95


class AgentRequest(BaseModel):
    """Agent execution request."""
    task: str
    available_tools: Optional[List[str]] = None
    context: Optional[str] = ""


class StatusResponse(BaseModel):
    """Server status response."""
    status: str
    model: Optional[str] = None
    model_loaded: bool = False
    inference_engine: str = "llama-cpp-python"
    hardware: dict = {}
    timestamp: str


# ============================================================================
# Authentication
# ============================================================================


async def get_api_key(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify API key from Authorization header."""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    if not verify_api_key(token):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token


# ============================================================================
# Public Endpoints
# ============================================================================


@app.get("/health")
async def health():
    """Health check - public endpoint for connectivity."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Tyla-Gen",
        "version": "1.0.0"
    }


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve web UI."""
    try:
        ui_path = Path(__file__).parent.parent / "web" / "index.html"
        if ui_path.exists():
            return ui_path.read_text()
    except Exception as e:
        logger.error(f"Failed to load UI: {e}")
    
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Tyla-Gen</title></head>
    <body>
        <h1>🧠 Tyla-Gen</h1>
        <p>All-in-One AI Server Running in GitHub Codespaces</p>
        <p><a href="/docs">API Documentation</a></p>
    </body>
    </html>
    """


# ============================================================================
# Protected Endpoints - Status & Info
# ============================================================================


@app.get("/v1/status")
async def status(api_key: str = Depends(get_api_key)) -> StatusResponse:
    """Get server and model status."""
    status_info = model_manager.get_status()
    
    return StatusResponse(
        status="operational",
        model=status_info["model"],
        model_loaded=status_info["loaded"],
        inference_engine="llama-cpp-python (CPU-only)",
        hardware=status_info["hardware"],
        timestamp=datetime.now().isoformat()
    )


@app.get("/v1/models")
async def list_models(api_key: str = Depends(get_api_key)):
    """List available models."""
    status_info = model_manager.get_status()
    
    return {
        "current_model": status_info["model"],
        "model_loaded": status_info["loaded"],
        "inference_engine": "llama-cpp-python",
        "local_inference": True,
        "hardware": status_info["hardware"],
        "available_models": [
            {"name": "phi-2", "size_gb": 4.7, "quantization": "q4_k_m", "min_ram": 6},
            {"name": "mistral-7b", "size_gb": 7.0, "quantization": "q4_k_m", "min_ram": 8},
            {"name": "neural-chat", "size_gb": 3.5, "quantization": "q4_k_m", "min_ram": 5},
        ]
    }


# ============================================================================
# Chat Endpoint
# ============================================================================


@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest, api_key: str = Depends(get_api_key)):
    """Process chat completion using local model."""
    try:
        # Ensure model is loaded
        if not model_manager.current_model:
            logger.info("Model not in memory, attempting to load...")
            if not model_manager.load_model():
                raise HTTPException(status_code=503, detail="Model failed to load")
        
        # Get last user message
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message provided")
        
        # Run inference
        logger.info(f"Chat completion request: {user_message[:50]}...")
        response = model_manager.infer(
            user_message,
            max_tokens=request.max_tokens or 2048,
            temperature=request.temperature or 0.7,
            top_p=request.top_p or 0.95,
        )
        
        # Log to memory
        memory_manager.log_message("user", user_message)
        memory_manager.log_message("assistant", response)
        
        return {
            "id": f"tyla-{int(datetime.now().timestamp() * 1000)}",
            "object": "text_completion",
            "created": int(datetime.now().timestamp()),
            "model": model_manager.model_config["name"] if model_manager.model_config else "unknown",
            "choices": [
                {
                    "text": response,
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(user_message.split()) + len(response.split())
            },
            "inference_engine": "llama-cpp-python",
            "local_inference": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Agent Endpoint
# ============================================================================


@app.post("/v1/agent")
async def agent_execution(request: AgentRequest, api_key: str = Depends(get_api_key)):
    """Execute agent with tool use."""
    try:
        if not model_manager.current_model:
            logger.info("Model not in memory, attempting to load...")
            if not model_manager.load_model():
                raise HTTPException(status_code=503, detail="Model failed to load")
        
        logger.info(f"Agent task: {request.task}")
        result = agent_engine.execute(
            request.task,
            available_tools=request.available_tools,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "result": result["result"],
            "iterations": result["iterations"],
            "state": result["state"],
            "inference_engine": "llama-cpp-python",
            "local_inference": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RAG Endpoint
# ============================================================================


@app.get("/v1/rag/search")
async def rag_search(q: str, limit: int = 5, api_key: str = Depends(get_api_key)):
    """Search knowledge base."""
    try:
        results = rag_engine.search(q, limit=limit)
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"RAG search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/rag/documents")
async def list_documents(api_key: str = Depends(get_api_key)):
    """List all documents in knowledge base."""
    try:
        docs = rag_engine.list_documents()
        return {"documents": docs, "count": len(docs)}
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Memory Endpoint
# ============================================================================


@app.get("/v1/memory/history")
async def get_history(session_id: str = "default", api_key: str = Depends(get_api_key)):
    """Get conversation history."""
    try:
        history = memory_manager.get_conversation_history(session_id)
        return {"session_id": session_id, "messages": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/memory/clear")
async def clear_memory(session_id: str = "default", api_key: str = Depends(get_api_key)):
    """Clear conversation history."""
    try:
        memory_manager.clear_session(session_id)
        return {"status": "cleared", "session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the FastAPI server."""
    logger.info(f"Starting Tyla-Gen server on {host}:{port}")
    print(f"\n{'='*60}")
    print(f"🧠 Tyla-Gen Server Starting")
    print(f"{'='*60}")
    print(f"Local: http://localhost:{port}")
    print(f"API: http://localhost:{port}/v1/chat/completions")
    print(f"Docs: http://localhost:{port}/docs")
    print(f"\nModel: {model_manager.model_config['name'] if model_manager.model_config else 'Loading...'}")
    print(f"Engine: llama-cpp-python (CPU-only)")
    print(f"Status: {'Ready' if model_manager.current_model else 'Loading model...'}")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tyla-Gen FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    start_server(host=args.host, port=args.port, reload=args.reload)
