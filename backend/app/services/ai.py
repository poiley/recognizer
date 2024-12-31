from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
import ollama
from fastapi import WebSocket
from typing import Optional

from app.core.logging import logger

async def load_prompt(prompt_path: str = "prompts/default.txt") -> str:
    try:
        with open(prompt_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        logger.warning(f"Prompt file {prompt_path} not found, using default prompt")
        return """You are processing part of a document. Your task is to create a concise summary of this section while maintaining context with previous sections.

Guidelines:
1. Focus on extracting key information from the current section
2. If you see content that continues from a previous section, briefly acknowledge it and focus on what's new
3. Keep the summary concise and well-structured
4. Use clear paragraph breaks for different topics
5. Avoid repeating information that was covered in previous sections"""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def process_chunk(chunk: str, websocket: WebSocket, chunk_index: int, total_chunks: int, previous_summary: Optional[str] = None) -> str:
    try:
        prompt_template = await load_prompt('default')
        context = f"This is chunk {chunk_index + 1} of {total_chunks}."
        
        # Pass more focused context about previous content
        if previous_summary:
            # Extract key points from previous summary to maintain flow
            key_points = previous_summary.split('\n')[-5:]  # Take last few key points
            points_text = '\n'.join(key_points)
            context = f"{context}\n\nKey points from previous section:\n{points_text}\n\nContinue the document flow, focusing on new information while maintaining narrative coherence."
        
        full_prompt = f"{prompt_template}\n\n{context}\n\nText to analyze:\n{chunk}"
        
        logger.info(f"Processing chunk {chunk_index + 1}/{total_chunks} (length: {len(chunk)} chars):\n{chunk}")
        logger.info("Chunk boundary marker ----")

        try:
            response = ollama.chat(
                model='mistral',
                messages=[{
                    'role': 'user',
                    'content': full_prompt
                }],
                stream=False
            )
            result = response['message']['content']
            logger.info(f"AI Output for chunk {chunk_index + 1}/{total_chunks} (length: {len(result)} chars):\n{result}")
            return result

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