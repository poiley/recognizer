from tenacity import retry, stop_after_attempt, wait_exponential
import ollama
import json
from fastapi import WebSocket
from typing import Optional, Dict, Any

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
            content = file.read().strip()
            logger.info(f"Loaded prompt from {prompt_path} (length: {len(content)} chars)")
            return content
    except FileNotFoundError:
        logger.warning(f"Prompt file {prompt_path} not found, using default prompt")
        return """You are processing part of a document. Your task is to create a concise summary of this section while maintaining context with previous sections.

Guidelines:
1. Focus on extracting key information from the current section
2. If you see content that continues from a previous section, briefly acknowledge it and focus on what's new
3. Keep the summary concise and well-structured
4. Use clear paragraph breaks for different topics
5. Avoid repeating information that was covered in previous sections"""

def extract_tag_content(text: str, tag: str) -> str:
    """Extract content between XML-style tags, handling nested tags."""
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    result_start = "<result>"
    result_end = "</result>"
    
    try:
        # First try direct tag extraction
        start = text.index(start_tag) + len(start_tag)
        end = text.index(end_tag)
        return text[start:end].strip()
    except ValueError:
        try:
            # Try extracting from within <result> tags
            result_content_start = text.index(result_start) + len(result_start)
            result_content_end = text.index(result_end)
            result_content = text[result_content_start:result_content_end].strip()
            
            # Now try to find our tag within the result content
            start = result_content.index(start_tag) + len(start_tag)
            end = result_content.index(end_tag)
            return result_content[start:end].strip()
        except ValueError:
            return ""

def validate_markdown_structure(summary: str) -> str:
    """Ensure summary has proper markdown structure"""
    lines = summary.split('\n')
    if not any(line.startswith('#') for line in lines):
        return f"# Summary\n\n{summary}"
    return summary

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def process_chunk(
    chunk: str, 
    websocket: WebSocket, 
    chunk_index: int, 
    total_chunks: int, 
    previous_context: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Process a document chunk and return both context and summary.
    
    Args:
        chunk: The text chunk to process
        websocket: WebSocket connection for status updates
        chunk_index: Current chunk index
        total_chunks: Total number of chunks
        previous_context: Context from previous chunk processing
        
    Returns:
        Dict containing 'context' and 'summary' keys
    """
    try:
        prompt_template = await load_prompt()
        
        # Initialize or maintain context
        if previous_context is None:
            previous_context = {
                "metadata": {
                    "partial_titles": [],
                    "current_depth": 1,
                    "pending_sections": []
                },
                "content": {
                    "active_concepts": [],
                    "knowledge_chain": []
                }
            }
        
        # Prepare input section
        inputs = f"""<Inputs>
{chunk}: str  # Current text section for analysis
{chunk_index == 0}: bool  # Start of new document flag
{json.dumps(previous_context, indent=2)}: dict  # Previous context
</Inputs>"""

        full_prompt = f"{prompt_template}\n\n{inputs}"
        
        logger.info(f"Processing chunk {chunk_index + 1}/{total_chunks} (length: {len(chunk)} chars)")
        
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': '''Your response must be in this exact format:
<context>
{
    "metadata": {
        "partial_titles": [],
        "current_depth": 1,
        "pending_sections": []
    },
    "content": {
        "active_concepts": [],
        "knowledge_chain": []
    }
}
</context>

<summary>
# [Section Title]

## Overview
[One paragraph overview]

## New Concepts
### [Concept Name]
- Definition: [Clear definition]
- Example: [Concrete example]
- Prerequisites: [Required concepts]

## Technical Implementation
[Implementation details with examples]

## Related Concepts
[List of related concepts with brief connections]
</summary>'''
                    },
                    {
                        'role': 'user',
                        'content': full_prompt
                    }
                ],
                stream=False
            )
            result = response['message']['content']
            
            # Add detailed logging of AI response
            logger.debug(f"Raw AI response for chunk {chunk_index + 1}:\n{result}")
            
            # Extract both context and summary
            context = extract_tag_content(result, "context")
            summary = extract_tag_content(result, "summary")
            
            # Log extracted content
            logger.debug(f"Extracted context for chunk {chunk_index + 1}:\n{context}")
            logger.debug(f"Extracted summary for chunk {chunk_index + 1}:\n{summary}")
            
            if not context or not summary:
                logger.warning(f"Missing context or summary in AI response for chunk {chunk_index + 1}")
                logger.warning("AI response structure:\n" + "\n".join(
                    f"- Line {i+1}: {line[:100]}..." for i, line in enumerate(result.split('\n'))
                ))
                
            # Parse context back into dictionary if present
            try:
                context_dict = json.loads(context) if context else previous_context
            except json.JSONDecodeError:
                logger.error(f"Failed to parse context JSON for chunk {chunk_index + 1}")
                logger.error(f"Invalid context content:\n{context}")
                context_dict = previous_context
                
            logger.info(f"AI Output for chunk {chunk_index + 1}/{total_chunks} (context: {len(context)} chars, summary: {len(summary)} chars)")
            logger.info(f"Context: {context_dict}")
            logger.info(f"Summary: {summary}")
            
            return {
                "context": context_dict,
                "summary": summary or result  # Fallback to full response if no summary tag
            }

        except Exception as e:
            logger.error(f"AI processing error for chunk {chunk_index + 1}: {str(e)}")
            await websocket.send_json({
                'error': f'AI processing failed: {str(e)}'
            })
            raise

    except Exception as e:
        logger.error(f"Chunk processing failed: {str(e)}")
        raise 