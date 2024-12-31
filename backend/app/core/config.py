from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    MAX_MEMORY_PERCENT: int = 90
    OLLAMA_TIMEOUT: int = 300
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    CHUNK_SIZE: int = 2000
    OLLAMA_HOST: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "mistral"
    MAX_RETRIES: int = 3
    HEARTBEAT_INTERVAL: int = 5

    class Config:
        env_file = ".env"

settings = Settings() 