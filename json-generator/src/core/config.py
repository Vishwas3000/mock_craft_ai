"""Configuration management for the JSON Generator"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConfig(BaseSettings):
    """LLM-specific configuration"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_temperature: float = Field(0.7, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(2000, env="OPENAI_MAX_TOKENS")
    
    # Ollama Configuration
    ollama_host: str = Field("http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field("llama3.1:8b", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(120, env="OLLAMA_TIMEOUT")
    
    # Local Model Configuration
    local_model_path: Optional[str] = Field(None, env="LOCAL_MODEL_PATH")
    local_model_type: str = Field("llama_cpp", env="LOCAL_MODEL_TYPE")
    local_model_device: str = Field("cpu", env="LOCAL_MODEL_DEVICE")
    local_model_gpu_layers: int = Field(0, env="LOCAL_MODEL_GPU_LAYERS")
    
    @validator("local_model_path")
    def validate_model_path(cls, v):
        if v and not Path(v).exists():
            print(f"⚠️  Warning: Local model path '{v}' does not exist")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

class AppConfig(BaseSettings):
    """Application configuration"""
    
    app_name: str = "JSON Generator"
    app_env: str = Field("development", env="APP_ENV")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    models_dir: Optional[Path] = None
    data_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    
    # Feature flags
    enable_web_search: bool = Field(True, env="ENABLE_WEB_SEARCH")
    enable_caching: bool = Field(True, env="ENABLE_CACHING")
    enable_streaming: bool = Field(True, env="ENABLE_STREAMING")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up paths after initialization
        self.models_dir = self.project_root / "models"
        self.data_dir = self.project_root / "data"
        self.cache_dir = self.data_dir / "cache"
        
        # Create directories if they don't exist
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    class Config:
        env_file = ".env"

class Settings:
    """Global settings singleton"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.app = AppConfig()
            cls._instance.llm = LLMConfig()
        return cls._instance
    
    def get_llm_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for specific LLM provider"""
        if provider == "openai":
            return {
                "api_key": self.llm.openai_api_key,
                "model": self.llm.openai_model,
                "temperature": self.llm.openai_temperature,
                "max_tokens": self.llm.openai_max_tokens,
            }
        elif provider == "ollama":
            return {
                "host": self.llm.ollama_host,
                "model": self.llm.ollama_model,
                "timeout": self.llm.ollama_timeout,
            }
        elif provider == "local":
            return {
                "model_path": self.llm.local_model_path,
                "model_type": self.llm.local_model_type,
                "device": self.llm.local_model_device,
                "n_gpu_layers": self.llm.local_model_gpu_layers,
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")

# Create global settings instance
settings = Settings()

# Logging configuration
import logging
from rich.logging import RichHandler

def setup_logging():
    """Configure logging with Rich handler"""
    logging.basicConfig(
        level=getattr(logging, settings.app.log_level),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

# Run logging setup when module is imported
setup_logging() 