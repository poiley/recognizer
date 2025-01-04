from tenacity import retry, stop_after_attempt, wait_exponential
import ollama
from fastapi import WebSocket
from typing import Optional

from app.core.logging import logger
from app.core.config import settings

async def load_prompt(prompt_path: str = None) -> str:
    """
    Load prompt template from file or use default.
    """
    if prompt_path is None:
        prompt_path = settings.PROMPT_FILE
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
        prompt_template = await load_prompt()
        
        # Prepare input section
        inputs = f"""<Inputs>
{chunk}
{chunk_index == 0}
{previous_summary if previous_summary else ''}
</Inputs>"""

        full_prompt = f"{prompt_template}\n\n{inputs}"
        
        logger.info(f"Processing chunk {chunk_index + 1}/{total_chunks} (length: {len(chunk)} chars)")
        
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=[{
                    'role': 'user',
                    'content': full_prompt
                }],
                stream=False
            )
            result = response['message']['content']
            
            # Extract content between <summary> tags if present
            if '<summary>' in result and '</summary>' in result:
                result = result.split('<summary>')[1].split('</summary>')[0].strip()
                
            logger.info(f"AI Output for chunk {chunk_index + 1}/{total_chunks} (length: {len(result)} chars)")
            return result

        except Exception as e:
            await websocket.send_json({
                'error': f'AI processing failed: {str(e)}'
            })
            raise

    except Exception as e:
        logger.error(f"Chunk processing failed: {str(e)}")
        raise 