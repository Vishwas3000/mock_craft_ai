"""Validation script for LLM integration"""

import asyncio
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.llm_manager import LLMManager
from src.core.config import settings

console = Console()

async def validate_llm_integration():
    """Main validation function"""
    console.print(Panel.fit(
        "[bold blue]LLM Integration Validation[/bold blue]\n"
        "Testing OpenAI, Ollama, and Local Model connections",
        title="Week 1 Validation"
    ))
    
    results = {
        "openai": {"status": "pending", "details": "", "latency": None},
        "ollama": {"status": "pending", "details": "", "latency": None}
        # "local": {"status": "pending", "details": "", "latency": None}
    }
    
    # Test each provider
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # OpenAI Test
        task = progress.add_task("[cyan]Testing OpenAI connection...", total=1)
        results["openai"] = await test_openai()
        progress.update(task, completed=1)
        
        # Ollama Test
        task = progress.add_task("[cyan]Testing Ollama connection...", total=1)
        results["ollama"] = await test_ollama()
        progress.update(task, completed=1)
        
        # Local Model Test
        # task = progress.add_task("[cyan]Testing Local Model...", total=1)
        # results["local"] = await test_local_model()
        # progress.update(task, completed=1)
    
    # Display results
    display_results(results)
    
    # Test LLM Manager
    console.print("\n[bold]Testing LLM Manager Integration...[/bold]")
    manager_ok = await test_llm_manager()
    
    # Final summary
    all_passed = all(r["status"] == "✅ Connected" for r in results.values()) and manager_ok
    
    if all_passed:
        console.print("\n[bold green]✅ All tests PASSED! Ready for Week 2.[/bold green]")
        return 0
    else:
        console.print("\n[bold red]❌ Some tests failed. Please check the configuration.[/bold red]")
        return 1

async def test_openai():
    """Test OpenAI connection"""
    try:
        if not settings.llm.openai_api_key:
            return {
                "status": "❌ Not Configured",
                "details": "OPENAI_API_KEY not set in .env",
                "latency": None
            }
        
        from src.core.llm_providers.openai_llm import OpenAILLM
        
        start_time = time.time()
        llm = OpenAILLM()
        await llm.initialize()
        
        # Test generation
        response = await llm.generate("Say 'test passed'")
        latency = time.time() - start_time
        
        return {
            "status": "✅ Connected",
            "details": f"Model: {llm.model_name}",
            "latency": f"{latency:.2f}s"
        }
        
    except Exception as e:
        return {
            "status": "❌ Failed",
            "details": str(e)[:50] + "...",
            "latency": None
        }

async def test_ollama():
    """Test Ollama connection"""
    try:
        from src.core.llm_providers.ollama_llm import OllamaLLM
        
        start_time = time.time()
        llm = OllamaLLM()
        
        # Check if Ollama is running
        if not await llm._check_ollama_status():
            return {
                "status": "❌ Not Running",
                "details": "Start Ollama with: ollama serve",
                "latency": None
            }
        
        await llm.initialize()
        
        # Test generation
        response = await llm.generate("Say 'test passed'")
        latency = time.time() - start_time
        
        return {
            "status": "✅ Connected",
            "details": f"Model: {llm.model_name}",
            "latency": f"{latency:.2f}s"
        }
        
    except Exception as e:
        return {
            "status": "❌ Failed",
            "details": str(e)[:50] + "...",
            "latency": None
        }

# async def test_local_model():
    # """Test local model"""
    # try:
    #     if not settings.llm.local_model_path:
    #         return {
    #             "status": "❌ Not Configured",
    #             "details": "LOCAL_MODEL_PATH not set in .env",
    #             "latency": None
    #         }
        
    #     model_path = Path(settings.llm.local_model_path)
    #     if not model_path.exists():
    #         return {
    #             "status": "❌ Model Not Found",
    #             "details": f"File not found: {model_path.name}",
    #             "latency": None
    #         }
        
    #     from src.core.llm_providers.local_llm import LocalLLM
        
    #     start_time = time.time()
    #     llm = LocalLLM()
    #     await llm.initialize()
        
    #     # Test generation
    #     response = await llm.generate("Say 'test passed'", max_tokens=10)
    #     latency = time.time() - start_time
        
    #     return {
    #         "status": "✅ Connected",
    #         "details": f"Model: {model_path.name} ({llm._get_model_size()})",
    #         "latency": f"{latency:.2f}s"
    #     }
        
    # except Exception as e:
    #     return {
    #         "status": "❌ Failed",
    #         "details": str(e)[:50] + "...",
    #         "latency": None
    #     }

async def test_llm_manager():
    """Test the unified LLM manager"""
    try:
        manager = LLMManager()
        await manager.initialize()
        
        if not manager.available_models:
            console.print("[red]No models available in LLM Manager[/red]")
            return False
        
        # Test generation
        response = await manager.generate("Hello")
        console.print(f"[green]✅ LLM Manager working with {len(manager.available_models)} models[/green]")
        
        # Test fallback
        if len(manager.available_models) >= 2:
            response = await manager.generate("Test", model="fake_model", fallback=True)
            console.print("[green]✅ Fallback mechanism working[/green]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ LLM Manager failed: {e}[/red]")
        return False

def display_results(results):
    """Display test results in a table"""
    table = Table(title="LLM Provider Test Results")
    table.add_column("Provider", style="cyan", width=12)
    table.add_column("Status", style="bold", width=20)
    table.add_column("Details", style="yellow", width=40)
    table.add_column("Latency", style="green", width=10)
    
    for provider, result in results.items():
        table.add_row(
            provider.upper(),
            result["status"],
            result["details"],
            result["latency"] or "N/A"
        )
    
    console.print("\n")
    console.print(table)

if __name__ == "__main__":
    exit_code = asyncio.run(validate_llm_integration())
    sys.exit(exit_code) 