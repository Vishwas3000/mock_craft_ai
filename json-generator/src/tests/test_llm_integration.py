"""Test suite for Week 1: LLM Integration"""

import pytest
import asyncio
import os
from pathlib import Path

from src.core.llm_manager import LLMManager, ModelPriority
from src.core.base_llm import GenerationConfig
from src.core.config import settings

# Test fixtures
@pytest.fixture
async def llm_manager():
    """Create and initialize LLM manager"""
    manager = LLMManager()
    await manager.initialize()
    return manager

# Basic connection tests
class TestLLMConnections:
    """Test basic connections to each LLM provider"""
    
    @pytest.mark.asyncio
    async def test_openai_connection(self):
        """Test OpenAI connection"""
        if not settings.llm.openai_api_key:
            pytest.skip("OpenAI API key not configured")
        
        from src.core.llm_providers.openai_llm import OpenAILLM
        llm = OpenAILLM()
        await llm.initialize()
        
        assert llm._is_initialized
        assert await llm.test_connection()
    
    @pytest.mark.asyncio
    async def test_ollama_connection(self):
        """Test Ollama connection"""
        from src.core.llm_providers.ollama_llm import OllamaLLM
        
        try:
            llm = OllamaLLM()
            await llm.initialize()
            assert llm._is_initialized
        except Exception as e:
            if "not running" in str(e):
                pytest.skip("Ollama not running")
            raise
    
    @pytest.mark.asyncio
    async def test_local_model_connection(self):
        """Test local model connection"""
        if not settings.llm.local_model_path:
            pytest.skip("Local model path not configured")
        
        # from src.core.llm_providers.local_llm import LocalLLM
        
        try:
            # llm = LocalLLM()
            # await llm.initialize()
            assert False  # This should never be reached if LocalLLM is not imported
        except Exception as e:
            if "not found" in str(e):
                pytest.skip("Local model file not found")
            raise

# Generation tests
class TestGeneration:
    """Test generation capabilities"""
    
    @pytest.mark.asyncio
    async def test_basic_generation(self, llm_manager):
        """Test basic text generation"""
        prompt = "Say 'Hello, World!' and nothing else."
        response = await llm_manager.generate(prompt)
        
        assert response.content
        assert "hello" in response.content.lower()
        assert response.model
        assert response.provider
    
    @pytest.mark.asyncio
    async def test_json_generation(self, llm_manager):
        """Test JSON generation"""
        prompt = "Generate a simple user object with name and age"
        response = await llm_manager.generate_json(prompt)
        
        assert isinstance(response, dict)
        # Check if it has expected fields (may vary by model)
        assert any(key in str(response).lower() for key in ['name', 'user', 'age'])
    
    @pytest.mark.asyncio
    async def test_generation_with_config(self, llm_manager):
        """Test generation with custom config"""
        config = GenerationConfig(
            temperature=0.1,
            max_tokens=50,
            stop_sequences=["\n"]
        )
        
        prompt = "Count from 1 to 5"
        response = await llm_manager.generate(prompt, config=config)
        
        assert response.content
        assert len(response.content) < 200  # Should be limited by max_tokens
    
    @pytest.mark.asyncio
    async def test_streaming_generation(self, llm_manager):
        """Test streaming generation"""
        if not llm_manager.available_models:
            pytest.skip("No models available")
        
        model = llm_manager.available_models[0]
        llm = llm_manager.models[model]
        
        prompt = "Count from 1 to 3"
        chunks = []
        
        async for chunk in llm.generate_stream(prompt):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert any(num in full_response for num in ["1", "2", "3"])

# Fallback tests
class TestFallback:
    """Test fallback mechanisms"""
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, llm_manager):
        """Test fallback to another model"""
        if len(llm_manager.available_models) < 2:
            pytest.skip("Need at least 2 models for fallback test")
        
        # Force an error by using wrong model name
        response = await llm_manager.generate(
            "Hello",
            model="nonexistent_model",
            fallback=True
        )
        
        assert response.content
        assert response.metadata.get("fallback_used") == True
    
    @pytest.mark.asyncio
    async def test_model_priority_selection(self, llm_manager):
        """Test model selection by priority"""
        for priority in ModelPriority:
            model = llm_manager.select_model_by_priority(priority)
            assert model in llm_manager.available_models

