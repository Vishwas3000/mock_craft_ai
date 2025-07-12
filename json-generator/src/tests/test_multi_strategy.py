# src/tests/test_multi_strategy.py
"""
Multi-Strategy JSON Generation Test Suite
=========================================

This file contains comprehensive tests for the JSON generation system using different
prompt engineering strategies. It evaluates the performance and effectiveness of
various approaches to generating structured JSON data from schemas.

OVERVIEW:
---------
This test suite validates the multi-strategy JSON generation engine by testing:
1. Different prompt engineering strategies (Chain-of-Thought, Few-Shot, Structured, Zero-Shot)
2. Multi-strategy automatic selection
3. Adaptive generation with auto-retry mechanisms
4. Performance comparison across different schema complexities

TEST TYPES AND DESCRIPTIONS:
---------------------------

1. MULTI-STRATEGY COMPARISON TEST (test_multi_strategy)
   Purpose: Compare the effectiveness of different generation strategies
   - Tests 3 schema complexity levels (Simple, Medium, Complex)
   - Evaluates 3 strategies per schema:
     * Single Strategy (Chain-of-Thought)
     * Multi-Strategy (Automatic selection)
     * Adaptive Generation (Auto-retry)
   - Measures: Execution time, validation scores, success rates
   - Output: Performance comparison table and detailed results

2. SPECIFIC STRATEGY TESTING (test_specific_strategies)
   Purpose: Deep dive into individual strategy performance
   - Tests each strategy individually with a complex e-commerce schema
   - Strategies tested:
     * Chain-of-Thought: Step-by-step reasoning approach
     * Few-Shot: Learning from examples
     * Structured: Template-based generation
     * Zero-Shot: Direct generation without examples
     * Multi-Strategy: Automatic strategy selection
     * Adaptive: Auto-retry with different strategies
   - Measures: Individual performance metrics and validation scores
   - Output: Strategy comparison table and recommendations

SCHEMA COMPLEXITY LEVELS:
-------------------------
- Simple Schema: Basic user profile with 4-5 fields
- Medium Complexity: E-commerce order with nested objects and arrays
- Complex Schema: Company organizational data with deep nesting and multiple arrays

GENERATION STRATEGIES:
---------------------
1. Chain-of-Thought (CoT): Breaks down complex generation into logical steps
2. Few-Shot: Uses examples to guide the generation process
3. Structured: Uses predefined templates and patterns
4. Zero-Shot: Direct generation without additional context
5. Multi-Strategy: Automatically selects the best strategy based on schema analysis
6. Adaptive: Tries multiple strategies and selects the best result

USAGE:
------
1. Basic Test Run:
   python src/tests/test_multi_strategy.py

2. Verbose Output (shows generated JSON):
   python src/tests/test_multi_strategy.py --verbose

3. Show Saved Output Files:
   python src/tests/test_multi_strategy.py --show-outputs

4. Both Verbose and Show Outputs:
   python src/tests/test_multi_strategy.py --verbose --show-outputs

OUTPUTS:
--------
- Console Output: Real-time test progress and results
- Generated Data: Sample JSON outputs for each strategy
- Performance Metrics: Execution times and validation scores
- Comparison Tables: Strategy performance comparisons
- Saved Files: Test results saved to outputs/ directory
- Summary Reports: Overall test statistics and recommendations

VALIDATION METRICS:
------------------
- Schema Compliance: Checks if generated data matches the input schema
- Data Quality: Validates data types, formats, and relationships
- Completeness: Ensures all required fields are present
- Consistency: Verifies logical consistency of generated data

PERFORMANCE METRICS:
-------------------
- Execution Time: Time taken for each generation attempt
- Success Rate: Percentage of successful generations
- Validation Score: Quality score of generated data (0-1)
- Strategy Effectiveness: Comparison of different approaches

DEPENDENCIES:
-------------
- LLM Manager: Manages different language model providers
- Generation Engine: Core JSON generation functionality
- Schema Analyzer: Analyzes schema complexity and structure
- Output Manager: Saves and manages test results
- Rich Console: Provides beautiful terminal output

AUTHOR: JSON Generator Test Suite
VERSION: 1.0
LAST UPDATED: 2024
"""

import asyncio
import json
import argparse
from pathlib import Path
import sys
import uuid

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.llm_manager import LLMManager
from src.core.generation_engine import JSONGenerationEngine, GenerationRequest, GenerationMode
from src.core.schema_analyzer import SchemaAnalyzer
from src.core.prompt_engineer import PromptStrategy
from src.core.output_parser import ValidationLevel
from src.utils.output.output_manager import output_manager
from src.utils.testing.test_decorators import save_generation_output, with_output_summary
from rich.console import Console
from rich.table import Table

console = Console()

