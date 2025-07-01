"""Unified LLM Manager for handling multiple providers"""

import logging
from typing import Dict, Optional, List, Any
from enum import Enum
import asyncio
from rich.console import Console
from rich.table import Table

from .base_llm import BaseLLM, LLMProvider, GenerationConfig, LLMResponse
from .llm_providers.openai_llm import OpenAILLM
from .llm_providers.ollama_llm import OllamaLLM
# from .llm_providers.local_llm import LocalLLM
from .config import settings

logger = logging.getLogger(__name__)
console = Console()

class ModelPriority(Enum):
    """Model selection priority"""
    QUALITY = "quality"      # Prefer quality (API models)
    SPEED = "speed"         # Prefer speed (local models)
    COST = "cost"          # Prefer cost (local > ollama > API)
    BALANCED = "balanced"   # Balance all factors

class LLMManager:
    """Manages multiple LLM providers with fallback support"""
    
    def __init__(self):
        self.models: Dict[str, BaseLLM] = {}
        self.default_model: Optional[str] = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize all configured LLMs"""
        if self._initialized:
            return
        
        console.print("[bold blue]Initializing LLM Manager...[/bold blue]")
        
        # Try to initialize each provider
        providers = [
            ("openai", self._init_openai),
            ("ollama", self._init_ollama),
            ("local", self._init_local)
        ]
        
        results = []
        for name, init_func in providers:
            try:
                success = await init_func()
                results.append((name, success))
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
                results.append((name, False))
        
        # Set default model (first successful initialization)
        for name, success in results:
            if success and not self.default_model:
                self.default_model = name
        
        self._initialized = True
        self._print_status()
        
        if not self.models:
            raise Exception("No LLM providers could be initialized!")
    
    async def _init_openai(self) -> bool:
        """Initialize OpenAI provider"""
        try:
            if not settings.llm.openai_api_key:
                logger.warning("OpenAI API key not configured")
                return False
            
            llm = OpenAILLM()
            await llm.initialize()
            
            self.models["openai"] = llm
            logger.info("✅ OpenAI initialized")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            return False
    
    async def _init_ollama(self) -> bool:
        """Initialize Ollama provider"""
        try:
            llm = OllamaLLM()
            await llm.initialize()
            
            self.models["ollama"] = llm
            logger.info("✅ Ollama initialized")
            return True
            
        except Exception as e:
            logger.error(f"Ollama initialization failed: {e}")
            return False
    
    async def _init_local(self) -> bool:
        """Initialize local model provider"""
        try:
            if not settings.llm.local_model_path:
                logger.warning("Local model path not configured")
                return False
            # llm = LocalLLM()
            # await llm.initialize()
            # self.models["local"] = llm
            # logger.info("✅ Local model initialized")
            # return True
            logger.warning("LocalLLM is not implemented.")
            return False
        except Exception as e:
            logger.error(f"Local model initialization failed: {e}")
            return False
    
    def _print_status(self):
        """Print status table of all models"""
        table = Table(title="LLM Provider Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Info", style="blue")
        
        # Check each provider
        providers = ["openai", "ollama", "local"]
        for provider in providers:
            if provider in self.models:
                llm = self.models[provider]
                info = llm.info
                table.add_row(
                    provider.upper(),
                    "✅ Ready",
                    info.get("model", "N/A"),
                    self._get_provider_info(provider, info)
                )
            else:
                table.add_row(
                    provider.upper(),
                    "❌ Not Available",
                    "-",
                    self._get_provider_error(provider)
                )
        
        console.print(table)
        
        if self.default_model:
            console.print(f"\n[bold green]Default model: {self.default_model}[/bold green]")
    
    def _get_provider_info(self, provider: str, info: Dict) -> str:
        """Get provider-specific info for display"""
        if provider == "openai":
            return f"Context: {info.get('max_context', 'N/A')}"
        elif provider == "ollama":
            return f"Host: {info.get('host', 'N/A')}"
        elif provider == "local":
            return f"Size: {info.get('model_size', 'N/A')}"
        return ""
    
    def _get_provider_error(self, provider: str) -> str:
        """Get provider-specific error message"""
        if provider == "openai":
            return "API key not set"
        elif provider == "ollama":
            return "Ollama not running"
        elif provider == "local":
            return "Model not found"
        return "Unknown error"
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
        fallback: bool = True
    ) -> LLMResponse:
        """Generate response with automatic fallback"""
        
        if not self._initialized:
            await self.initialize()
        
        # Use specified model or default
        model_name = model or self.default_model
        
        if not model_name or model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not available")
        
        # Try primary model
        try:
            llm = self.models[model_name]
            response = await llm.generate(prompt, config)
            return response
            
        except Exception as e:
            logger.error(f"Generation failed with {model_name}: {e}")
            
            if not fallback:
                raise
            
            # Try fallback models
            fallback_order = self._get_fallback_order(model_name)
            
            for fallback_model in fallback_order:
                if fallback_model in self.models:
                    try:
                        logger.info(f"Trying fallback model: {fallback_model}")
                        llm = self.models[fallback_model]
                        response = await llm.generate(prompt, config)
                        response.metadata = response.metadata or {}
                        response.metadata["fallback_used"] = True
                        response.metadata["original_model"] = model_name
                        return response
                        
                    except Exception as e:
                        logger.error(f"Fallback {fallback_model} also failed: {e}")
                        continue
            
            raise Exception("All models failed to generate response")
    
    async def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None
    ) -> Dict:
        """Generate JSON response"""
        if not self._initialized:
            await self.initialize()
        
        model_name = model or self.default_model
        llm = self.models[model_name]
        
        return await llm.generate_json(prompt, schema, config)
    
    def _get_fallback_order(self, primary_model: str) -> List[str]:
        """Get fallback order for a given model"""
        all_models = list(self.models.keys())
        all_models.remove(primary_model)
        
        # Define fallback preferences
        if primary_model == "openai":
            # OpenAI -> Ollama -> Local
            return ["ollama", "local"]
        elif primary_model == "ollama":
            # Ollama -> Local -> OpenAI
            return ["local", "openai"]
        else:  # local
            # Local -> Ollama -> OpenAI
            return ["ollama", "openai"]
    
    def select_model_by_priority(self, priority: ModelPriority) -> str:
        """Select best model based on priority"""
        if not self.models:
            raise Exception("No models available")
        
        if priority == ModelPriority.QUALITY:
            # Prefer: OpenAI > Ollama > Local
            for model in ["openai", "ollama", "local"]:
                if model in self.models:
                    return model
                    
        elif priority == ModelPriority.SPEED:
            # Prefer: Local > Ollama > OpenAI
            for model in ["local", "ollama", "openai"]:
                if model in self.models:
                    return model
                    
        elif priority == ModelPriority.COST:
            # Prefer: Local > Ollama > OpenAI
            for model in ["local", "ollama", "openai"]:
                if model in self.models:
                    return model
                    
        else:  # BALANCED
            # Prefer: Ollama > Local > OpenAI
            for model in ["ollama", "local", "openai"]:
                if model in self.models:
                    return model
        
        return self.default_model
    
    async def benchmark_models(self, test_prompt: str = "Hello, how are you?") -> Dict[str, Any]:
        """Benchmark all available models"""
        results = {}
        
        for model_name, llm in self.models.items():
            try:
                import time
                start_time = time.time()
                
                response = await llm.generate(test_prompt)
                
                end_time = time.time()
                
                results[model_name] = {
                    "success": True,
                    "latency": end_time - start_time,
                    "response_length": len(response.content),
                    "tokens_used": response.usage.get("total_tokens", 0) if response.usage else 0
                }
                
            except Exception as e:
                results[model_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    @property
    def available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())
    
    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a specific model or all models"""
        if model:
            if model in self.models:
                return self.models[model].info
            else:
                return {"error": f"Model '{model}' not found"}
        else:
            return {name: llm.info for name, llm in self.models.items()}


# Convenience function for testing
async def test_llm_manager():
    """Test the LLM manager with all providers"""
    manager = LLMManager()
    await manager.initialize()
    
    # Test generation with each model
    test_prompt = "Write a haiku about artificial intelligence"
    
    console.print("\n[bold]Testing all models:[/bold]")
    
    for model in manager.available_models:
        try:
            console.print(f"\n[yellow]Testing {model}:[/yellow]")
            response = await manager.generate(test_prompt, model=model)
            console.print(f"[green]Response:[/green] {response.content}")
            console.print(f"[blue]Tokens:[/blue] {response.usage}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
    
    # Test fallback
    console.print("\n[bold]Testing fallback mechanism:[/bold]")
    response = await manager.generate(
        "What is 2+2?",
        model="nonexistent",
        fallback=True
    )
    console.print(f"[green]Fallback response:[/green] {response.content}")
    console.print(f"[blue]Used model:[/blue] {response.model}")

if __name__ == "__main__":
    # Run test when module is executed directly
    asyncio.run(test_llm_manager()) 