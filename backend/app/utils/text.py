from typing import List
import tiktoken
from app.core.config import settings
from app.core.logging import logger

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string using tiktoken.
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Token counting failed, falling back to approximate: {str(e)}")
        return len(text.split()) # Fallback to word count

def split_into_chunks(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Split text into chunks of approximately equal token counts.
    
    Args:
        text: Text to split
        chunk_size: Target size for each chunk in tokens (default 2000)
        
    Returns:
        List of text chunks with approximately chunk_size tokens each
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for word in words:
        word_tokens = count_tokens(word + ' ')
        
        if current_token_count + word_tokens > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_token_count = word_tokens
        else:
            current_chunk.append(word)
            current_token_count += word_tokens
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks 