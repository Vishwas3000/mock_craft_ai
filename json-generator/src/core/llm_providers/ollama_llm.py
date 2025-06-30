"""Ollama LLM implementation for locally hosted models"""

import logging
import aiohttp
import json
from typing import Optional, AsyncGenerator, Dict, Any, List
from urllib.parse import urljoin

from ..base_llm import BaseLLM, LLMProvider, LLMResponse, GenerationConfig
from ..base_llm import LLMConnectionError, LLMGenerationError
from ..config import settings

logger = logging.getLogger(__name__)

class OllamaLLM(BaseLLM):
    """Ollama implementation for locally hosted models"""
    
    def __init__(self, model_name: Optional[str] = None, host: Optional[str] = None):
        model_name = model_name or settings.llm.ollama_model
        super().__init__(model_name, LLMProvider.OLLAMA)
        self.host = host or settings.llm.ollama_host
        self.timeout = settings.llm.ollama_timeout
        self._available_models = []
        
    async def _initialize(self) -> None:
        """Initialize Ollama connection"""
        try:
            # Check if Ollama is running
            if not await self._check_ollama_status():
                raise LLMConnectionError(
                    f"Ollama is not running at {self.host}. "
                    "Please start Ollama with: ollama serve"
                )
            
            # Get list of available models
            self._available_models = await self._list_models()
            
            # Check if requested model is available
            if self.model_name not in [m['name'] for m in self._available_models]:
                logger.warning(
                    f"Model {self.model_name} not found. "
                    f"Available models: {[m['name'] for m in self._available_models]}"
                )
                
                # Try to pull the model
                logger.info(f"Attempting to pull model: {self.model_name}")
                await self._pull_model(self.model_name)
            
            logger.info(f"✅ Ollama LLM initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise LLMConnectionError(f"Ollama initialization failed: {e}")
    
    async def _check_ollama_status(self) -> bool:
        """Check if Ollama server is running"""
        try:
            async with aiohttp.ClientSession() as session:
                url = urljoin(self.host, "/api/tags")
                async with session.get(url, timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def _list_models(self) -> List[Dict[str, Any]]:
        """List available models in Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                url = urljoin(self.host, "/api/tags")
                async with session.get(url) as response:
                    data = await response.json()
                    return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def _pull_model(self, model_name: str) -> None:
        """Pull a model from Ollama registry"""
        try:
            async with aiohttp.ClientSession() as session:
                url = urljoin(self.host, "/api/pull")
                data = {"name": model_name, "stream": False}
                
                async with session.post(url, json=data, timeout=600) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to pull model: {await response.text()}")
                    
                    logger.info(f"Successfully pulled model: {model_name}")
                    
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            # Try a simple generation
            async with aiohttp.ClientSession() as session:
                url = urljoin(self.host, "/api/generate")
                data = {
                    "model": self.model_name,
                    "prompt": "Hi",
                    "stream": False,
                    "options": {"num_predict": 5}
                }
                
                async with session.post(url, json=data, timeout=30) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
    
    async def generate(
        self, 
        prompt: str, 
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate response from Ollama"""
        if not self._is_initialized:
            await self.initialize()
        
        config = config or GenerationConfig()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = urljoin(self.host, "/api/generate")
                
                # Prepare request
                data = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": config.temperature,
                        "num_predict": config.max_tokens,
                        "top_p": config.top_p,
                        "stop": config.stop_sequences or []
                    }
                }
                
                # Add JSON formatting if requested
                if config.response_format == "json":
                    data["format"] = "json"
                
                # Make request
                async with session.post(
                    url, 
                    json=data, 
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMGenerationError(f"Ollama error: {error_text}")
                    
                    result = await response.json()
                    
                    return LLMResponse(
                        content=result["response"],
                        model=self.model_name,
                        provider=self.provider,
                        usage={
                            "prompt_tokens": result.get("prompt_eval_count", 0),
                            "completion_tokens": result.get("eval_count", 0),
                            "total_tokens": (
                                result.get("prompt_eval_count", 0) + 
                                result.get("eval_count", 0)
                            )
                        },
                        metadata={
                            "total_duration": result.get("total_duration"),
                            "load_duration": result.get("load_duration"),
                            "eval_duration": result.get("eval_duration")
                        }
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"Ollama request failed: {e}")
            raise LLMGenerationError(f"Ollama request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            raise LLMGenerationError(f"Generation failed: {e}")
    
    async def generate_stream(
        self, 
        prompt: str, 
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        if not self._is_initialized:
            await self.initialize()
        
        config = config or GenerationConfig()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = urljoin(self.host, "/api/generate")
                
                data = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": config.temperature,
                        "num_predict": config.max_tokens,
                        "top_p": config.top_p
                    }
                }
                
                async with session.post(url, json=data) as response:
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise LLMGenerationError(f"Streaming failed: {e}")
    
    @property
    def info(self) -> Dict[str, str]:
        """Get information about the LLM"""
        base_info = super().info
        base_info.update({
            "host": self.host,
            "available_models": [m['name'] for m in self._available_models],
            "supports_json_mode": True,
            "supports_streaming": True
        })
        return base_info 