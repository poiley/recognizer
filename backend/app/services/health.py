from fastapi import APIRouter
import psutil
import socket
import httpx
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

@router.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "memory": psutil.virtual_memory().percent,
        "hostname": socket.gethostname(),
        "config": {
            "chunk_size": settings.CHUNK_SIZE,
            "model": settings.OLLAMA_MODEL,
            "token_encoding": settings.TOKEN_ENCODING
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=settings.HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
            health_status["ollama"] = "connected" if response.status_code == 200 else "error"
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        health_status["ollama"] = "error"
        
    return health_status 