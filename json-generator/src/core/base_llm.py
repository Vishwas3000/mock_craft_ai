"""Base LLM interface and implementations"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncGenerator, Any
from dataclasses import dataclass
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    LOCAL = "local"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    provider: LLMProvider
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class GenerationConfig:
    """Configuration for generation"""
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    response_format: Optional[str] = None  # "json" or None

class BaseLLM(ABC):
    """Abstract base class for all LLM implementations"""
    
    def __init__(self, model_name: str, provider: LLMProvider):
        self.model_name = model_name
        self.provider = provider
        self._is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize the LLM (load models, check connections, etc.)"""
        if not self._is_initialized:
            await self._initialize()
            self._is_initialized = True
    
    @abstractmethod
    async def _initialize(self) -> None:
        """Provider-specific initialization"""
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        prompt: str, 
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response"""
        pass
    
    async def generate_json(
        self, 
        prompt: str, 
        schema: Optional[Dict] = None,
        config: Optional[GenerationConfig] = None
    ) -> Dict:
        """Generate JSON output"""
        if config is None:
            config = GenerationConfig()
        
        # Add JSON formatting to prompt
        json_prompt = self._format_json_prompt(prompt, schema)
        config.response_format = "json"
        
        response = await self.generate(json_prompt, config)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            # Try to extract JSON from response
            return self._extract_json(response.content)
    
    def _format_json_prompt(self, prompt: str, schema: Optional[Dict]) -> str:
        """Format prompt for JSON generation"""
        json_instruction = "\n\nProvide your response as valid JSON."
        
        if schema:
            json_instruction += f"\n\nFollow this schema:\n{json.dumps(schema, indent=2)}"
        
        return prompt + json_instruction
    
    def _extract_json(self, text: str) -> Dict:
        """Try to extract JSON from text"""
        import re
        
        # Try to find JSON in the text
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        
        # If no valid JSON found, return empty dict
        logger.warning("No valid JSON found in response")
        return {}
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the LLM is accessible"""
        pass
    
    @property
    def info(self) -> Dict[str, str]:
        """Get information about the LLM"""
        return {
            "provider": self.provider.value,
            "model": self.model_name,
            "initialized": self._is_initialized
        }

class LLMError(Exception):
    """Base exception for LLM errors"""
    pass

class LLMConnectionError(LLMError):
    """Error connecting to LLM"""
    pass

class LLMGenerationError(LLMError):
    """Error during generation"""
    pass 