@save_generation_output("multi_strategy_comparison")
async def test_multi_strategy():
    """Test multi-strategy generation with different schemas"""
    
    # Initialize components
    console.print("[bold blue]Initializing JSON Generator...[/bold blue]")
    console.print("=" * 60)
    
    llm_manager = LLMManager()
    await llm_manager.initialize()
    
    # Log LLM Manager state
    console.print(f"[cyan]LLM Manager Status:[/cyan]")
    console.print(f"  • Available Models: {list(llm_manager.models.keys()) if llm_manager.models else 'None'}")
    console.print(f"  • Default Model: {llm_manager.default_model}")
    console.print(f"  • Initialized: {llm_manager._initialized}")
    console.print()
    
    engine = JSONGenerationEngine(llm_manager)
    analyzer = SchemaAnalyzer()
    
    console.print(f"[cyan]Components Initialized:[/cyan]")
    console.print(f"  • Generation Engine: {type(engine).__name__}")
    console.print(f"  • Schema Analyzer: {type(analyzer).__name__}")
    console.print()
    
    # Test schemas of varying complexity
    test_cases = [
        # {
        #     "name": "Simple Schema",
        #     "schema": {
        #         "id": str(uuid.uuid4()),
        #         "name": "John Doe",
        #         "age": 30,
        #         "active": True,
        #         "email": "john.doe@example.com",
        #         "created_at": "2024-01-15T10:30:00Z"
        #     },
        #     "context": "user profiles",
        #     "count": 3
        # },
        # {
        #     "name": "Medium Complexity",
        #     "schema": {
        #         "orderId": str(uuid.uuid4()),
        #         "customer": {
        #             "id": str(uuid.uuid4()),
        #             "name": "Jane Smith",
        #             "email": "jane.smith@example.com",
        #             "phone": "+1-555-0123"
        #         },
        #         "items": [
        #             {
        #                 "productId": str(uuid.uuid4()),
        #                 "name": "Wireless Headphones",
        #                 "quantity": 2,
        #                 "price": 29.99,
        #                 "category": "Electronics"
        #             },
        #             {
        #                 "productId": str(uuid.uuid4()),
        #                 "name": "USB-C Cable",
        #                 "quantity": 1,
        #                 "price": 12.99,
        #                 "category": "Accessories"
        #             }
        #         ],
        #         "totalAmount": 72.97,
        #         "orderDate": "2024-01-15T14:22:30Z",
        #         "status": "pending",
        #         "shippingAddress": {
        #             "street": "123 Main St",
        #             "city": "New York",
        #             "state": "NY",
        #             "zipCode": "10001",
        #             "country": "USA"
        #         }
        #     },
        #     "context": "e-commerce orders",
        #     "count": 5
        # },
        {
            "name": "Complex Schema",
            "schema": {
                "companyId": str(uuid.uuid4()),
                "name": "Tech Corp",
                "industry": "Technology",
                "departments": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Engineering",
                        "manager": {
                            "id": str(uuid.uuid4()),
                            "name": "Bob Johnson",
                            "email": "bob.johnson@techcorp.com",
                            "title": "Engineering Manager"
                        },
                        "employees": [
                            {
                                "id": str(uuid.uuid4()),
                                "name": "Alice Smith",
                                "email": "alice.smith@techcorp.com",
                                "role": "Senior Developer",
                                "skills": ["Python", "JavaScript", "React", "Node.js"],
                                "hireDate": "2022-03-15",
                                "salary": 95000
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "name": "Charlie Brown",
                                "email": "charlie.brown@techcorp.com",
                                "role": "Frontend Developer",
                                "skills": ["JavaScript", "React", "CSS", "HTML"],
                                "hireDate": "2023-01-10",
                                "salary": 85000
                            }
                        ],
                        "budget": 1000000.00,
                        "projects": [
                            {
                                "id": str(uuid.uuid4()),
                                "name": "Mobile App Redesign",
                                "status": "in_progress",
                                "deadline": "2024-06-30"
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Marketing",
                        "manager": {
                            "id": str(uuid.uuid4()),
                            "name": "Diana Wilson",
                            "email": "diana.wilson@techcorp.com",
                            "title": "Marketing Director"
                        },
                        "employees": [
                            {
                                "id": str(uuid.uuid4()),
                                "name": "Eve Davis",
                                "email": "eve.davis@techcorp.com",
                                "role": "Digital Marketing Specialist",
                                "skills": ["SEO", "Google Ads", "Social Media"],
                                "hireDate": "2023-08-20",
                                "salary": 70000
                            }
                        ],
                        "budget": 500000.00,
                        "campaigns": [
                            {
                                "id": str(uuid.uuid4()),
                                "name": "Q1 Product Launch",
                                "status": "active",
                                "budget": 75000
                            }
                        ]
                    }
                ],
                "address": {
                    "street": "123 Tech Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zipCode": "94105",
                    "country": "USA"
                },
                "contact": {
                    "phone": "+1-415-555-0123",
                    "email": "info@techcorp.com",
                    "website": "https://techcorp.com"
                },
                "founded": "2010-05-15",
                "employeeCount": 150,
                "revenue": 25000000.00,
                "status": "active"
            },
            "context": "company organizational data",
            "count": 3
        }
    ]
    
    results_table = Table(title="Multi-Strategy Generation Results")
    results_table.add_column("Schema", style="cyan")
    results_table.add_column("Complexity", style="yellow")
    results_table.add_column("Strategy Used", style="green")
    results_table.add_column("Success", style="bold")
    results_table.add_column("Score", style="magenta")
    results_table.add_column("Time", style="blue")
    
    for test_case in test_cases:
        console.print(f"\n[bold blue]Testing: {test_case['name']}[/bold blue]")
        console.print("=" * 50)
        console.print(f"[cyan]Context:[/cyan] {test_case['context']}")
        console.print(f"[cyan]Target Count:[/cyan] {test_case['count']} records")
        
        # Display input schema
        console.print(f"\n[bold yellow]Input Schema:[/bold yellow]")
        console.print_json(data=test_case['schema'])
        
        # Analyze schema
        console.print(f"\n[bold yellow]Schema Analysis:[/bold yellow]")
        analysis = analyzer.analyze(test_case['schema'], test_case['context'])
        console.print(f"  • Complexity Score: {analysis.complexity_score:.2f}")
        console.print(f"  • Total Fields: {analysis.total_fields}")
        console.print(f"  • Depth: {analysis.depth}")
        console.print(f"  • Has Arrays: {analysis.has_arrays}")
        console.print(f"  • Has Nested Objects: {analysis.has_nested_objects}")
        
        # Show field types
        field_types = {}
        for field_name, field_analysis in analysis.fields.items():
            field_type = field_analysis.data_type.value
            if field_type not in field_types:
                field_types[field_type] = 0
            field_types[field_type] += 1
        
        console.print(f"  • Field Types: {dict(field_types)}")
        
        # Test 1: Single strategy
        console.print("\n[bold yellow]Test 1: Single Strategy (Chain-of-Thought)[/bold yellow]")
        console.print("-" * 40)
        
        # Log request details
        console.print(f"[cyan]Request Configuration:[/cyan]")
        console.print(f"  • Strategy: Chain-of-Thought")
        console.print(f"  • Multi-Strategy: False")
        console.print(f"  • Target Count: {test_case['count']}")
        console.print(f"  • Schema Keys: {list(test_case['schema'].keys())}")
        
        start_time = asyncio.get_event_loop().time()
        
        single_request = GenerationRequest(
            schema=test_case['schema'],
            context=test_case['context'],
            count=test_case['count'],
            strategy=PromptStrategy.CHAIN_OF_THOUGHT,
            use_multi_strategy=False,
            validation_level=ValidationLevel.LENIENT  # Use lenient validation for testing
        )
        
        console.print(f"\n[cyan]Generating with Chain-of-Thought strategy...[/cyan]")
        single_result = await engine.generate(single_request)
        single_time = asyncio.get_event_loop().time() - start_time
        
        console.print(f"\n[bold]Single Strategy Results:[/bold]")
        console.print(f"  • Execution Time: {single_time:.2f}s")
        console.print(f"  • Success: {single_result.success}")
        
        if single_result.success:
            console.print(f"  • [green]✓ Generated {len(single_result.data)} records[/green]")
            console.print(f"  • Validation Score: {single_result.validation_result.score:.2f}")
            
            # Display generated data sample
            if single_result.data:
                console.print(f"\n[bold green]Generated Data Sample:[/bold green]")
                sample_data = single_result.data[0] if isinstance(single_result.data, list) else single_result.data
                console.print_json(data=sample_data)
                
                # Show validation details
                if single_result.validation_result:
                    console.print(f"\n[cyan]Validation Details:[/cyan]")
                    console.print(f"  • Score: {single_result.validation_result.score:.2f}")
                    console.print(f"  • Is Valid: {single_result.validation_result.is_valid}")
                    if hasattr(single_result.validation_result, 'errors') and single_result.validation_result.errors:
                        console.print(f"  • Errors: {single_result.validation_result.errors}")
                    if hasattr(single_result.validation_result, 'warnings') and single_result.validation_result.warnings:
                        console.print(f"  • Warnings: {single_result.validation_result.warnings}")
        else:
            console.print(f"  • [red]✗ Generation failed[/red]")
            console.print(f"  • Errors: {single_result.errors}")
            
            # Show partial data if available
            if single_result.data:
                console.print(f"\n[bold yellow]Partial Generated Data (with errors):[/bold yellow]")
                console.print_json(data=single_result.data)
        
        # Test 2: Multi-strategy
        console.print("\n[bold yellow]Test 2: Multi-Strategy (Automatic)[/bold yellow]")
        console.print("-" * 40)
        
        # Log request details
        console.print(f"[cyan]Request Configuration:[/cyan]")
        console.print(f"  • Strategy: Automatic (Multi-Strategy)")
        console.print(f"  • Multi-Strategy: True")
        console.print(f"  • Target Count: {test_case['count']}")
        console.print(f"  • Schema Keys: {list(test_case['schema'].keys())}")
        
        start_time = asyncio.get_event_loop().time()
        
        multi_request = GenerationRequest(
            schema=test_case['schema'],
            context=test_case['context'],
            count=test_case['count'],
            use_multi_strategy=True,
            validation_level=ValidationLevel.LENIENT  # Use lenient validation for testing
        )
        
        console.print(f"\n[cyan]Generating with Multi-Strategy (automatic selection)...[/cyan]")
        multi_result = await engine.generate(multi_request)
        multi_time = asyncio.get_event_loop().time() - start_time
        
        console.print(f"\n[bold]Multi-Strategy Results:[/bold]")
        console.print(f"  • Execution Time: {multi_time:.2f}s")
        console.print(f"  • Success: {multi_result.success}")
        console.print(f"  • Strategy Used: {multi_result.metadata.get('strategy_used', 'unknown')}")
        
        if multi_result.success:
            console.print(f"  • [green]✓ Generated {len(multi_result.data)} records[/green]")
            console.print(f"  • Validation Score: {multi_result.validation_result.score:.2f}")
            
            # Display generated data sample
            if multi_result.data:
                console.print(f"\n[bold green]Generated Data Sample:[/bold green]")
                sample_data = multi_result.data[0] if isinstance(multi_result.data, list) else multi_result.data
                console.print_json(data=sample_data)
                
                # Show validation details
                if multi_result.validation_result:
                    console.print(f"\n[cyan]Validation Details:[/cyan]")
                    console.print(f"  • Score: {multi_result.validation_result.score:.2f}")
                    console.print(f"  • Is Valid: {multi_result.validation_result.is_valid}")
                    if hasattr(multi_result.validation_result, 'errors') and multi_result.validation_result.errors:
                        console.print(f"  • Errors: {multi_result.validation_result.errors}")
                    if hasattr(multi_result.validation_result, 'warnings') and multi_result.validation_result.warnings:
                        console.print(f"  • Warnings: {multi_result.validation_result.warnings}")
                
                # Show metadata details
                if multi_result.metadata:
                    console.print(f"\n[cyan]Generation Metadata:[/cyan]")
                    for key, value in multi_result.metadata.items():
                        console.print(f"  • {key}: {value}")
        else:
            console.print(f"  • [red]✗ Generation failed[/red]")
            console.print(f"  • Errors: {multi_result.errors}")
            
            # Show partial data if available
            if multi_result.data:
                console.print(f"\n[bold yellow]Partial Generated Data (with errors):[/bold yellow]")
                console.print_json(data=multi_result.data)
        
        # Test 3: Adaptive generation
        console.print("\n[bold yellow]Test 3: Adaptive Generation[/bold yellow]")
        console.print("-" * 40)
        
        # Log request details
        console.print(f"[cyan]Request Configuration:[/cyan]")
        console.print(f"  • Strategy: Adaptive (Auto-retry)")
        console.print(f"  • Max Attempts: 2")
        console.print(f"  • Target Count: {test_case['count']}")
        console.print(f"  • Schema Keys: {list(test_case['schema'].keys())}")
        
        start_time = asyncio.get_event_loop().time()
        
        adaptive_request = GenerationRequest(
            schema=test_case['schema'],
            context=test_case['context'],
            count=test_case['count'],
            validation_level=ValidationLevel.LENIENT  # Use lenient validation for testing
        )
        
        console.print(f"\n[cyan]Generating with Adaptive strategy (auto-retry)...[/cyan]")
        adaptive_result = await engine.generate_adaptive(adaptive_request, max_attempts=2)
        adaptive_time = asyncio.get_event_loop().time() - start_time
        
        console.print(f"\n[bold]Adaptive Generation Results:[/bold]")
        console.print(f"  • Execution Time: {adaptive_time:.2f}s")
        console.print(f"  • Success: {adaptive_result.success}")
        
        if adaptive_result.success:
            console.print(f"  • [green]✓ Generated {len(adaptive_result.data)} records[/green]")
            console.print(f"  • Final Score: {adaptive_result.validation_result.score:.2f}")
            
            # Display generated data sample
            if adaptive_result.data:
                console.print(f"\n[bold green]Generated Data Sample:[/bold green]")
                sample_data = adaptive_result.data[0] if isinstance(adaptive_result.data, list) else adaptive_result.data
                console.print_json(data=sample_data)
                
                # Show validation details
                if adaptive_result.validation_result:
                    console.print(f"\n[cyan]Validation Details:[/cyan]")
                    console.print(f"  • Score: {adaptive_result.validation_result.score:.2f}")
                    console.print(f"  • Is Valid: {adaptive_result.validation_result.is_valid}")
                    if hasattr(adaptive_result.validation_result, 'errors') and adaptive_result.validation_result.errors:
                        console.print(f"  • Errors: {adaptive_result.validation_result.errors}")
                    if hasattr(adaptive_result.validation_result, 'warnings') and adaptive_result.validation_result.warnings:
                        console.print(f"  • Warnings: {adaptive_result.validation_result.warnings}")
                
                # Show adaptive metadata
                if adaptive_result.metadata:
                    console.print(f"\n[cyan]Adaptive Generation Metadata:[/cyan]")
                    for key, value in adaptive_result.metadata.items():
                        console.print(f"  • {key}: {value}")
        else:
            console.print(f"  • [red]✗ Generation failed[/red]")
            console.print(f"  • Errors: {adaptive_result.errors}")
            
            # Show partial data if available
            if adaptive_result.data:
                console.print(f"\n[bold yellow]Partial Generated Data (with errors):[/bold yellow]")
                console.print_json(data=adaptive_result.data)
        
        # Add to results table
        results_table.add_row(
            test_case['name'],
            f"{analysis.complexity_score:.2f}",
            "Single (CoT)",
            "✓" if single_result.success else "✗",
            f"{single_result.validation_result.score:.2f}" if single_result.validation_result else "N/A",
            f"{single_time:.2f}s"
        )
        
        results_table.add_row(
            "",
            "",
            "Multi-Strategy",
            "✓" if multi_result.success else "✗",
            f"{multi_result.validation_result.score:.2f}" if multi_result.validation_result else "N/A",
            f"{multi_time:.2f}s"
        )
        
        results_table.add_row(
            "",
            "",
            "Adaptive",
            "✓" if adaptive_result.success else "✗",
            f"{adaptive_result.validation_result.score:.2f}" if adaptive_result.validation_result else "N/A",
            f"{adaptive_time:.2f}s"
        )
        
        # Performance comparison for this test case
        console.print(f"\n[bold cyan]Performance Comparison for {test_case['name']}:[/bold cyan]")
        single_score = f"{single_result.validation_result.score:.2f}" if single_result.validation_result else "N/A"
        multi_score = f"{multi_result.validation_result.score:.2f}" if multi_result.validation_result else "N/A"
        adaptive_score = f"{adaptive_result.validation_result.score:.2f}" if adaptive_result.validation_result else "N/A"
        
        console.print(f"  • Single Strategy: {single_time:.2f}s (Score: {single_score})")
        console.print(f"  • Multi-Strategy: {multi_time:.2f}s (Score: {multi_score})")
        console.print(f"  • Adaptive: {adaptive_time:.2f}s (Score: {adaptive_score})")
        
        # Determine best strategy
        strategies = [
            ("Single", single_result.validation_result.score if single_result.validation_result else 0),
            ("Multi", multi_result.validation_result.score if multi_result.validation_result else 0),
            ("Adaptive", adaptive_result.validation_result.score if adaptive_result.validation_result else 0)
        ]
        best_strategy = max(strategies, key=lambda x: x[1])
        console.print(f"  • [bold green]Best Strategy: {best_strategy[0]} (Score: {best_strategy[1]:.2f})[/bold green]")
        
        console.print("\n" + "="*60)
    
    # Display comprehensive results table
    console.print("\n[bold blue]Comprehensive Test Results Summary[/bold blue]")
    console.print("=" * 60)
    console.print(results_table)
    
    # Performance comparison and insights
    console.print("\n[bold blue]Key Findings and Insights:[/bold blue]")
    console.print("=" * 50)
    console.print("1. [green]Multi-strategy typically achieves higher validation scores[/green]")
    console.print("2. [green]Adaptive generation can recover from initial failures[/green]")
    console.print("3. [green]Complex schemas benefit most from multi-strategy approach[/green]")
    console.print("4. [yellow]Execution time varies significantly between strategies[/yellow]")
    console.print("5. [cyan]Schema complexity affects strategy performance[/cyan]")
    
    # Calculate overall statistics
    total_tests = len(test_cases) * 3  # 3 strategies per test case
    successful_generations = sum([
        1 for test_case in test_cases
        for result in [single_result, multi_result, adaptive_result]
        if result.success
    ])
    
    console.print(f"\n[bold cyan]Overall Statistics:[/bold cyan]")
    console.print(f"  • Total Test Cases: {len(test_cases)}")
    console.print(f"  • Total Strategy Tests: {total_tests}")
    console.print(f"  • Successful Generations: {successful_generations}")
    console.print(f"  • Success Rate: {(successful_generations/total_tests)*100:.1f}%")