# Performance tests
class TestPerformance:
    """Test performance and benchmarking"""
    
    @pytest.mark.asyncio
    async def test_benchmark_models(self, llm_manager):
        """Benchmark all available models"""
        results = await llm_manager.benchmark_models()
        
        assert len(results) > 0
        
        for model, metrics in results.items():
            if metrics["success"]:
                assert "latency" in metrics
                assert metrics["latency"] > 0
                assert "response_length" in metrics
    
    @pytest.mark.asyncio
    async def test_concurrent_generation(self, llm_manager):
        """Test concurrent generation requests"""
        prompts = [
            "What is 1+1?",
            "What is 2+2?",
            "What is 3+3?"
        ]
        
        tasks = [llm_manager.generate(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 3
        for response in responses:
            assert response.content

# Integration tests
class TestIntegration:
    """Full integration tests"""
    
    @pytest.mark.asyncio
    async def test_multi_model_generation(self, llm_manager):
        """Test generation with all available models"""
        prompt = "Write the word 'success'"
        
        for model in llm_manager.available_models:
            response = await llm_manager.generate(prompt, model=model)
            assert response.content
            assert "success" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, llm_manager):
        """Test error handling"""
        # Test with empty prompt
        with pytest.raises(Exception):
            await llm_manager.generate("")
        
        # Test with invalid model
        with pytest.raises(ValueError):
            await llm_manager.generate("test", model="invalid_model", fallback=False)

# Validation script
def run_validation():
    """Run validation script for Week 1"""
    import sys
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    console.print("[bold blue]Week 1 Validation: LLM Integration[/bold blue]\n")
    
    # Run tests
    test_results = {}
    
    async def validate():
        manager = LLMManager()
        
        # Test 1: Initialization
        try:
            await manager.initialize()
            test_results["Initialization"] = ("✅ Pass", "All providers initialized")
        except Exception as e:
            test_results["Initialization"] = ("❌ Fail", str(e))
        
        # Test 2: Model availability
        if manager.available_models:
            test_results["Models Available"] = (
                "✅ Pass", 
                f"Found {len(manager.available_models)} models: {', '.join(manager.available_models)}"
            )
        else:
            test_results["Models Available"] = ("❌ Fail", "No models available")
        
        # Test 3: Generation test
        if manager.available_models:
            try:
                response = await manager.generate("Hello")
                test_results["Basic Generation"] = ("✅ Pass", f"Generated {len(response.content)} chars")
            except Exception as e:
                test_results["Basic Generation"] = ("❌ Fail", str(e))
        
        # Test 4: JSON generation
        if manager.available_models:
            try:
                json_response = await manager.generate_json("Generate a simple object")
                test_results["JSON Generation"] = ("✅ Pass", "JSON generated successfully")
            except Exception as e:
                test_results["JSON Generation"] = ("⚠️  Partial", "JSON mode not fully supported")
        
        # Test 5: Fallback
        if len(manager.available_models) >= 2:
            try:
                response = await manager.generate("Test", model="fake", fallback=True)
                test_results["Fallback System"] = ("✅ Pass", "Fallback working")
            except:
                test_results["Fallback System"] = ("❌ Fail", "Fallback not working")
        else:
            test_results["Fallback System"] = ("⚠️  Skip", "Need 2+ models for fallback")
        
        # Test 6: Performance
        try:
            benchmark = await manager.benchmark_models()
            avg_latency = sum(r["latency"] for r in benchmark.values() if r.get("success", False)) / len(benchmark)
            test_results["Performance"] = ("✅ Pass", f"Avg latency: {avg_latency:.2f}s")
        except:
            test_results["Performance"] = ("⚠️  Partial", "Benchmark incomplete")
        
        return manager
    
    # Run validation
    manager = asyncio.run(validate())
    
    # Display results
    table = Table(title="Validation Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="yellow")
    
    for test, (status, details) in test_results.items():
        table.add_row(test, status, details)
    
    console.print(table)
    
    # Summary
    passed = sum(1 for _, (status, _) in test_results.items() if "✅" in status)
    total = len(test_results)
    
    console.print(f"\n[bold]Summary:[/bold] {passed}/{total} tests passed")
    
    if passed == total:
        console.print("[bold green]✅ Week 1 validation PASSED![/bold green]")
        return 0
    else:
        console.print("[bold red]❌ Week 1 validation needs attention[/bold red]")
        return 1

if __name__ == "__main__":
    sys.exit(run_validation()) 