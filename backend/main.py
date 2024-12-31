import socket
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.websocket.handlers import websocket_handler
from app.services.health import router as health_router

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    """
    logger.info("=== STARTING APPLICATION ===")
    
    # Network diagnostics
    logger.info("=== STARTUP DIAGNOSTICS ===")
    logger.info(f"[Startup] Hostname: {socket.gethostname()}")
    try:
        logger.info(f"[Startup] Container IP: {socket.gethostbyname(socket.gethostname())}")
    except Exception as e:
        logger.error(f"[Startup] Failed to get IP: {str(e)}")

    # DNS check
    logger.info("=== OLLAMA DNS CHECK ===")
    try:
        ollama_ip = socket.gethostbyname('ollama')
        logger.info(f"[Startup] Ollama DNS resolution: ollama -> {ollama_ip}")
    except Exception as e:
        logger.error(f"[Startup] Ollama DNS resolution failed: {str(e)}")

    # Connection test
    logger.info("=== OLLAMA CONNECTION TEST ===")
    try:
        logger.info("[Startup] Attempting Ollama connection...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://ollama:11434/api/tags")
            logger.info(f"[Startup] Response status: {response.status_code}")
            logger.info(f"[Startup] Response body: {response.text}")
            models = response.json().get('models', [])
            logger.info(f"[Startup] Available models: {models}")
    except Exception as e:
        logger.error(f"[Startup] Connection error: {str(e)}")

    logger.info("=== STARTUP COMPLETE ===")
    yield
    logger.info("=== SHUTTING DOWN ===")

# Create FastAPI application
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add routes
app.include_router(health_router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)