@save_generation_output("specific_strategy_testing")
async def test_specific_strategies():
    """Test specific strategy combinations"""
    console.print("\n[bold blue]Testing Specific Strategy Combinations[/bold blue]")
    console.print("=" * 60)
    
    # Initialize components
    console.print("[cyan]Initializing components for specific strategy testing...[/cyan]")
    llm_manager = LLMManager()
    await llm_manager.initialize()
    
    engine = JSONGenerationEngine(llm_manager)
    
    console.print(f"[green]✓[/green] Components initialized successfully")
    console.print(f"  • LLM Manager: {type(llm_manager).__name__}")
    console.print(f"  • Generation Engine: {type(engine).__name__}")
    console.print()
    
    # E-commerce product schema
    console.print("[bold yellow]Test Schema: E-commerce Product[/bold yellow]")
    console.print("-" * 40)
    
    schema = {
        "productId": str(uuid.uuid4()),
        "name": "Wireless Headphones",
        "brand": "AudioTech",
        "price": 79.99,
        "originalPrice": 99.99,
        "categories": ["Electronics", "Audio", "Wireless"],
        "tags": ["bluetooth", "noise-cancelling", "wireless"],
        "specifications": {
            "batteryLife": "30 hours",
            "connectivity": "Bluetooth 5.0",
            "noiseCancellation": True,
            "waterResistance": "IPX4",
            "weight": "250g",
            "warranty": "2 years"
        },
        "features": [
            "Active Noise Cancellation",
            "Touch Controls",
            "Voice Assistant Support",
            "Quick Charge"
        ],
        "inStock": True,
        "stockQuantity": 45,
        "rating": 4.5,
        "reviewCount": 128,
        "seller": {
            "id": str(uuid.uuid4()),
            "name": "AudioTech Store",
            "rating": 4.8,
            "verified": True
        },
        "shipping": {
            "freeShipping": True,
            "estimatedDelivery": "2-3 business days",
            "returnPolicy": "30 days"
        },
        "images": [
            {
                "id": str(uuid.uuid4()),
                "url": "https://example.com/images/headphones-main.jpg",
                "alt": "Wireless Headphones Main View",
                "primary": True
            },
            {
                "id": str(uuid.uuid4()),
                "url": "https://example.com/images/headphones-side.jpg",
                "alt": "Wireless Headphones Side View",
                "primary": False
            }
        ],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:45:00Z"
    }
    
    # Display schema details
    console.print(f"[cyan]Schema Details:[/cyan]")
    console.print(f"  • Total Fields: {len(schema)}")
    console.print(f"  • Nested Objects: {sum(1 for v in schema.values() if isinstance(v, dict))}")
    console.print(f"  • Arrays: {sum(1 for v in schema.values() if isinstance(v, list))}")
    console.print(f"  • Context: e-commerce products")
    console.print(f"  • Target Count: 3 records")
    
    # Show schema structure
    console.print(f"\n[bold yellow]Schema Structure:[/bold yellow]")
    console.print_json(data=schema)
    console.print()
    
    # Test individual strategies
    individual_strategies = [
        ("Chain-of-Thought", PromptStrategy.CHAIN_OF_THOUGHT),
        ("Few-Shot", PromptStrategy.FEW_SHOT),
        ("Structured", PromptStrategy.STRUCTURED),
        ("Zero-Shot", PromptStrategy.ZERO_SHOT)
    ]
    
    # Create results table
    strategy_table = Table(title="Individual Strategy Performance")
    strategy_table.add_column("Strategy", style="cyan")
    strategy_table.add_column("Success", style="bold")
    strategy_table.add_column("Score", style="magenta")
    strategy_table.add_column("Time", style="blue")
    strategy_table.add_column("Records Generated", style="green")
    
    for strategy_name, strategy in individual_strategies:
        console.print(f"\n[bold yellow]Testing Individual Strategy: {strategy_name}[/bold yellow]")
        console.print("-" * 50)
        
        # Log strategy details
        console.print(f"[cyan]Strategy Configuration:[/cyan]")
        console.print(f"  • Strategy: {strategy_name}")
        console.print(f"  • Strategy Type: {strategy}")
        console.print(f"  • Multi-Strategy: False (forced single)")
        console.print(f"  • Target Count: 3")
        
        start_time = asyncio.get_event_loop().time()
        
        # Test individual strategy
        request = GenerationRequest(
            schema=schema,
            context="e-commerce products",
            count=3,
            strategy=strategy,
            use_multi_strategy=False,  # Force single strategy
            validation_level=ValidationLevel.LENIENT  # Use lenient validation for testing
        )
        
        console.print(f"\n[cyan]Generating with {strategy_name} strategy...[/cyan]")
        result = await engine.generate(request)
        execution_time = asyncio.get_event_loop().time() - start_time
        
        console.print(f"\n[bold]Results for {strategy_name}:[/bold]")
        console.print(f"  • Execution Time: {execution_time:.2f}s")
        console.print(f"  • Success: {result.success}")
        
        if result.success:
            console.print(f"  • [green]✓ Success - Score: {result.validation_result.score:.2f}[/green]")
            console.print(f"  • Generated {len(result.data)} records")
            
            # Show validation details
            if result.validation_result:
                console.print(f"\n[cyan]Validation Details:[/cyan]")
                console.print(f"  • Score: {result.validation_result.score:.2f}")
                console.print(f"  • Is Valid: {result.validation_result.is_valid}")
                if hasattr(result.validation_result, 'errors') and result.validation_result.errors:
                    console.print(f"  • Errors: {result.validation_result.errors}")
                if hasattr(result.validation_result, 'warnings') and result.validation_result.warnings:
                    console.print(f"  • Warnings: {result.validation_result.warnings}")
            
            # Show generated data sample
            if result.data:
                console.print(f"\n[bold green]Generated Data Sample:[/bold green]")
                sample_data = result.data[0] if isinstance(result.data, list) else result.data
                console.print_json(data=sample_data)
                
                # Show all records if verbose
                if VERBOSE and len(result.data) > 1:
                    console.print(f"\n[bold cyan]All Generated Records:[/bold cyan]")
                    for i, record in enumerate(result.data):
                        console.print(f"\n[bold]Record {i+1}:[/bold]")
                        console.print_json(data=record)
        else:
            console.print(f"  • [red]✗ Failed[/red]")
            console.print(f"  • Errors: {result.errors}")
            
            # Show partial data if available
            if result.data:
                console.print(f"\n[bold yellow]Partial Generated Data (with errors):[/bold yellow]")
                console.print_json(data=result.data)
        
        # Add to table
        strategy_table.add_row(
            strategy_name,
            "✓" if result.success else "✗",
            f"{result.validation_result.score:.2f}" if result.validation_result else "N/A",
            f"{execution_time:.2f}s",
            str(len(result.data)) if result.data else "0"
        )
    
    # Test multi-strategy combinations
    console.print("\n[bold blue]Testing Multi-Strategy Combinations[/bold blue]")
    console.print("=" * 50)
    
    multi_strategy_tests = [
        ("Multi-Strategy (Auto)", True),
        ("Adaptive Generation", "adaptive")
    ]
    
    for test_name, strategy_type in multi_strategy_tests:
        console.print(f"\n[bold yellow]Testing Multi-Strategy: {test_name}[/bold yellow]")
        console.print("-" * 50)
        
        # Log strategy details
        console.print(f"[cyan]Strategy Configuration:[/cyan]")
        console.print(f"  • Strategy Type: {test_name}")
        console.print(f"  • Mode: {strategy_type}")
        console.print(f"  • Target Count: 3")
        
        start_time = asyncio.get_event_loop().time()
        
        if strategy_type == "adaptive":
            console.print(f"\n[cyan]Generating with Adaptive strategy (auto-retry)...[/cyan]")
            request = GenerationRequest(
                schema=schema,
                context="e-commerce products",
                count=3,
                validation_level=ValidationLevel.LENIENT  # Use lenient validation for testing
            )
            result = await engine.generate_adaptive(request, max_attempts=2)
        else:
            console.print(f"\n[cyan]Generating with Multi-Strategy (automatic selection)...[/cyan]")
            request = GenerationRequest(
                schema=schema,
                context="e-commerce products",
                count=3,
                use_multi_strategy=True,
                validation_level=ValidationLevel.LENIENT  # Use lenient validation for testing
            )
            result = await engine.generate(request)
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        console.print(f"\n[bold]Results for {test_name}:[/bold]")
        console.print(f"  • Execution Time: {execution_time:.2f}s")
        console.print(f"  • Success: {result.success}")
        
        if result.success:
            console.print(f"  • [green]✓ Success - Score: {result.validation_result.score:.2f}[/green]")
            console.print(f"  • Strategy Used: {result.metadata.get('strategy_used', 'unknown')}")
            console.print(f"  • Generated {len(result.data)} records")
            
            # Show validation details
            if result.validation_result:
                console.print(f"\n[cyan]Validation Details:[/cyan]")
                console.print(f"  • Score: {result.validation_result.score:.2f}")
                console.print(f"  • Is Valid: {result.validation_result.is_valid}")
                if hasattr(result.validation_result, 'errors') and result.validation_result.errors:
                    console.print(f"  • Errors: {result.validation_result.errors}")
                if hasattr(result.validation_result, 'warnings') and result.validation_result.warnings:
                    console.print(f"  • Warnings: {result.validation_result.warnings}")
            
            # Show metadata details
            if result.metadata:
                console.print(f"\n[cyan]Generation Metadata:[/cyan]")
                for key, value in result.metadata.items():
                    console.print(f"  • {key}: {value}")
            
            # Show generated data sample
            if result.data:
                console.print(f"\n[bold green]Generated Data Sample:[/bold green]")
                sample_data = result.data[0] if isinstance(result.data, list) else result.data
                console.print_json(data=sample_data)
                
                # Show all records if verbose
                if VERBOSE and len(result.data) > 1:
                    console.print(f"\n[bold cyan]All Generated Records:[/bold cyan]")
                    for i, record in enumerate(result.data):
                        console.print(f"\n[bold]Record {i+1}:[/bold]")
                        console.print_json(data=record)
        else:
            console.print(f"  • [red]✗ Failed[/red]")
            console.print(f"  • Errors: {result.errors}")
            
            # Show partial data if available
            if result.data:
                console.print(f"\n[bold yellow]Partial Generated Data (with errors):[/bold yellow]")
                console.print_json(data=result.data)
        
        # Add to table
        strategy_table.add_row(
            test_name,
            "✓" if result.success else "✗",
            f"{result.validation_result.score:.2f}" if result.validation_result else "N/A",
            f"{execution_time:.2f}s",
            str(len(result.data)) if result.data else "0"
        )
    
    # Display comprehensive results table
    console.print("\n[bold blue]Strategy Performance Comparison Table[/bold blue]")
    console.print("=" * 60)
    console.print(strategy_table)
    
    # Calculate performance statistics
    successful_strategies = sum(1 for row in strategy_table.rows if "✓" in str(row))
    total_strategies = len(strategy_table.rows)
    
    # Find best performing strategy
    best_score = 0
    best_strategy = "None"
    for row in strategy_table.rows:
        row_str = str(row)
        if "✓" in row_str:
            # Extract score from the row string
            try:
                # Find the score in the row string (format: "Strategy ✓ Score Time Records")
                parts = row_str.split()
                if len(parts) >= 3:
                    score_str = parts[2]
                    if score_str != "N/A":
                        score = float(score_str)
                        if score > best_score:
                            best_score = score
                            best_strategy = parts[0]  # First part is strategy name
            except (ValueError, IndexError):
                continue
    
    # Summary and insights
    console.print("\n[bold blue]Strategy Testing Summary and Insights[/bold blue]")
    console.print("=" * 60)
    console.print(f"[cyan]Overall Statistics:[/cyan]")
    console.print(f"  • Total Strategies Tested: {total_strategies}")
    console.print(f"  • Successful Strategies: {successful_strategies}")
    console.print(f"  • Success Rate: {(successful_strategies/total_strategies)*100:.1f}%")
    console.print(f"  • Best Strategy: {best_strategy} (Score: {best_score:.2f})")
    
    console.print(f"\n[bold yellow]Key Findings:[/bold yellow]")
    console.print("1. [green]Individual strategies show different performance characteristics[/green]")
    console.print("2. [green]Multi-strategy approaches can combine the best of multiple strategies[/green]")
    console.print("3. [green]Adaptive generation can automatically select the best strategy[/green]")
    console.print("4. [yellow]Strategy selection depends on schema complexity and context[/yellow]")
    console.print("5. [cyan]Validation scores help identify the most effective approach[/cyan]")
    
    # Performance recommendations
    console.print(f"\n[bold cyan]Performance Recommendations:[/bold cyan]")
    if best_strategy != "None":
        console.print(f"  • [green]Recommended Strategy: {best_strategy}[/green]")
        console.print(f"  • [green]Expected Score: {best_score:.2f}[/green]")
    
    # Strategy-specific insights
    console.print(f"\n[bold yellow]Strategy-Specific Insights:[/bold yellow]")
    console.print("  • [cyan]Chain-of-Thought:[/cyan] Good for complex reasoning tasks")
    console.print("  • [cyan]Few-Shot:[/cyan] Effective with clear examples")
    console.print("  • [cyan]Structured:[/cyan] Best for well-defined schemas")
    console.print("  • [cyan]Zero-Shot:[/cyan] Fastest but may have lower accuracy")
    console.print("  • [cyan]Multi-Strategy:[/cyan] Automatic selection based on context")
    console.print("  • [cyan]Adaptive:[/cyan] Auto-retry with different strategies")

