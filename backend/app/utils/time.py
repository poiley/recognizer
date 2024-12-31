def estimate_processing_time(total_chunks: int) -> str:
    """
    Estimate total processing time based on number of chunks.
    """
    total_seconds = total_chunks * 30
    if total_seconds < 60:
        return f"{total_seconds}s"
    minutes = total_seconds // 60
    return f"{minutes}m"

def estimate_remaining_time(current_chunk: int, total_chunks: int) -> str:
    """
    Estimate remaining processing time.
    """
    remaining_chunks = total_chunks - current_chunk
    remaining_seconds = remaining_chunks * 30
    if remaining_seconds < 60:
        return f"{remaining_seconds}s"
    minutes = remaining_seconds // 60
    return f"{minutes}m" 