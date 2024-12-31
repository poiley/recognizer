import base64
import os
import tempfile
import asyncio
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.core.logging import logger
from app.services.pdf import process_pdf
from app.websocket.connection import send_heartbeat

async def websocket_handler(websocket: WebSocket):
    """
    Handle WebSocket connection and messages.
    """
    await websocket.accept()
    heartbeat_task = None
    
    try:
        # Start heartbeat
        heartbeat_task = asyncio.create_task(send_heartbeat(websocket))
        
        while True:
            # Receive message
            message = await websocket.receive_json()
            
            if message['type'] == 'start':
                # Create temporary file for PDF
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    # Decode and save PDF
                    pdf_data = base64.b64decode(message['data'])
                    tmp_file.write(pdf_data)
                    tmp_file.flush()
                    
                    try:
                        # Process PDF
                        summary = await process_pdf(tmp_file.name, websocket)
                        
                        # Send completion message
                        await websocket.send_json({
                            'complete': True,
                            'summary': summary
                        })
                        
                    finally:
                        # Cleanup
                        os.unlink(tmp_file.name)
                        
            elif message['type'] == 'cancel':
                break
                
    except WebSocketDisconnect:
        logger.info("[WebSocket] Client disconnected")
    except Exception as e:
        logger.error(f"[WebSocket] Error: {str(e)}")
        try:
            await websocket.send_json({
                'error': f'Server error: {str(e)}'
            })
        except:
            pass
    finally:
        if heartbeat_task:
            heartbeat_task.cancel() 