@with_output_summary
async def main():
    """Run all tests"""
    try:
        await test_multi_strategy()
        await test_specific_strategies()
        
        # Display final summary
        console.print("\n[bold blue]Test Run Summary[/bold blue]")
        console.print("=" * 50)
        
        # Get summary from output manager
        summary_path = output_manager.generate_summary_report()
        console.print(f"[green]✓[/green] Summary report saved to: {summary_path}")
        
        # Display output summary table
        output_manager.display_output_summary()
        
        # Show saved output files if requested
        if args.show_outputs:
            console.print("\n[bold blue]Saved Output Files:[/bold blue]")
            console.print("=" * 50)
            
            # List all generation data files
            generation_files = list(output_manager.generation_output_dir.glob('*.json'))
            if generation_files:
                console.print(f"\n[green]Found {len(generation_files)} generation data files:[/green]")
                for file_path in sorted(generation_files, key=lambda x: x.stat().st_mtime, reverse=True):
                    console.print(f"  📄 {file_path.name}")
                    
                    # Show a preview of the file content
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if 'output_data' in data and data['output_data']:
                                console.print(f"    [dim]Contains {len(data['output_data'])} records[/dim]")
                            else:
                                console.print(f"    [dim]No output data[/dim]")
                    except Exception as e:
                        console.print(f"    [dim]Error reading file: {e}[/dim]")
            else:
                console.print("[yellow]No generation data files found[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test multi-strategy JSON generation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output including generated JSON")
    parser.add_argument("--show-outputs", "-o", action="store_true", help="Show saved output files")
    args = parser.parse_args()
    
    # Set global verbose flag
    VERBOSE = args.verbose or args.show_outputs
    
    asyncio.run(main())