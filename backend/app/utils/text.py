from typing import List
import tiktoken
from app.core.logging import logger
from app.core.config import settings

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string using tiktoken.
    """
    try:
        encoding = tiktoken.get_encoding(settings.TOKEN_ENCODING)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Token counting failed, falling back to approximate: {str(e)}")
        return len(text.split()) # Fallback to word count

def split_into_chunks(text: str, chunk_size: int = None) -> List[str]:
    """
    Split text into chunks while trying to preserve paragraph structure.
    
    Args:
        text: Text to split
        chunk_size: Target size for each chunk in tokens. If None, uses settings.CHUNK_SIZE
        
    Returns:
        List of text chunks with approximately chunk_size tokens each,
        preserving paragraph boundaries where possible
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE

    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph + '\n\n')
        
        # If a single paragraph exceeds chunk size, split it on sentences
        if paragraph_tokens > chunk_size:
            sentences = paragraph.replace('. ', '.\n').split('\n')
            for sentence in sentences:
                sentence_tokens = count_tokens(sentence + ' ')
                if current_token_count + sentence_tokens > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_token_count = sentence_tokens
                else:
                    current_chunk.append(sentence)
                    current_token_count += sentence_tokens
        # Otherwise try to keep paragraphs together
        elif current_token_count + paragraph_tokens > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [paragraph]
            current_token_count = paragraph_tokens
        else:
            current_chunk.append(paragraph)
            current_token_count += paragraph_tokens
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks 