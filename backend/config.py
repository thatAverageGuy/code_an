import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Authentication
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # File Handling
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/code_analyzer")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Graph Settings
    GRAPH_OUTPUT_DIR: str = "graph_output"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create necessary directories
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.GRAPH_OUTPUT_DIR, exist_ok=True)