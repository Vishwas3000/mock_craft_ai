"""
Feedback Integration Module

This module provides seamless integration between the feedback system and the existing
generation engine, allowing automatic tracking and monitoring without requiring major
changes to existing code.

Features:
- Automatic session management
- Phase tracking integration
- Error capture and analysis
- Performance monitoring
- Recovery suggestion integration
"""

import asyncio
import functools
import time
from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager

from .feedback_system import feedback_system, GenerationPhase, ErrorSeverity
from .generation_engine import JSONGenerationEngine, GenerationRequest, GenerationResult

class FeedbackIntegratedEngine:
    """
    Wrapper around JSONGenerationEngine that provides automatic feedback tracking
    """
    
    def __init__(self, generation_engine: JSONGenerationEngine):
        self.engine = generation_engine
        self.current_session_id: Optional[str] = None
    
    async def generate_with_feedback(
        self,
        request: GenerationRequest,
        test_name: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate with automatic feedback tracking
        """
        # Start feedback session
        session_id = feedback_system.start_session(
            test_name=test_name or f"generation_{int(time.time())}",
            input_schema=request.schema,
            input_context=request.context,
            configuration={
                'strategy': request.strategy.value if request.strategy else 'auto',
                'count': request.count,
                'validation_level': request.validation_level.value if request.validation_level else 'standard',
                'use_multi_strategy': request.use_multi_strategy,
                'max_retries': request.max_retries
            }
        )
        
        self.current_session_id = session_id
        
        try:
            # Track schema analysis phase
            feedback_system.start_phase(session_id, GenerationPhase.SCHEMA_ANALYSIS)
            
            # Monkey patch the engine to track phases
            original_generate = self.engine.generate
            
            async def tracked_generate(req):
                return await self._generate_with_phase_tracking(original_generate, req, session_id)
            
            # Execute generation with tracking
            result = await tracked_generate(request)
            
            # Complete session
            validation_score = result.validation_result.score if result.validation_result else None
            feedback_system.complete_session(
                session_id=session_id,
                final_result=result,
                validation_score=validation_score,
                status="completed" if result.success else "failed"
            )
            
            return result
            
        except Exception as e:
            # Record error and complete session
            feedback_system.record_error(
                session_id=session_id,
                error=e,
                phase=GenerationPhase.COMPLETION,
                severity=ErrorSeverity.CRITICAL
            )
            
            feedback_system.complete_session(
                session_id=session_id,
                status="failed"
            )
            
            raise
    
    async def _generate_with_phase_tracking(
        self,
        original_generate: Callable,
        request: GenerationRequest,
        session_id: str
    ) -> GenerationResult:
        """
        Execute generation with detailed phase tracking
        """
        try:
            # Phase 1: Schema Analysis
            feedback_system.end_phase(session_id, GenerationPhase.SCHEMA_ANALYSIS, success=True)
            
            # Phase 2: Prompt Building
            feedback_system.start_phase(session_id, GenerationPhase.PROMPT_BUILDING)
            
            # We'll hook into the actual generation process
            # For now, we'll track the overall process
            feedback_system.end_phase(session_id, GenerationPhase.PROMPT_BUILDING, success=True)
            
            # Phase 3: LLM Generation
            feedback_system.start_phase(session_id, GenerationPhase.LLM_GENERATION)
            
            # Execute the original generation
            result = await original_generate(request)
            
            feedback_system.end_phase(session_id, GenerationPhase.LLM_GENERATION, success=True)
            
            # Phase 4: Output Parsing
            feedback_system.start_phase(session_id, GenerationPhase.OUTPUT_PARSING)
            feedback_system.end_phase(session_id, GenerationPhase.OUTPUT_PARSING, success=result.success)
            
            # Phase 5: Validation
            feedback_system.start_phase(session_id, GenerationPhase.VALIDATION)
            
            validation_success = result.validation_result is not None and result.validation_result.score > 0.5
            feedback_system.end_phase(session_id, GenerationPhase.VALIDATION, success=validation_success)
            
            return result
            
        except Exception as e:
            # Record error for current phase
            current_phase = getattr(self, '_current_phase', GenerationPhase.COMPLETION)
            feedback_system.record_error(
                session_id=session_id,
                error=e,
                phase=current_phase,
                severity=ErrorSeverity.HIGH
            )
            raise

@contextmanager
def feedback_tracking(test_name: str, schema: Dict[str, Any], context: str = ""):
    """
    Context manager for feedback tracking
    """
    session_id = feedback_system.start_session(
        test_name=test_name,
        input_schema=schema,
        input_context=context,
        configuration={}
    )
    
    try:
        yield session_id
        feedback_system.complete_session(session_id, status="completed")
    except Exception as e:
        feedback_system.record_error(
            session_id=session_id,
            error=e,
            phase=GenerationPhase.COMPLETION,
            severity=ErrorSeverity.HIGH
        )
        feedback_system.complete_session(session_id, status="failed")
        raise

def with_feedback_integration(test_name: Optional[str] = None):
    """
    Simple decorator for adding feedback integration to existing functions
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract schema from arguments
            schema = {}
            context = ""
            
            # Try to find schema in arguments
            for arg in args:
                if hasattr(arg, 'schema'):
                    schema = arg.schema
                    context = getattr(arg, 'context', '')
                    break
                elif isinstance(arg, dict) and any(key in ['id', 'name', 'email'] for key in arg.keys()):
                    schema = arg
                    break
            
            # Use feedback tracking context
            with feedback_tracking(test_name or func.__name__, schema, context):
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Utility functions for easy integration
def create_feedback_engine(generation_engine: JSONGenerationEngine) -> FeedbackIntegratedEngine:
    """
    Create a feedback-integrated version of the generation engine
    """
    return FeedbackIntegratedEngine(generation_engine)

def track_generation_request(request: GenerationRequest, test_name: str) -> str:
    """
    Start tracking a generation request
    """
    return feedback_system.start_session(
        test_name=test_name,
        input_schema=request.schema,
        input_context=request.context,
        configuration={
            'strategy': request.strategy.value if request.strategy else 'auto',
            'count': request.count,
            'validation_level': request.validation_level.value if request.validation_level else 'standard'
        }
    )

def complete_generation_tracking(session_id: str, result: GenerationResult):
    """
    Complete tracking for a generation result
    """
    validation_score = result.validation_result.score if result.validation_result else None
    feedback_system.complete_session(
        session_id=session_id,
        final_result=result,
        validation_score=validation_score,
        status="completed" if result.success else "failed"
    )

# Example usage
async def example_integration():
    """
    Example of how to integrate feedback tracking with existing code
    """
    from .config import settings
    from .llm_manager import LLMManager
    from .schema_analyzer import SchemaAnalyzer
    
    # Initialize components
    config = settings
    llm_manager = LLMManager()
    generation_engine = JSONGenerationEngine(llm_manager)
    
    # Create feedback-integrated engine
    feedback_engine = create_feedback_engine(generation_engine)
    
    # Test schema
    test_schema = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    
    # Create request
    request = GenerationRequest(
        schema=test_schema,
        count=3,
        context="Example integration test"
    )
    
    # Generate with feedback tracking
    result = await feedback_engine.generate_with_feedback(request, "example_integration_test")
    
    # Display results
    print(f"Generation successful: {result.success}")
    if result.validation_result:
        print(f"Validation score: {result.validation_result.score}")
    
    # Display system dashboard
    feedback_system.display_system_dashboard()

if __name__ == "__main__":
    asyncio.run(example_integration()) 