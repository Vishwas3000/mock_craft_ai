"""
Test Decorators for Automatic Output Management

This module provides decorators for automatically saving test outputs, generation results, validation results,
and performance metrics using the OutputManager. It is designed to help you:

- Automatically log test results, errors, and metadata to organized output directories (see output_manager.py)
- Save outputs for both synchronous and asynchronous test functions
- Display a summary of all outputs after tests run

USAGE:
------
1. Import the decorators in your test or experiment files:

    from src.utils.testing.test_decorators import save_test_output, save_generation_output, save_validation_output, save_performance_output, with_output_summary

2. Decorate your test functions:

    @save_test_output("my_test_name")
    def my_test(...):
        ...
        return result

    @save_generation_output("generation_test")
    def test_generation(...):
        ...
        return generated_data

    @save_validation_output("validation_test")
    def test_validation(...):
        ...
        return validation_result

    @with_output_summary
    def run_all_tests():
        ...

- All outputs are saved using the OutputManager (see output_manager.py) in the 'outputs/' directory, organized by type.
- Errors are automatically logged with tracebacks.
- A summary table is printed at the end of your test run.

See the bottom of this file for example usage.
"""

import functools
import asyncio
import time
import sys
from typing import Callable, Any, Dict, Optional
from rich.console import Console

# Debug: Show current module info
print(f"DEBUG: __name__ = {__name__}")
print(f"DEBUG: sys.path = {sys.path[:3]}...")  # Show first 3 paths
print(f"DEBUG: Current working directory = {sys.path[0]}")

try:
    from ..output.output_manager import output_manager, OutputType
    print("DEBUG: Relative import SUCCESS")
except ImportError as e:
    print(f"DEBUG: Relative import FAILED: {e}")
    # Fallback for direct execution
    import sys
    sys.path.append('/Users/sudeepsharma/Documents/GitHub/mock_craft_ai/json-generator')
    from src.utils.output.output_manager import output_manager, OutputType
    print("DEBUG: Absolute import SUCCESS")

console = Console()

def save_test_output(test_name: Optional[str] = None, output_type: OutputType = OutputType.TEST_RESULT):
    """Decorator to automatically save test outputs"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            test_name_actual = test_name or func.__name__
            
            try:
                # Extract input data from function arguments
                input_data = {
                    'args': [str(arg) for arg in args],
                    'kwargs': kwargs
                }
                
                # Run the test
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Save successful result
                metadata = {
                    'execution_time': execution_time,
                    'success': True
                }
                
                output_path = output_manager.save_test_output(
                    test_name=test_name_actual,
                    input_data=input_data,
                    output_data=result,
                    metadata=metadata,
                    output_type=output_type
                )
                
                if output_path:
                    console.print(f"[green]✓[/green] Test output saved: {output_path}")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Save error log
                error_metadata = {
                    'execution_time': execution_time,
                    'success': False
                }
                
                error_path = output_manager.save_error_log(
                    test_name=test_name_actual,
                    error=e,
                    input_data={'args': [str(arg) for arg in args], 'kwargs': kwargs},
                    metadata=error_metadata
                )
                
                if error_path:
                    console.print(f"[red]✗[/red] Error log saved: {error_path}")
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            test_name_actual = test_name or func.__name__
            
            try:
                # Extract input data from function arguments
                input_data = {
                    'args': [str(arg) for arg in args],
                    'kwargs': kwargs
                }
                
                # Run the test
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Save successful result
                metadata = {
                    'execution_time': execution_time,
                    'success': True
                }
                
                output_path = output_manager.save_test_output(
                    test_name=test_name_actual,
                    input_data=input_data,
                    output_data=result,
                    metadata=metadata,
                    output_type=output_type
                )
                
                if output_path:
                    console.print(f"[green]✓[/green] Test output saved: {output_path}")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Save error log
                error_metadata = {
                    'execution_time': execution_time,
                    'success': False
                }
                
                error_path = output_manager.save_error_log(
                    test_name=test_name_actual,
                    error=e,
                    input_data={'args': [str(arg) for arg in args], 'kwargs': kwargs},
                    metadata=error_metadata
                )
                
                if error_path:
                    console.print(f"[red]✗[/red] Error log saved: {error_path}")
                
                raise
        
        # Return async wrapper if function is async, sync wrapper otherwise
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def save_generation_output(test_name: Optional[str] = None):
    """Decorator specifically for generation tests"""
    return save_test_output(test_name, OutputType.GENERATION_DATA)

def save_validation_output(test_name: Optional[str] = None):
    """Decorator specifically for validation tests"""
    return save_test_output(test_name, OutputType.VALIDATION_RESULT)

def save_performance_output(test_name: Optional[str] = None):
    """Decorator specifically for performance tests"""
    return save_test_output(test_name, OutputType.PERFORMANCE_METRICS)

def with_output_summary(func: Callable) -> Callable:
    """Decorator to display output summary after test completion"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        output_manager.display_output_summary()
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        output_manager.display_output_summary()
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Test functions to demonstrate the decorators
@save_test_output("test_basic_function")
def test_basic_function():
    """Test function to demonstrate the decorator"""
    return {"message": "Hello, World!", "status": "success"}


@save_generation_output("test_generation")
def test_generation():
    """Test generation function"""
    return {"generated_data": [1, 2, 3, 4, 5], "count": 5}


@save_validation_output("test_validation")
def test_validation():
    """Test validation function"""
    return {"is_valid": True, "score": 0.95}


if __name__ == "__main__":
    console.print("[bold blue]Testing decorators...[/bold blue]")
    
    # Test the decorators
    try:
        result1 = test_basic_function()
        console.print(f"[green]✓[/green] Basic function result: {result1}")
        
        result2 = test_generation()
        console.print(f"[green]✓[/green] Generation result: {result2}")
        
        result3 = test_validation()
        console.print(f"[green]✓[/green] Validation result: {result3}")
        
        # Display output summary
        output_manager.display_output_summary()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error during testing: {e}") 