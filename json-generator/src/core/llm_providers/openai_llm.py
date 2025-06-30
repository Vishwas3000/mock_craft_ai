"""OpenAI LLM implementation"""

import logging
from typing import Optional, AsyncGenerator, Dict
import openai
from openai import AsyncOpenAI
import tiktoken

from ..base_llm import BaseLLM, LLMProvider, LLMResponse, GenerationConfig
from ..base_llm import LLMConnectionError, LLMGenerationError
from ..config import settings

logger = logging.getLogger(__name__)

class OpenAILLM(BaseLLM):
    """OpenAI API implementation"""
    
    def __init__(self, model_name: Optional[str] = None):
        model_name = model_name or settings.llm.openai_model
        super().__init__(model_name, LLMProvider.OPENAI)
        self.client: Optional[AsyncOpenAI] = None
        self.tokenizer = None
        
    async def _initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            if not settings.llm.openai_api_key:
                raise LLMConnectionError("OpenAI API key not configured")
            
            self.client = AsyncOpenAI(api_key=settings.llm.openai_api_key)
            
            # Initialize tokenizer for token counting
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except:
                # Fallback to cl100k_base encoding
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
            # Test connection
            await self.test_connection()
            
            logger.info(f"✅ OpenAI LLM initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            raise LLMConnectionError(f"OpenAI initialization failed: {e}")
    
    async def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            # Make a minimal API call
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    async def generate(
        self, 
        prompt: str, 
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate response from OpenAI"""
        if not self._is_initialized:
            await self.initialize()
        
        config = config or GenerationConfig()
        
        try:
            # Prepare request parameters
            request_params = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
            }
            
            if config.stop_sequences:
                request_params["stop"] = config.stop_sequences
            
            # Add JSON mode if requested
            if config.response_format == "json":
                request_params["response_format"] = {"type": "json_object"}
            
            # Make API call
            response = await self.client.chat.completions.create(**request_params)
            
            # Extract response
            message = response.choices[0].message
            usage = response.usage
            
            return LLMResponse(
                content=message.content,
                model=response.model,
                provider=self.provider,
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                } if usage else None,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id
                }
            )
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMGenerationError(f"OpenAI API error: {e}")
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
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise LLMGenerationError(f"Streaming failed: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Rough estimation if tokenizer not available
        return len(text) // 4
    
    @property
    def info(self) -> Dict[str, str]:
        """Get information about the LLM"""
        base_info = super().info
        base_info.update({
            "api_key_configured": bool(settings.llm.openai_api_key),
            "supports_json_mode": True,
            "supports_streaming": True,
            "max_context": self._get_max_context()
        })
        return base_info
    
    def _get_max_context(self) -> int:
        """Get max context length for model"""
        context_lengths = {
            "gpt-4-turbo-preview": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16384,
            "gpt-3.5-turbo-16k": 16384
        }
        return context_lengths.get(self.model_name, 4096) 