"""
Scripts Package

Organized collection of scripts for the JSON Generator project.

Structure:
- validation/: System validation and setup verification scripts
- demos/: Interactive demonstration and showcase scripts  
- testing/: Specialized testing and component verification scripts
- utilities/: Development and maintenance utility scripts

Usage:
    # Run validation scripts
    python scripts/validation/validate_llm_integration.py
    
    # Run demos
    python scripts/demos/quick_start.py
    
    # Run testing scripts
    python scripts/testing/test_feedback_system.py
"""

# Import submodules for easy access
from . import validation
from . import demos
from . import testing
from . import utilities

__all__ = ['validation', 'demos', 'testing', 'utilities'] 