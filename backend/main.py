from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ollama
import asyncio
import tempfile
import os
from pdf2image import convert_from_path
import pytesseract
import gc
import psutil
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential
import base64
from starlette.websockets import WebSocketDisconnect
import json
import binascii
from starlette.websockets import WebSocketDisconnect
import httpx
import socket
from contextlib import asynccontextmanager
import traceback

MAX_WORKERS = 2
MAX_MEMORY_PERCENT = 80
MAX_RETRIES = 3
OLLAMA_TIMEOUT = 300  # 5 minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n=== STARTING APPLICATION ===")

    # Network diagnostics
    print("\n=== STARTUP DIAGNOSTICS ===")
    print(f"[Startup] Hostname: {socket.gethostname()}")
    try:
        print(f"[Startup] Container IP: {socket.gethostbyname(socket.gethostname())}")
    except Exception as e:
        print(f"[Startup] Failed to get IP: {str(e)}")

    # DNS check
    print("\n=== OLLAMA DNS CHECK ===")
    try:
        ollama_ip = socket.gethostbyname('ollama')
        print(f"[Startup] Ollama DNS resolution: ollama -> {ollama_ip}")
    except Exception as e:
        print(f"[Startup] Ollama DNS resolution failed: {str(e)}")

    # Connection test
    print("\n=== OLLAMA CONNECTION TEST ===")
    try:
        print("[Startup] Attempting Ollama connection...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            print("[Startup] Making request to http://ollama:11434/api/tags")
            response = await client.get("http://ollama:11434/api/tags")
            print(f"[Startup] Response status: {response.status_code}")
            print(f"[Startup] Response body: {response.text}")
            models = response.json().get('models', [])
            print(f"[Startup] Available models: {models}")
    except httpx.TimeoutException:
        print("[Startup] Connection timed out")
    except httpx.ConnectError as e:
        print(f"[Startup] Connection failed: {str(e)}")
    except Exception as e:
        print(f"[Startup] Unexpected error: {str(e)}")
        print(f"[Startup] Error type: {type(e)}")

    print("\n=== STARTUP COMPLETE ===\n")
    yield
    print("\n=== SHUTTING DOWN ===")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:5173"],
   allow_methods=["*"],
   allow_headers=["*"]
)


def check_memory():
   memory = psutil.Process().memory_percent()
   if memory > MAX_MEMORY_PERCENT:
       gc.collect()
       return False
   return True


async def send_status_updates(websocket: WebSocket):
    """Send periodic status updates to keep connection alive"""
    try:
        while True:
            await websocket.send_json({"status": "processing", "message": "Processing with Ollama..."})
            await asyncio.sleep(5)  # Update every 5 seconds
    except asyncio.CancelledError:
        pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@lru_cache(maxsize=10)
async def process_chunk(text: str, websocket: WebSocket) -> str:
    if not check_memory():
        print("[Chunk] Memory limit exceeded")
        raise MemoryError("Memory limit exceeded")
    try:
        print("[Chunk] Starting Ollama request")
        print(f"[Chunk] Request length: {len(text)} characters")

        # Start status updates
        status_task = asyncio.create_task(send_status_updates(websocket))

        async with asyncio.timeout(OLLAMA_TIMEOUT):
            try:
                print("[Chunk] Making API call to Ollama")
                response = await ollama.chat(
                    model='mistral',
                    messages=[{'role': 'user', 'content': f'Analyze and summarize: {text}'}]
                )
                print("[Chunk] Ollama request complete")
                print(f"[Chunk] Response length: {len(response['message']['content'])} characters")
                status_task.cancel()  # Stop status updates
                return response['message']['content']
            except ollama.ResponseError as e:
                print(f"[Chunk] Ollama API error: {str(e)}")
                print(f"[Chunk] Response status: {getattr(e, 'status', 'unknown')}")
                status_task.cancel()
                raise
            except Exception as e:
                print(f"[Chunk] Unexpected Ollama error: {str(e)}")
                print(f"[Chunk] Error type: {type(e)}")
                status_task.cancel()
                raise
    except asyncio.TimeoutError:
        print(f"[Chunk] Request timed out after {OLLAMA_TIMEOUT} seconds")
        raise
    except Exception as e:
        print(f"[Chunk] Error in process_chunk: {str(e)}")
        print(f"[Chunk] Error type: {type(e)}")
        raise

async def send_heartbeat(websocket: WebSocket):
    while True:
        try:
            await asyncio.sleep(15)
            await websocket.send_json({"type": "ping"})
        except Exception:
            break


