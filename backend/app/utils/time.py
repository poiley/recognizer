from typing import List
from statistics import mean
from app.core.config import settings

class TimeEstimator:
    def __init__(self):
        self.processing_times: List[float] = []
        self.default_chunk_time = settings.DEFAULT_CHUNK_TIME  # Add to settings

    def add_processing_time(self, seconds: float) -> None:
        """Record actual processing time for a chunk."""
        self.processing_times.append(seconds)
        
    def get_average_chunk_time(self) -> float:
        """Get average processing time per chunk."""
        if not self.processing_times:
            return self.default_chunk_time
        return mean(self.processing_times)

    def format_time(self, seconds: float) -> str:
        """Format time duration with appropriate units and precision."""
        if seconds < 60:
            return f"{int(seconds)}s"
        
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes == 0:
            return f"{remaining_seconds}s"
        elif remaining_seconds == 0:
            return f"{minutes}m"
        else:
            return f"{minutes}m {remaining_seconds}s"

    def estimate_total_time(self, total_chunks: int) -> str:
        """Estimate total processing time based on actual performance."""
        avg_time = self.get_average_chunk_time()
        total_seconds = total_chunks * avg_time
        return self.format_time(total_seconds)

    def estimate_remaining_time(self, current_chunk: int, total_chunks: int) -> str:
        """Estimate remaining time based on actual performance."""
        remaining_chunks = total_chunks - current_chunk
        avg_time = self.get_average_chunk_time()
        remaining_seconds = remaining_chunks * avg_time
        return self.format_time(remaining_seconds)

# Global estimator instance
estimator = TimeEstimator() 