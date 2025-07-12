"""
Utilities Package

This package provides organized utilities for the JSON Generator project.

Structure:
- output/: Output management utilities
- testing/: Testing decorators and utilities  
- processing/: Data processing utilities
- common/: Common shared utilities
"""

# Import all utility modules for easy access
from . import output
from . import testing  
from . import processing
from . import common

# Import commonly used utilities directly
from .output import OutputManager, OutputType
from .testing import (
    # Basic decorators
    save_test_output,
    save_generation_output,
    save_validation_output,
    save_performance_output,
    with_output_summary,
    
    # Enhanced decorators
    comprehensive_test_tracking,
    generation_test_tracking,
    performance_test_tracking,
    validation_test_tracking,
    with_comprehensive_analysis
)
from .processing import (
    UUIDProcessor,
    UUIDFormat,
    UUIDContext,
    UUIDConfig,
    process_uuids,
    replace_uuid_placeholders,
    get_uuid_instructions,
    validate_uuids,
    detect_uuid_fields
)

__all__ = [
    # Modules
    'output',
    'testing',
    'processing',
    'common',
    
    # Output utilities
    'OutputManager',
    'OutputType',
    
    # Testing decorators - Basic
    'save_test_output',
    'save_generation_output',
    'save_validation_output',
    'save_performance_output',
    'with_output_summary',
    
    # Testing decorators - Enhanced
    'comprehensive_test_tracking',
    'generation_test_tracking',
    'performance_test_tracking',
    'validation_test_tracking',
    'with_comprehensive_analysis',
    
    # Processing utilities
    'UUIDProcessor',
    'UUIDFormat',
    'UUIDContext',
    'UUIDConfig',
    'process_uuids',
    'replace_uuid_placeholders',
    'get_uuid_instructions',
    'validate_uuids',
    'detect_uuid_fields'
]
