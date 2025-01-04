from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    CORS_ORIGINS: List[str] = os.environ.get("CORS_ORIGINS", ["http://localhost:5173"]).split(",")
    CHUNK_SIZE: int = os.environ.get("CHUNK_SIZE", 3000)
    OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
    OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "mistral")
    TOKEN_ENCODING: str = os.environ.get("TOKEN_ENCODING", "cl100k_base")
    PROMPT_FILE: str = os.environ.get("PROMPT_FILE", "prompts/default.txt")
    HEALTH_CHECK_TIMEOUT: float = float(os.environ.get("HEALTH_CHECK_TIMEOUT", "5.0"))
    OLLAMA_TIMEOUT: float = float(os.environ.get("OLLAMA_TIMEOUT", "30.0"))

    class Config:
        env_file = ".env"

settings = Settings() 