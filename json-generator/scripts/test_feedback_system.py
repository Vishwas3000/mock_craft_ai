#!/usr/bin/env python3
"""
Feedback System Test and Demonstration Script

This script demonstrates the comprehensive feedback system integration with the
JSON generation pipeline. It shows how to use the feedback system for:

1. Automatic tracking and monitoring
2. Error detection and analysis
3. Performance monitoring
4. Recovery suggestions
5. Comprehensive reporting

Usage:
    python scripts/test_feedback_system.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import core components
from core.config import settings
from core.llm_manager import LLMManager
from core.schema_analyzer import SchemaAnalyzer
from core.generation_engine import JSONGenerationEngine, GenerationRequest
from core.prompt_engineer import PromptStrategy
from core.output_parser import ValidationLevel

# Import feedback system
from core.feedback_system import feedback_system
from core.feedback_integration import create_feedback_engine, feedback_tracking
from core.enhanced_test_decorators import comprehensive_test_tracking

console = Console()

class FeedbackSystemDemo:
    """Demonstration of the feedback system capabilities"""
    
    def __init__(self):
        self.config = settings
        self.llm_manager = LLMManager()
        self.generation_engine = JSONGenerationEngine(self.llm_manager)
        self.feedback_engine = create_feedback_engine(self.generation_engine)
        
        # Test schemas
        self.simple_schema = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30,
            "active": True
        }
        
        self.complex_schema = {
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "profile": {
                "personal_info": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "email": "jane.smith@example.com",
                    "phone": "+1-555-123-4567"
                },
                "preferences": {
                    "language": "en",
                    "timezone": "UTC",
                    "notifications": {
                        "email": True,
                        "sms": False,
                        "push": True
                    }
                }
            },
            "account": {
                "account_id": "acc_550e8400e29b41d4a716446655440002",
                "created_at": "2023-01-15T10:30:00Z",
                "billing": {
                    "plan": "pro",
                    "amount": 29.99,
                    "currency": "USD"
                }
            }
        }
    
    async def demonstrate_basic_tracking(self):
        """Demonstrate basic feedback tracking"""
        console.print(Panel(
            "[bold blue]Demonstration 1: Basic Feedback Tracking[/bold blue]\n"
            "This shows how the feedback system automatically tracks generation sessions,\n"
            "monitors performance, and provides detailed insights.",
            title="🔍 Basic Tracking Demo"
        ))
        
        # Create a simple generation request
        request = GenerationRequest(
            schema=self.simple_schema,
            count=3,
            context="Basic tracking demonstration",
            strategy=PromptStrategy.STRUCTURED,
            validation_level=ValidationLevel.LENIENT
        )
        
        try:
            # Generate with feedback tracking
            result = await self.feedback_engine.generate_with_feedback(
                request, 
                "basic_tracking_demo"
            )
            
            console.print(f"[green]✅ Generation successful: {result.success}[/green]")
            if result.validation_result:
                console.print(f"[yellow]Validation score: {result.validation_result.score:.2f}[/yellow]")
            
        except Exception as e:
            console.print(f"[red]❌ Generation failed: {str(e)}[/red]")
    
    async def demonstrate_error_handling(self):
        """Demonstrate error detection and recovery suggestions"""
        console.print(Panel(
            "[bold blue]Demonstration 2: Error Detection & Recovery[/bold blue]\n"
            "This shows how the feedback system detects errors, categorizes them,\n"
            "and provides intelligent recovery suggestions.",
            title="🛠️ Error Handling Demo"
        ))
        
        # Create a request that might cause issues
        problematic_request = GenerationRequest(
            schema={"invalid_field": None},  # This might cause issues
            count=50,  # Large count to potentially cause timeout
            context="Error handling demonstration",
            strategy=PromptStrategy.ZERO_SHOT,
            validation_level=ValidationLevel.STRICT
        )
        
        try:
            result = await self.feedback_engine.generate_with_feedback(
                problematic_request,
                "error_handling_demo"
            )
            console.print(f"[green]✅ Unexpectedly successful: {result.success}[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Expected error occurred: {str(e)}[/yellow]")
            console.print("[cyan]The feedback system has recorded this error and provided recovery suggestions.[/cyan]")
    
    async def demonstrate_performance_monitoring(self):
        """Demonstrate performance monitoring"""
        console.print(Panel(
            "[bold blue]Demonstration 3: Performance Monitoring[/bold blue]\n"
            "This shows how the feedback system monitors performance metrics,\n"
            "tracks trends, and identifies optimization opportunities.",
            title="📊 Performance Monitoring Demo"
        ))
        
        # Test different record counts for performance analysis
        record_counts = [1, 3, 5]
        
        for count in record_counts:
            console.print(f"[yellow]Testing with {count} records...[/yellow]")
            
            request = GenerationRequest(
                schema=self.simple_schema,
                count=count,
                context=f"Performance test with {count} records",
                strategy=PromptStrategy.STRUCTURED,
                validation_level=ValidationLevel.LENIENT
            )
            
            start_time = time.time()
            try:
                result = await self.feedback_engine.generate_with_feedback(
                    request,
                    f"performance_test_{count}_records"
                )
                execution_time = time.time() - start_time
                
                console.print(f"[green]✅ {count} records: {execution_time:.2f}s "
                            f"({count/execution_time:.2f} records/sec)[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ {count} records failed: {str(e)}[/red]")
    
    async def demonstrate_validation_tracking(self):
        """Demonstrate validation tracking"""
        console.print(Panel(
            "[bold blue]Demonstration 4: Validation Tracking[/bold blue]\n"
            "This shows how the feedback system tracks validation results,\n"
            "identifies patterns in validation failures, and suggests improvements.",
            title="🔬 Validation Tracking Demo"
        ))
        
        # Test with different validation levels
        validation_levels = [
            ValidationLevel.LENIENT,
            ValidationLevel.STANDARD,
            ValidationLevel.STRICT
        ]
        
        for level in validation_levels:
            console.print(f"[yellow]Testing with {level.value} validation...[/yellow]")
            
            request = GenerationRequest(
                schema=self.complex_schema,
                count=2,
                context=f"Validation test with {level.value} level",
                strategy=PromptStrategy.CHAIN_OF_THOUGHT,
                validation_level=level
            )
            
            try:
                result = await self.feedback_engine.generate_with_feedback(
                    request,
                    f"validation_test_{level.value}"
                )
                
                score = result.validation_result.score if result.validation_result else 0.0
                console.print(f"[green]✅ {level.value}: Score {score:.2f}[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ {level.value} failed: {str(e)}[/red]")
    
    @comprehensive_test_tracking("comprehensive_demo")
    async def demonstrate_comprehensive_analysis(self):
        """Demonstrate comprehensive analysis with decorators"""
        console.print(Panel(
            "[bold blue]Demonstration 5: Comprehensive Analysis[/bold blue]\n"
            "This shows how the feedback system provides comprehensive analysis\n"
            "using decorators for automatic tracking and reporting.",
            title="🎯 Comprehensive Analysis Demo"
        ))
        
        # This function is decorated with comprehensive tracking
        # The decorator will automatically handle session management
        
        # Test multiple strategies
        strategies = [
            PromptStrategy.STRUCTURED,
            PromptStrategy.CHAIN_OF_THOUGHT,
            PromptStrategy.FEW_SHOT
        ]
        
        results = {}
        
        for strategy in strategies:
            console.print(f"[yellow]Testing strategy: {strategy.value}[/yellow]")
            
            request = GenerationRequest(
                schema=self.simple_schema,
                count=2,
                context=f"Comprehensive analysis with {strategy.value}",
                strategy=strategy,
                validation_level=ValidationLevel.LENIENT
            )
            
            try:
                # Use the original engine for this demo
                result = await self.generation_engine.generate(request)
                
                results[strategy.value] = {
                    'success': result.success,
                    'validation_score': result.validation_result.score if result.validation_result else 0.0
                }
                
                console.print(f"[green]✅ {strategy.value}: "
                            f"Success={result.success}, "
                            f"Score={results[strategy.value]['validation_score']:.2f}[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ {strategy.value} failed: {str(e)}[/red]")
                results[strategy.value] = {'success': False, 'error': str(e)}
        
        return results
    
    def demonstrate_context_manager(self):
        """Demonstrate context manager usage"""
        console.print(Panel(
            "[bold blue]Demonstration 6: Context Manager Usage[/bold blue]\n"
            "This shows how to use the feedback system with context managers\n"
            "for fine-grained control over tracking sessions.",
            title="🎛️ Context Manager Demo"
        ))
        
        # Use the feedback tracking context manager
        with feedback_tracking("context_manager_demo", self.simple_schema, "Context manager test"):
            console.print("[cyan]Inside feedback tracking context...[/cyan]")
            time.sleep(1)  # Simulate some work
            console.print("[green]✅ Context manager demo completed[/green]")
    
    async def run_all_demonstrations(self):
        """Run all demonstrations"""
        console.print(Panel(
            "[bold green]🚀 Feedback System Comprehensive Demonstration[/bold green]\n"
            "This script will demonstrate all the key features of the feedback system:\n"
            "• Basic tracking and monitoring\n"
            "• Error detection and recovery\n"
            "• Performance monitoring\n"
            "• Validation tracking\n"
            "• Comprehensive analysis\n"
            "• Context manager usage\n"
            "• System dashboard and reporting",
            title="Feedback System Demo"
        ))
        
        demonstrations = [
            ("Basic Tracking", self.demonstrate_basic_tracking),
            ("Error Handling", self.demonstrate_error_handling),
            ("Performance Monitoring", self.demonstrate_performance_monitoring),
            ("Validation Tracking", self.demonstrate_validation_tracking),
            ("Comprehensive Analysis", self.demonstrate_comprehensive_analysis),
            ("Context Manager", lambda: self.demonstrate_context_manager())
        ]
        
        for name, demo_func in demonstrations:
            console.print(f"\n[bold blue]Running: {name}[/bold blue]")
            try:
                if asyncio.iscoroutinefunction(demo_func):
                    await demo_func()
                else:
                    demo_func()
                console.print(f"[green]✅ {name} completed successfully[/green]")
            except Exception as e:
                console.print(f"[red]❌ {name} failed: {str(e)}[/red]")
            
            # Small delay between demonstrations
            await asyncio.sleep(1)
        
        # Display final system dashboard
        console.print(Panel(
            "[bold green]📊 Final System Dashboard[/bold green]\n"
            "The feedback system has been tracking all activities.\n"
            "Here's the comprehensive system health report:",
            title="System Dashboard"
        ))
        
        feedback_system.display_system_dashboard()
        
        # Show system health
        health = feedback_system.get_system_health()
        console.print(f"\n[bold green]System Health Summary:[/bold green]")
        console.print(f"[green]Total Sessions: {health['global_metrics']['total_sessions']}[/green]")
        console.print(f"[green]Success Rate: {health['global_metrics']['success_rate']:.1%}[/green]")
        console.print(f"[green]Total Errors: {health['global_metrics']['total_errors']}[/green]")
        console.print(f"[green]Health Status: {health['health_status'].title()}[/green]")

async def main():
    """Main function to run the feedback system demonstration"""
    console.print("[bold blue]🎉 Starting Feedback System Demonstration[/bold blue]")
    
    try:
        demo = FeedbackSystemDemo()
        await demo.run_all_demonstrations()
        
        console.print("\n[bold green]🎉 Feedback System Demonstration Complete![/bold green]")
        console.print("[cyan]Check the 'outputs/feedback' directory for detailed session reports.[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Demo failed: {str(e)}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")

if __name__ == "__main__":
    asyncio.run(main()) 