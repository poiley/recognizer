import asyncio
from fastapi import WebSocket
from app.core.logging import logger

async def send_heartbeat(websocket: WebSocket):
    """
    Send periodic heartbeat messages to keep the WebSocket connection alive.
    """
    try:
        while True:
            await websocket.send_json({"type": "ping"})
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        logger.info("[Heartbeat] Task cancelled")
    except Exception as e:
        logger.error(f"[Heartbeat] Error: {str(e)}") 