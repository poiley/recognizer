from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
import ollama
from fastapi import WebSocket

from app.core.logging import logger

async def load_prompt(prompt_path: str = "prompts/default.txt") -> str:
    try:
        with open(prompt_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        logger.warning(f"Prompt file {prompt_path} not found, using default prompt")
        return "Summarize this section of text concisely:"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@lru_cache(maxsize=10)
async def process_chunk(chunk: str, websocket: WebSocket) -> str:
    try:
        prompt_template = await load_prompt('default')
        full_prompt = f"{prompt_template}\n\nText to analyze:\n{chunk}"

        try:
            response = ollama.chat(
                model='mistral',
                messages=[{
                    'role': 'user',
                    'content': full_prompt
                }],
                stream=False
            )
            return response['message']['content']

        except Exception as e:
            logger.error(f"Ollama processing failed: {str(e)}")
            await websocket.send_json({
                'error': f'AI processing failed: {str(e)}'
            })
            raise

    except Exception as e:
        logger.error(f"Chunk processing failed: {str(e)}")
        await websocket.send_json({
            'error': f'Chunk processing failed: {str(e)}'
        })
        raise 