"""
Enhanced Multi-Strategy Test Suite with Comprehensive Feedback System

This test suite demonstrates the integration of the feedback system with JSON generation tests,
providing detailed tracking, error analysis, performance monitoring, and intelligent recovery
suggestions.

Features:
- Comprehensive feedback tracking for all test phases
- Detailed error analysis and categorization
- Performance monitoring and optimization insights
- Intelligent recovery suggestions
- Pattern detection and analysis
- Automated reporting and dashboards

Test Types:
1. Simple Schema Tests - Basic validation and generation
2. Complex Schema Tests - Advanced patterns and relationships
3. Performance Tests - Speed and efficiency analysis
4. Error Recovery Tests - Failure handling and recovery
5. Validation Tests - Schema compliance and data quality
6. Strategy Comparison Tests - Effectiveness analysis

Usage:
    python -m pytest src/tests/test_multi_strategy_enhanced.py -v -s
    
The tests will automatically generate comprehensive reports and save detailed
session data for analysis.
"""

import asyncio
import pytest
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Rich imports for enhanced console output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.tree import Tree
from rich.text import Text

# Core system imports
from src.core.generation_engine import JSONGenerationEngine, GenerationRequest
from src.core.config import settings
from src.core.llm_manager import LLMManager
from src.core.schema_analyzer import SchemaAnalyzer
from src.core.prompt_engineer import PromptStrategy
from src.core.output_parser import ValidationLevel

# Enhanced feedback system imports
from src.core.feedback_system import feedback_system, GenerationPhase, ErrorSeverity, ErrorCategory
from src.utils.testing.enhanced_test_decorators import (
    comprehensive_test_tracking,
    generation_test_tracking,
    performance_test_tracking,
    validation_test_tracking,
    with_comprehensive_analysis
)

console = Console()

