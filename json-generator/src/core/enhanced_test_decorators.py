"""
Enhanced Test Decorators with Comprehensive Feedback Integration

This module provides decorators that automatically integrate with the feedback system
to track test execution, monitor performance, detect errors, and provide intelligent
recovery suggestions.

Features:
- Automatic session management
- Phase-by-phase tracking
- Error detection and categorization
- Recovery suggestion integration
- Performance monitoring
- Comprehensive reporting
"""

import functools
import asyncio
import time
import sys
from typing import Callable, Any, Dict, Optional, List
from rich.console import Console

try:
    from .feedback_system import feedback_system, GenerationPhase, ErrorSeverity
    from .output_manager import output_manager
except ImportError:
    # Fallback for direct execution
    sys.path.append('/Users/sudeepsharma/Documents/GitHub/mock_craft_ai/json-generator')
    from src.core.feedback_system import feedback_system, GenerationPhase, ErrorSeverity
    from src.core.output_manager import output_manager

console = Console()

def with_feedback_tracking(
    test_name: Optional[str] = None,
    track_phases: bool = True,
    auto_recovery: bool = False
):
    """
    Decorator to add comprehensive feedback tracking to test functions
    
    Args:
        test_name: Name for the test (defaults to function name)
        track_phases: Whether to automatically track generation phases
        auto_recovery: Whether to attempt automatic recovery on errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            test_name_actual = test_name or func.__name__
            session_id = None
            
            try:
                # Extract input data for tracking
                input_data = _extract_input_data(args, kwargs)
                
                # Start feedback session
                session_id = feedback_system.start_session(
                    test_name=test_name_actual,
                    input_schema=input_data.get('schema', {}),
                    input_context=input_data.get('context', ''),
                    configuration=input_data.get('configuration', {})
                )
                
                if track_phases:
                    feedback_system.start_phase(session_id, GenerationPhase.INITIALIZATION)
                
                # Execute the test function
                result = await func(*args, **kwargs)
                
                if track_phases:
                    feedback_system.end_phase(session_id, GenerationPhase.INITIALIZATION, success=True)
                    feedback_system.start_phase(session_id, GenerationPhase.COMPLETION)
                    feedback_system.end_phase(session_id, GenerationPhase.COMPLETION, success=True)
                
                # Extract validation score if available
                validation_score = _extract_validation_score(result)
                
                # Complete session successfully
                feedback_system.complete_session(
                    session_id=session_id,
                    final_result=result,
                    validation_score=validation_score,
                    status="completed"
                )
                
                return result
                
            except Exception as e:
                if session_id:
                    # Record the error
                    recovery_suggestions = feedback_system.record_error(
                        session_id=session_id,
                        error=e,
                        phase=GenerationPhase.COMPLETION,
                        context={'function': func.__name__, 'args': str(args)[:200]},
                        severity=ErrorSeverity.HIGH
                    )
                    
                    # Attempt auto-recovery if enabled
                    if auto_recovery and recovery_suggestions:
                        console.print("[yellow]🔧 Attempting automatic recovery...[/yellow]")
                        # This would integrate with the actual generation system
                        # For now, we just log the attempt
                        feedback_system.record_recovery_action(
                            session_id=session_id,
                            action=recovery_suggestions[0]['action'],
                            description=recovery_suggestions[0]['description'],
                            success=False  # Would be determined by actual recovery attempt
                        )
                    
                    # Complete session with error
                    feedback_system.complete_session(
                        session_id=session_id,
                        status="failed"
                    )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            test_name_actual = test_name or func.__name__
            session_id = None
            
            try:
                # Extract input data for tracking
                input_data = _extract_input_data(args, kwargs)
                
                # Start feedback session
                session_id = feedback_system.start_session(
                    test_name=test_name_actual,
                    input_schema=input_data.get('schema', {}),
                    input_context=input_data.get('context', ''),
                    configuration=input_data.get('configuration', {})
                )
                
                if track_phases:
                    feedback_system.start_phase(session_id, GenerationPhase.INITIALIZATION)
                
                # Execute the test function
                result = func(*args, **kwargs)
                
                if track_phases:
                    feedback_system.end_phase(session_id, GenerationPhase.INITIALIZATION, success=True)
                    feedback_system.start_phase(session_id, GenerationPhase.COMPLETION)
                    feedback_system.end_phase(session_id, GenerationPhase.COMPLETION, success=True)
                
                # Extract validation score if available
                validation_score = _extract_validation_score(result)
                
                # Complete session successfully
                feedback_system.complete_session(
                    session_id=session_id,
                    final_result=result,
                    validation_score=validation_score,
                    status="completed"
                )
                
                return result
                
            except Exception as e:
                if session_id:
                    # Record the error
                    recovery_suggestions = feedback_system.record_error(
                        session_id=session_id,
                        error=e,
                        phase=GenerationPhase.COMPLETION,
                        context={'function': func.__name__, 'args': str(args)[:200]},
                        severity=ErrorSeverity.HIGH
                    )
                    
                    # Complete session with error
                    feedback_system.complete_session(
                        session_id=session_id,
                        status="failed"
                    )
                
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def with_generation_tracking(test_name: Optional[str] = None):
    """
    Decorator specifically for JSON generation tests with detailed phase tracking
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            test_name_actual = test_name or func.__name__
            session_id = None
            
            try:
                # Extract input data
                input_data = _extract_input_data(args, kwargs)
                
                # Start feedback session
                session_id = feedback_system.start_session(
                    test_name=test_name_actual,
                    input_schema=input_data.get('schema', {}),
                    input_context=input_data.get('context', ''),
                    configuration=input_data.get('configuration', {})
                )
                
                # Track initialization phase
                feedback_system.start_phase(session_id, GenerationPhase.INITIALIZATION)
                
                # Execute the test with enhanced tracking
                result = await _execute_with_generation_tracking(func, session_id, *args, **kwargs)
                
                feedback_system.end_phase(session_id, GenerationPhase.INITIALIZATION, success=True)
                
                # Extract validation score and complete session
                validation_score = _extract_validation_score(result)
                feedback_system.complete_session(
                    session_id=session_id,
                    final_result=result,
                    validation_score=validation_score,
                    status="completed"
                )
                
                return result
                
            except Exception as e:
                if session_id:
                    feedback_system.record_error(
                        session_id=session_id,
                        error=e,
                        phase=GenerationPhase.COMPLETION,
                        severity=ErrorSeverity.CRITICAL
                    )
                    feedback_system.complete_session(session_id, status="failed")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar implementation for sync functions
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def with_performance_monitoring(test_name: Optional[str] = None):
    """
    Decorator for detailed performance monitoring
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            test_name_actual = test_name or func.__name__
            
            # Start performance tracking
            session_id = feedback_system.start_session(
                test_name=f"perf_{test_name_actual}",
                input_schema={},
                input_context="performance_test",
                configuration={'performance_monitoring': True}
            )
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record performance metrics
                feedback_system.complete_session(
                    session_id=session_id,
                    final_result={'execution_time': execution_time},
                    status="completed"
                )
                
                console.print(f"[green]⏱️ Performance: {test_name_actual} completed in {execution_time:.2f}s[/green]")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                feedback_system.record_error(
                    session_id=session_id,
                    error=e,
                    phase=GenerationPhase.COMPLETION,
                    context={'execution_time': execution_time}
                )
                feedback_system.complete_session(session_id, status="failed")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def with_validation_tracking(test_name: Optional[str] = None):
    """
    Decorator for detailed validation tracking
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            test_name_actual = test_name or func.__name__
            
            session_id = feedback_system.start_session(
                test_name=f"validation_{test_name_actual}",
                input_schema={},
                input_context="validation_test",
                configuration={'validation_tracking': True}
            )
            
            try:
                feedback_system.start_phase(session_id, GenerationPhase.VALIDATION)
                result = await func(*args, **kwargs)
                feedback_system.end_phase(session_id, GenerationPhase.VALIDATION, success=True)
                
                # Extract validation details
                validation_score = _extract_validation_score(result)
                validation_errors = _extract_validation_errors(result)
                
                if validation_errors:
                    for error_msg in validation_errors:
                        feedback_system.record_error(
                            session_id=session_id,
                            error=Exception(error_msg),
                            phase=GenerationPhase.VALIDATION,
                            severity=ErrorSeverity.MEDIUM
                        )
                
                feedback_system.complete_session(
                    session_id=session_id,
                    final_result=result,
                    validation_score=validation_score,
                    status="completed"
                )
                
                return result
                
            except Exception as e:
                feedback_system.record_error(
                    session_id=session_id,
                    error=e,
                    phase=GenerationPhase.VALIDATION,
                    severity=ErrorSeverity.HIGH
                )
                feedback_system.complete_session(session_id, status="failed")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def with_comprehensive_analysis(test_name: Optional[str] = None):
    """
    Decorator that provides comprehensive analysis and reporting
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            console.print(f"\n[bold blue]🔍 Starting Comprehensive Analysis: {test_name or func.__name__}[/bold blue]")
            
            try:
                # Execute with all tracking enabled
                result = await func(*args, **kwargs)
                
                # Display system dashboard after completion
                console.print(f"\n[bold green]📊 Analysis Complete for: {test_name or func.__name__}[/bold green]")
                feedback_system.display_system_dashboard()
                
                return result
                
            except Exception as e:
                console.print(f"\n[bold red]❌ Analysis Failed for: {test_name or func.__name__}[/bold red]")
                feedback_system.display_system_dashboard()
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

async def _execute_with_generation_tracking(func, session_id, *args, **kwargs):
    """Execute function with detailed generation phase tracking"""
    # This would be enhanced to track specific generation phases
    # For now, it's a placeholder that calls the original function
    return await func(*args, **kwargs)

def _extract_input_data(args, kwargs) -> Dict[str, Any]:
    """Extract relevant input data from function arguments"""
    input_data = {}
    
    # Try to extract schema from common argument patterns
    if args:
        for arg in args:
            if isinstance(arg, dict):
                if 'schema' in str(arg).lower() or any(key in ['id', 'name', 'email'] for key in arg.keys()):
                    input_data['schema'] = arg
                    break
    
    # Extract from kwargs
    input_data.update({
        'schema': kwargs.get('schema', kwargs.get('input_schema', {})),
        'context': kwargs.get('context', kwargs.get('input_context', '')),
        'configuration': {k: v for k, v in kwargs.items() if k not in ['schema', 'context']}
    })
    
    return input_data

def _extract_validation_score(result) -> Optional[float]:
    """Extract validation score from result"""
    if hasattr(result, 'validation_result') and hasattr(result.validation_result, 'score'):
        return result.validation_result.score
    elif isinstance(result, dict) and 'validation_score' in result:
        return result['validation_score']
    elif hasattr(result, 'score'):
        return result.score
    return None

def _extract_validation_errors(result) -> List[str]:
    """Extract validation errors from result"""
    errors = []
    
    if hasattr(result, 'validation_result') and hasattr(result.validation_result, 'errors'):
        errors.extend(result.validation_result.errors)
    elif hasattr(result, 'errors'):
        errors.extend(result.errors)
    elif isinstance(result, dict) and 'errors' in result:
        errors.extend(result['errors'])
    
    return errors

# Convenience decorators combining multiple features
def comprehensive_test_tracking(test_name: Optional[str] = None):
    """
    Comprehensive decorator combining all tracking features
    """
    return with_feedback_tracking(test_name=test_name, track_phases=True, auto_recovery=True)

def generation_test_tracking(test_name: Optional[str] = None):
    """
    Decorator specifically for generation tests
    """
    return with_generation_tracking(test_name=test_name)

def performance_test_tracking(test_name: Optional[str] = None):
    """
    Decorator for performance-focused tests
    """
    return with_performance_monitoring(test_name=test_name)

def validation_test_tracking(test_name: Optional[str] = None):
    """
    Decorator for validation-focused tests
    """
    return with_validation_tracking(test_name=test_name)

# Example usage functions
@comprehensive_test_tracking("example_comprehensive_test")
async def example_comprehensive_test():
    """Example of comprehensive test tracking"""
    await asyncio.sleep(1)  # Simulate work
    return {"status": "success", "validation_score": 0.95}

@generation_test_tracking("example_generation_test")
async def example_generation_test():
    """Example of generation test tracking"""
    await asyncio.sleep(2)  # Simulate generation
    return {"generated_data": [{"id": "123", "name": "test"}], "validation_score": 0.8}

@performance_test_tracking("example_performance_test")
async def example_performance_test():
    """Example of performance test tracking"""
    await asyncio.sleep(0.5)  # Simulate fast operation
    return {"performance_metrics": {"latency": 0.5}}

if __name__ == "__main__":
    # Example usage
    async def main():
        await example_comprehensive_test()
        await example_generation_test()
        await example_performance_test()
        
        # Display final dashboard
        feedback_system.display_system_dashboard()
    
    asyncio.run(main()) 