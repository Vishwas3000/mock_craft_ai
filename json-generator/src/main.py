"""Main entry point for the JSON Generator"""

import asyncio
from rich.console import Console
from core.llm_manager import LLMManager

console = Console()

async def main():
    """Main application entry point"""
    console.print("[bold blue]JSON Generator - Week 1 Development[/bold blue]\n")
    
    # Initialize LLM Manager
    manager = LLMManager()
    await manager.initialize()
    
    # Example usage
    prompt = "Generate a simple JSON object with a greeting message"
    response = await manager.generate(prompt)
    
    console.print("[green]Generated response:[/green]")
    console.print(response.content)
    
    # Try JSON generation
    json_response = await manager.generate_json(
        "Create a user profile with name, email, and preferences"
    )
    
    console.print("\n[green]Generated JSON:[/green]")
    console.print_json(data=json_response)

if __name__ == "__main__":
    asyncio.run(main()) 