class TestMultiStrategyEnhanced:
    """Enhanced test suite with comprehensive feedback integration"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment with feedback system"""
        console.print("\n[bold blue]🚀 Initializing Enhanced Test Suite[/bold blue]")
        
        # Initialize core components
        cls.llm_manager = LLMManager()
        cls.schema_analyzer = SchemaAnalyzer()
        cls.generation_engine = JSONGenerationEngine(
            llm_manager=cls.llm_manager
        )
        
        # Test schemas
        cls.simple_schema = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30,
            "active": True
        }
        
        cls.complex_schema = {
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "profile": {
                "personal_info": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "date_of_birth": "1990-05-15",
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
                "account_type": "premium",
                "created_at": "2023-01-15T10:30:00Z",
                "last_login": "2024-01-15T14:22:33Z",
                "billing": {
                    "plan": "pro",
                    "amount": 29.99,
                    "currency": "USD",
                    "billing_cycle": "monthly"
                }
            },
            "metadata": {
                "tags": ["vip", "early_adopter"],
                "custom_fields": {
                    "referral_code": "REF123456",
                    "source": "organic"
                }
            }
        }
        
        console.print("[green]✅ Test environment initialized successfully[/green]")
    
    @comprehensive_test_tracking("simple_schema_comprehensive")
    def test_simple_schema_comprehensive(self):
        """Test simple schema with comprehensive feedback tracking"""
        console.print("\n[bold cyan]🧪 Testing Simple Schema (Comprehensive)[/bold cyan]")
        
        try:
            # Test different strategies
            strategies = [
                PromptStrategy.ZERO_SHOT,
                PromptStrategy.CHAIN_OF_THOUGHT,
                PromptStrategy.STRUCTURED,
                PromptStrategy.FEW_SHOT
            ]
            
            results = {}
            
            for strategy in strategies:
                console.print(f"[yellow]Testing strategy: {strategy.value}[/yellow]")
                
                request = GenerationRequest(
                    schema=self.simple_schema,
                    count=3,
                    context="Simple user profile for testing",
                    strategy=strategy,
                    validation_level=ValidationLevel.LENIENT,
                    max_retries=2
                )
                
                start_time = time.time()
                result = asyncio.run(self.generation_engine.generate(request))
                execution_time = time.time() - start_time
                
                results[strategy.value] = {
                    'success': result.success,
                    'execution_time': execution_time,
                    'validation_score': result.validation_result.score if result.validation_result else 0.0,
                    'record_count': len(result.data) if result.data else 0,
                    'errors': result.validation_result.errors if result.validation_result else []
                }
                
                console.print(f"[green]✅ Strategy {strategy.value}: {result.success} (Score: {results[strategy.value]['validation_score']:.2f})[/green]")
            
            # Analyze results
            successful_strategies = [s for s, r in results.items() if r['success']]
            best_strategy = max(results.items(), key=lambda x: x[1]['validation_score'])
            
            console.print(f"\n[bold green]📊 Results Summary:[/bold green]")
            console.print(f"[green]Successful Strategies: {len(successful_strategies)}/{len(strategies)}[/green]")
            console.print(f"[green]Best Strategy: {best_strategy[0]} (Score: {best_strategy[1]['validation_score']:.2f})[/green]")
            
            return {
                'results': results,
                'best_strategy': best_strategy[0],
                'success_rate': len(successful_strategies) / len(strategies),
                'validation_score': best_strategy[1]['validation_score']
            }
            
        except Exception as e:
            console.print(f"[red]❌ Test failed: {str(e)}[/red]")
            raise
    
    @generation_test_tracking("complex_schema_generation")
    def test_complex_schema_generation(self):
        """Test complex schema with detailed generation tracking"""
        console.print("\n[bold cyan]🧪 Testing Complex Schema (Generation Focus)[/bold cyan]")
        
        try:
            # Test multi-strategy approach
            request = GenerationRequest(
                schema=self.complex_schema,
                count=2,
                context="Complex user profile with nested data and relationships",
                use_multi_strategy=True,
                validation_level=ValidationLevel.LENIENT,
                max_retries=3
            )
            
            start_time = time.time()
            result = asyncio.run(self.generation_engine.generate(request))
            execution_time = time.time() - start_time
            
            # Detailed analysis
            analysis = {
                'success': result.success,
                'execution_time': execution_time,
                'validation_score': result.validation_result.score if result.validation_result else 0.0,
                'record_count': len(result.data) if result.data else 0,
                'complexity_factors': {
                    'nested_levels': self._count_nested_levels(self.complex_schema),
                    'total_fields': self._count_total_fields(self.complex_schema),
                    'field_types': self._analyze_field_types(self.complex_schema)
                }
            }
            
            console.print(f"[green]✅ Complex Schema Generation: {result.success}[/green]")
            console.print(f"[yellow]Validation Score: {analysis['validation_score']:.2f}[/yellow]")
            console.print(f"[yellow]Execution Time: {execution_time:.2f}s[/yellow]")
            console.print(f"[yellow]Records Generated: {analysis['record_count']}[/yellow]")
            
            return analysis
            
        except Exception as e:
            console.print(f"[red]❌ Complex schema test failed: {str(e)}[/red]")
            raise
    
    @performance_test_tracking("performance_benchmark")
    def test_performance_benchmark(self):
        """Performance benchmark with detailed monitoring"""
        console.print("\n[bold cyan]🏃 Performance Benchmark Test[/bold cyan]")
        
        try:
            # Test different record counts
            record_counts = [1, 5, 10, 20]
            performance_data = {}
            
            for count in record_counts:
                console.print(f"[yellow]Testing with {count} records...[/yellow]")
                
                request = GenerationRequest(
                    schema=self.simple_schema,
                    count=count,
                    context="Performance testing",
                    strategy=PromptStrategy.STRUCTURED,  # Most reliable for performance
                    validation_level=ValidationLevel.LENIENT
                )
                
                start_time = time.time()
                result = asyncio.run(self.generation_engine.generate(request))
                execution_time = time.time() - start_time
                
                performance_data[count] = {
                    'execution_time': execution_time,
                    'records_per_second': count / execution_time if execution_time > 0 else 0,
                    'success': result.success,
                    'validation_score': result.validation_result.score if result.validation_result else 0.0
                }
                
                console.print(f"[green]✅ {count} records: {execution_time:.2f}s ({performance_data[count]['records_per_second']:.2f} records/sec)[/green]")
            
            # Performance analysis
            avg_time_per_record = sum(data['execution_time'] for data in performance_data.values()) / sum(record_counts)
            best_throughput = max(performance_data.values(), key=lambda x: x['records_per_second'])
            
            console.print(f"\n[bold green]📊 Performance Summary:[/bold green]")
            console.print(f"[green]Average Time per Record: {avg_time_per_record:.3f}s[/green]")
            console.print(f"[green]Best Throughput: {best_throughput['records_per_second']:.2f} records/sec[/green]")
            
            return {
                'performance_data': performance_data,
                'avg_time_per_record': avg_time_per_record,
                'best_throughput': best_throughput['records_per_second']
            }
            
        except Exception as e:
            console.print(f"[red]❌ Performance test failed: {str(e)}[/red]")
            raise
    
    @validation_test_tracking("validation_stress_test")
    def test_validation_stress_test(self):
        """Stress test validation system with various edge cases"""
        console.print("\n[bold cyan]🔬 Validation Stress Test[/bold cyan]")
        
        try:
            # Test with intentionally problematic schemas
            edge_case_schemas = [
                # Very long strings
                {"id": "x" * 100, "name": "Very long name test"},
                # Special characters
                {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "Test with émojis 🚀 and spëcial chars"},
                # Numeric edge cases
                {"id": "550e8400-e29b-41d4-a716-446655440000", "age": 999, "balance": 0.01},
                # Boolean variations
                {"id": "550e8400-e29b-41d4-a716-446655440000", "active": True, "verified": False}
            ]
            
            validation_results = {}
            
            for i, schema in enumerate(edge_case_schemas):
                console.print(f"[yellow]Testing edge case {i+1}...[/yellow]")
                
                request = self.generation_engine.GenerationRequest(
                    schema=schema,
                    count=2,
                    context=f"Edge case validation test {i+1}",
                    strategy=PromptStrategy.STRUCTURED,
                    validation_level=ValidationLevel.STRICT  # Use strict validation for stress test
                )
                
                try:
                    result = asyncio.run(self.generation_engine.generate(request))
                    validation_results[f"edge_case_{i+1}"] = {
                        'success': result.success,
                        'validation_score': result.validation_result.score if result.validation_result else 0.0,
                        'errors': result.validation_result.errors if result.validation_result else [],
                        'record_count': len(result.data) if result.data else 0
                    }
                    console.print(f"[green]✅ Edge case {i+1}: {result.success}[/green]")
                except Exception as e:
                    validation_results[f"edge_case_{i+1}"] = {
                        'success': False,
                        'error': str(e),
                        'validation_score': 0.0
                    }
                    console.print(f"[red]❌ Edge case {i+1}: Failed - {str(e)}[/red]")
            
            # Analyze validation robustness
            successful_cases = sum(1 for r in validation_results.values() if r.get('success', False))
            avg_validation_score = sum(r.get('validation_score', 0) for r in validation_results.values()) / len(validation_results)
            
            console.print(f"\n[bold green]📊 Validation Stress Test Results:[/bold green]")
            console.print(f"[green]Successful Cases: {successful_cases}/{len(edge_case_schemas)}[/green]")
            console.print(f"[green]Average Validation Score: {avg_validation_score:.2f}[/green]")
            
            return {
                'validation_results': validation_results,
                'success_rate': successful_cases / len(edge_case_schemas),
                'avg_validation_score': avg_validation_score
            }
            
        except Exception as e:
            console.print(f"[red]❌ Validation stress test failed: {str(e)}[/red]")
            raise
    
    @with_comprehensive_analysis("error_recovery_simulation")
    def test_error_recovery_simulation(self):
        """Simulate various error conditions and test recovery mechanisms"""
        console.print("\n[bold cyan]🛠️ Error Recovery Simulation[/bold cyan]")
        
        try:
            # Simulate different error scenarios
            error_scenarios = [
                {
                    'name': 'Invalid Schema',
                    'schema': {'invalid_field': None},  # This should cause issues
                    'expected_error': 'schema_error'
                },
                {
                    'name': 'Timeout Simulation',
                    'schema': self.simple_schema,
                    'count': 100,  # Large count to potentially cause timeout
                    'expected_error': 'timeout_error'
                },
                {
                    'name': 'Complex Validation',
                    'schema': self.complex_schema,
                    'validation_level': ValidationLevel.STRICT,
                    'expected_error': 'validation_error'
                }
            ]
            
            recovery_results = {}
            
            for scenario in error_scenarios:
                console.print(f"[yellow]Testing scenario: {scenario['name']}[/yellow]")
                
                request = self.generation_engine.GenerationRequest(
                    schema=scenario['schema'],
                    count=scenario.get('count', 2),
                    context=f"Error recovery test: {scenario['name']}",
                    strategy=PromptStrategy.ZERO_SHOT,
                    validation_level=scenario.get('validation_level', ValidationLevel.LENIENT),
                    max_retries=3
                )
                
                try:
                    result = asyncio.run(self.generation_engine.generate(request))
                    recovery_results[scenario['name']] = {
                        'success': result.success,
                        'recovered': True,
                        'validation_score': result.validation_result.score if result.validation_result else 0.0,
                        'retry_count': getattr(result, 'retry_count', 0)
                    }
                    console.print(f"[green]✅ {scenario['name']}: Recovered successfully[/green]")
                except Exception as e:
                    recovery_results[scenario['name']] = {
                        'success': False,
                        'recovered': False,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                    console.print(f"[red]❌ {scenario['name']}: Recovery failed - {str(e)}[/red]")
            
            # Analyze recovery effectiveness
            successful_recoveries = sum(1 for r in recovery_results.values() if r.get('recovered', False))
            recovery_rate = successful_recoveries / len(error_scenarios)
            
            console.print(f"\n[bold green]📊 Error Recovery Results:[/bold green]")
            console.print(f"[green]Successful Recoveries: {successful_recoveries}/{len(error_scenarios)}[/green]")
            console.print(f"[green]Recovery Rate: {recovery_rate:.1%}[/green]")
            
            return {
                'recovery_results': recovery_results,
                'recovery_rate': recovery_rate,
                'scenarios_tested': len(error_scenarios)
            }
            
        except Exception as e:
            console.print(f"[red]❌ Error recovery simulation failed: {str(e)}[/red]")
            raise
    
    def test_comprehensive_system_analysis(self):
        """Run comprehensive system analysis and generate final report"""
        console.print("\n[bold blue]📊 Comprehensive System Analysis[/bold blue]")
        
        try:
            # Display system health dashboard
            feedback_system.display_system_dashboard()
            
            # Generate comprehensive report
            health_data = feedback_system.get_system_health()
            
            # Create summary report
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_health': health_data,
                'test_summary': {
                    'total_sessions': health_data['global_metrics']['total_sessions'],
                    'success_rate': health_data['global_metrics']['success_rate'],
                    'total_errors': health_data['global_metrics']['total_errors'],
                    'active_sessions': health_data['active_sessions']
                },
                'recommendations': self._generate_recommendations(health_data)
            }
            
            # Save report
            report_path = Path("outputs/feedback/comprehensive_report.json")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            console.print(f"[green]✅ Comprehensive report saved to: {report_path}[/green]")
            
            return report
            
        except Exception as e:
            console.print(f"[red]❌ System analysis failed: {str(e)}[/red]")
            raise
    
    def _count_nested_levels(self, schema: Dict[str, Any], level: int = 0) -> int:
        """Count the maximum nesting level in a schema"""
        max_level = level
        for value in schema.values():
            if isinstance(value, dict):
                max_level = max(max_level, self._count_nested_levels(value, level + 1))
        return max_level
    
    def _count_total_fields(self, schema: Dict[str, Any]) -> int:
        """Count total number of fields in a schema"""
        count = len(schema)
        for value in schema.values():
            if isinstance(value, dict):
                count += self._count_total_fields(value)
        return count
    
    def _analyze_field_types(self, schema: Dict[str, Any]) -> Dict[str, int]:
        """Analyze field types in a schema"""
        type_counts = {}
        for value in schema.values():
            if isinstance(value, dict):
                nested_types = self._analyze_field_types(value)
                for t, c in nested_types.items():
                    type_counts[t] = type_counts.get(t, 0) + c
            else:
                type_name = type(value).__name__
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        return type_counts
    
    def _generate_recommendations(self, health_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on system health"""
        recommendations = []
        
        success_rate = health_data['global_metrics']['success_rate']
        if success_rate < 0.8:
            recommendations.append("Consider using more lenient validation settings for better success rates")
        
        if health_data['global_metrics']['total_errors'] > 10:
            recommendations.append("High error count detected - review error patterns for optimization")
        
        if health_data.get('detected_patterns'):
            recommendations.append("Error patterns detected - implement targeted fixes for recurring issues")
        
        perf_summary = health_data.get('performance_summary', {})
        if perf_summary.get('recent_avg_duration', 0) > 30:
            recommendations.append("Consider optimizing generation speed - current average duration is high")
        
        return recommendations

# Run tests if executed directly
if __name__ == "__main__":
    # Initialize console
    console.print("[bold blue]🚀 Running Enhanced Multi-Strategy Test Suite[/bold blue]")
    
    # Create test instance
    test_suite = TestMultiStrategyEnhanced()
    test_suite.setup_class()
    
    # Run all tests
    tests = [
        test_suite.test_simple_schema_comprehensive,
        test_suite.test_complex_schema_generation,
        test_suite.test_performance_benchmark,
        test_suite.test_validation_stress_test,
        test_suite.test_error_recovery_simulation,
        test_suite.test_comprehensive_system_analysis
    ]
    
    console.print(f"\n[bold green]📋 Running {len(tests)} enhanced tests...[/bold green]")
    
    for test in tests:
        try:
            console.print(f"\n[cyan]🧪 Running: {test.__name__}[/cyan]")
            result = test()
            console.print(f"[green]✅ {test.__name__} completed successfully[/green]")
        except Exception as e:
            console.print(f"[red]❌ {test.__name__} failed: {str(e)}[/red]")
    
    # Final system dashboard
    console.print("\n[bold blue]📊 Final System Dashboard[/bold blue]")
    feedback_system.display_system_dashboard()
    
    console.print("\n[bold green]🎉 Enhanced test suite completed![/bold green]") 