async def process_pdf(pdf_path: str, websocket: WebSocket) -> str:
    failed_chunks = []
    full_text = ''

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        try:
            print("[PDF] Starting conversion")
            try:
                # Add progress updates during conversion
                await websocket.send_json({'status': 'converting', 'message': 'Converting PDF to images...'})

                # Convert with more explicit options
                images = convert_from_path(
                    pdf_path,
                    dpi=200,  # Lower DPI for better memory usage
                    thread_count=1,  # Single thread to avoid memory spikes
                    fmt='jpeg',  # JPEG instead of PPM for lower memory
                    size=(1700, None)  # Limit width, maintain aspect ratio
                )
                total_images = len(images)
                print(f"[PDF] Successfully converted PDF: {total_images} pages")
                await websocket.send_json({'status': 'converted', 'total_pages': total_images})
            except Exception as e:
                print(f"[PDF] Failed to convert PDF: {str(e)}")
                print(f"[PDF] Error type: {type(e)}")
                traceback.print_exc()  # Add full traceback
                raise

            for idx, img in enumerate(images):
                if not check_memory():
                    await websocket.send_json({'warning': 'Memory pressure detected, garbage collecting...'})
                    gc.collect()

                try:
                    print(f"[PDF] OCR page {idx+1}/{total_images}")
                    text = await asyncio.to_thread(pytesseract.image_to_string, img)
                    print(f"[PDF] OCR complete for page {idx+1}")
                    full_text += text + '\n'
                    await websocket.send_json({
                        'progress': (idx + 1) / total_images,
                        'page': idx + 1,
                        'total': total_images
                    })
                except Exception as e:
                    print(f"[PDF] OCR failed for page {idx+1}: {str(e)}")
                    failed_chunks.append(idx)
                finally:
                    del img
                    gc.collect()

            print("[PDF] Starting Ollama analysis")
            try:
                print(f"[PDF] Text length: {len(full_text)} characters")
                summary = await process_chunk(full_text, websocket)
                print("[PDF] Analysis complete")
                return summary
            except Exception as e:
                print(f"[PDF] Ollama analysis failed: {str(e)}")
                print(f"[PDF] Error type: {type(e)}")
                raise

        except Exception as e:
            print(f"[PDF] Critical error: {str(e)}")
            print(f"[PDF] Error type: {type(e)}")
            raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
   await websocket.accept()
   print("[WS] Connected")
   chunks = []
   tmp_path = None
   file_size = 0

   heartbeat_task = asyncio.create_task(send_heartbeat(websocket))

   try:
       while True:
           message = await websocket.receive_json()
           print(f"[WS] Received: {message['type']}, final={message.get('final', False)}")

           if message['type'] == 'start':
               chunks = [message['data']]
               await websocket.send_json({'status': 'receiving'})
           elif message['type'] == 'chunk':
               chunks.append(message['data'])
               progress = message['current'] / message['total']
               print(f"[WS] Progress: {progress:.2f}")
               await websocket.send_json({
                   'status': 'receiving',
                   'progress': progress
               })

           if message.get('final', False):
                print("[WS] Final chunk received, processing...")
                await websocket.send_json({'status': 'processing'})
                try:
                   complete_data = ''.join(chunks)
                   file_bytes = base64.b64decode(complete_data)
                   file_size = len(file_bytes)
                   print(f"[WS] Decoded size: {file_size} bytes")

                   if file_size == 0:
                        raise ValueError("Empty file received")

                   with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                       tmp.write(file_bytes)
                       tmp_path = tmp.name
                       print(f"[WS] PDF saved: {tmp_path}")

                   async with asyncio.timeout(300):  # 5 min timeout
                       await websocket.send_json({'status': 'analyzing'})
                       summary = await process_pdf(tmp_path, websocket)
                       await websocket.send_json({
                           'status': 'complete',
                           'summary': summary
                       })
                       await websocket.receive_json()
                except asyncio.TimeoutError:
                    print("[WS] Processing timed out")
                    await websocket.send_json({'error': 'Processing timed out'})
                except Exception as e:
                    print(f"[WS] Processing error: {str(e)}")
                    await websocket.send_json({'error': f'Processing failed: {str(e)}'})
                break

   except WebSocketDisconnect as e:
       print(f"[WS] Disconnected with code: {e.code}")
   except Exception as e:
       print(f"[WS] Unexpected error: {str(e)}")
       try:
           await websocket.send_json({'error': str(e)})
       except:
           print("[WS] Failed to send error")
   finally:
       heartbeat_task.cancel()
       if tmp_path and os.path.exists(tmp_path):
           try:
               os.unlink(tmp_path)
               print(f"[WS] Cleaned up: {tmp_path}")
           except Exception as e:
               print(f"[WS] Cleanup failed: {str(e)}")
       print("[WS] Connection closed")


if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8000)
