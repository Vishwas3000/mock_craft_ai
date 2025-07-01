"""Validation script for LLM integration"""

import asyncio
import sys
import time
import argparse
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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Validate LLM integration for JSON Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_llm_integration.py                    # Test all providers
  python scripts/validate_llm_integration.py --openai           # Test only OpenAI
  python scripts/validate_llm_integration.py --ollama --openai  # Test OpenAI and Ollama
  python scripts/validate_llm_integration.py --local            # Test only local model
        """
    )
    
    parser.add_argument(
        "--openai", 
        action="store_true", 
        help="Test OpenAI integration"
    )
    parser.add_argument(
        "--ollama", 
        action="store_true", 
        help="Test Ollama integration"
    )
    parser.add_argument(
        "--local", 
        action="store_true", 
        help="Test local model integration"
    )
    parser.add_argument(
        "--manager", 
        action="store_true", 
        help="Test LLM Manager integration"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Test all providers (default if no flags specified)"
    )
    
    return parser.parse_args()

async def validate_llm_integration(providers_to_test=None):
    """Main validation function"""
    if providers_to_test is None:
        providers_to_test = ["openai", "ollama"]  # Default providers
    
    console.print(Panel.fit(
        f"[bold blue]LLM Integration Validation[/bold blue]\n"
        f"Testing: {', '.join(providers_to_test).upper()}",
        title="Week 1 Validation"
    ))
    
    results = {}
    
    # Initialize results for providers to test
    for provider in providers_to_test:
        results[provider] = {"status": "pending", "details": "", "latency": None}
    
    # Test each provider
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # OpenAI Test
        if "openai" in providers_to_test:
            task = progress.add_task("[cyan]Testing OpenAI connection...", total=1)
            results["openai"] = await test_openai()
            progress.update(task, completed=1)
        
        # Ollama Test
        if "ollama" in providers_to_test:
            task = progress.add_task("[cyan]Testing Ollama connection...", total=1)
            results["ollama"] = await test_ollama()
            progress.update(task, completed=1)
        
        # Local Model Test
        if "local" in providers_to_test:
            task = progress.add_task("[cyan]Testing Local Model...", total=1)
            results["local"] = await test_local_model()
            progress.update(task, completed=1)
    
    # Display results
    display_results(results)
    
    # Test LLM Manager if requested or if testing multiple providers
    manager_ok = True
    if "manager" in providers_to_test or len(providers_to_test) > 1:
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

async def test_local_model():
    """Test local model"""
    try:
        if not settings.llm.local_model_path:
            return {
                "status": "❌ Not Configured",
                "details": "LOCAL_MODEL_PATH not set in .env",
                "latency": None
            }
        
        model_path = Path(settings.llm.local_model_path)
        if not model_path.exists():
            return {
                "status": "❌ Model Not Found",
                "details": f"File not found: {model_path.name}",
                "latency": None
            }
        
        # LocalLLM is not implemented yet
        return {
            "status": "❌ Not Implemented",
            "details": "LocalLLM implementation pending",
            "latency": None
        }
        
    except Exception as e:
        return {
            "status": "❌ Failed",
            "details": str(e)[:50] + "...",
            "latency": None
        }

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
    args = parse_arguments()
    
    # Determine which providers to test
    providers_to_test = []
    
    if args.all or (not args.openai and not args.ollama and not args.local and not args.manager):
        # Default: test all available providers
        providers_to_test = ["openai", "ollama"]
    else:
        if args.openai:
            providers_to_test.append("openai")
        if args.ollama:
            providers_to_test.append("ollama")
        if args.local:
            providers_to_test.append("local")
        if args.manager:
            providers_to_test.append("manager")
    
    console.print(f"[dim]Testing providers: {', '.join(providers_to_test)}[/dim]\n")
    
    exit_code = asyncio.run(validate_llm_integration(providers_to_test))
    sys.exit(exit_code) 