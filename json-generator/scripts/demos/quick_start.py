"""Quick start script to test the LLM integration"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.llm_manager import LLMManager

console = Console()

async def interactive_demo():
    """Run an interactive demo of the LLM system"""
    console.print("[bold blue]JSON Generator - LLM Integration Demo[/bold blue]\n")
    
    # Initialize LLM Manager
    console.print("Initializing LLM Manager...")
    manager = LLMManager()
    
    try:
        await manager.initialize()
    except Exception as e:
        console.print(f"[red]Failed to initialize: {e}[/red]")
        return
    
    console.print(f"\n[green]Available models:[/green] {', '.join(manager.available_models)}")
    
    while True:
        console.print("\n" + "="*50 + "\n")
        
        # Get user input
        prompt = Prompt.ask("[cyan]Enter a prompt (or 'quit' to exit)[/cyan]")
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            break
        
        # Model selection
        if len(manager.available_models) > 1:
            console.print(f"\nAvailable models: {manager.available_models}")
            model = Prompt.ask(
                "Which model to use?",
                choices=manager.available_models + ["auto"],
                default="auto"
            )
            
            if model == "auto":
                model = None
        else:
            model = None
        
        # Generate response
        try:
            console.print("\n[yellow]Generating response...[/yellow]")
            response = await manager.generate(prompt, model=model)
            
            console.print(f"\n[green]Response ({response.model}):[/green]")
            console.print(response.content)
            
            if response.usage:
                console.print(f"\n[dim]Tokens used: {response.usage}[/dim]")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        # Ask if user wants to test JSON generation
        if Confirm.ask("\nTest JSON generation?", default=False):
            json_prompt = Prompt.ask("Enter JSON generation prompt")
            
            try:
                json_response = await manager.generate_json(json_prompt)
                console.print("\n[green]Generated JSON:[/green]")
                console.print_json(data=json_response)
            except Exception as e:
                console.print(f"[red]JSON generation error: {e}[/red]")
    
    console.print("\n[bold green]Thanks for testing![/bold green]")

async def run_examples():
    """Run example generations"""
    console.print("[bold]Running example generations...[/bold]\n")
    
    manager = LLMManager()
    await manager.initialize()
    
    examples = [
        {
            "name": "Simple JSON",
            "prompt": "Generate a JSON object with user information including name, age, and email"
        },
        {
            "name": "Array Generation",
            "prompt": "Generate a JSON array of 3 products with name, price, and category"
        },
        {
            "name": "Nested Structure",
            "prompt": "Generate a JSON object representing a company with departments and employees"
        }
    ]
    
    for example in examples:
        console.print(f"\n[cyan]Example: {example['name']}[/cyan]")
        console.print(f"Prompt: {example['prompt']}")
        
        try:
            response = await manager.generate_json(example['prompt'])
            console.print("[green]Generated:[/green]")
            console.print_json(data=response)
        except Exception as e:
            console.print(f"[red]Failed: {e}[/red]")

async def main():
    """Main entry point"""
    console.print("""
[bold blue]Week 1: LLM Integration Demo[/bold blue]

This script demonstrates the multi-LLM integration with:
- OpenAI API
- Ollama (local server)  
- Local GGUF models

Choose an option:
1. Interactive Demo
2. Run Examples
3. Exit
""")
    
    choice = Prompt.ask("Select option", choices=["1", "2", "3"], default="1")
    
    if choice == "1":
        await interactive_demo()
    elif choice == "2":
        await run_examples()
    else:
        console.print("Goodbye!")

if __name__ == "__main__":
    asyncio.run(main()) 