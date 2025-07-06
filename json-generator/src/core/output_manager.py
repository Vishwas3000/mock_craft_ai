"""Output Manager for Test Results and Generation Data"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()

class OutputType(Enum):
    """Types of output data"""
    TEST_RESULT = "test_result"
    GENERATION_DATA = "generation_data"
    VALIDATION_RESULT = "validation_result"
    PERFORMANCE_METRICS = "performance_metrics"
    ERROR_LOG = "error_log"

@dataclass
class OutputMetadata:
    """Metadata for output files"""
    timestamp: str
    test_name: str
    output_type: OutputType
    model_used: Optional[str] = None
    strategy_used: Optional[str] = None
    schema_complexity: Optional[float] = None
    generation_count: Optional[int] = None
    validation_score: Optional[float] = None
    execution_time: Optional[float] = None
    success: Optional[bool] = None
    errors: Optional[List[str]] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

@dataclass
class TestOutput:
    """Complete test output structure"""
    metadata: OutputMetadata
    input_data: Dict[str, Any]
    output_data: Optional[Any] = None
    raw_response: Optional[str] = None
    validation_details: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

class OutputManager:
    """Manages output file generation and organization"""
    
    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.test_output_dir = self.base_output_dir / "test_results"
        self.generation_output_dir = self.base_output_dir / "generation_data"
        self.validation_output_dir = self.base_output_dir / "validation_results"
        self.performance_output_dir = self.base_output_dir / "performance_metrics"
        self.error_output_dir = self.base_output_dir / "error_logs"
        
        # Create all directories
        for directory in [self.test_output_dir, self.generation_output_dir, 
                         self.validation_output_dir, self.performance_output_dir, 
                         self.error_output_dir]:
            directory.mkdir(exist_ok=True)
    
    def save_test_output(
        self,
        test_name: str,
        input_data: Dict[str, Any],
        output_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        output_type: OutputType = OutputType.TEST_RESULT
    ) -> str:
        """Save test output with metadata"""
        
        # Create metadata
        output_metadata = OutputMetadata(
            timestamp=datetime.now().isoformat(),
            test_name=test_name,
            output_type=output_type,
            **metadata or {}
        )
        
        # Create test output structure
        test_output = TestOutput(
            metadata=output_metadata,
            input_data=input_data,
            output_data=output_data
        )
        
        # Generate filename
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_test_name = test_name.replace(" ", "_").replace("/", "_")
        filename = f"{timestamp_str}_{safe_test_name}.json"
        
        # Determine output directory based on type
        if output_type == OutputType.TEST_RESULT:
            output_path = self.test_output_dir / filename
        elif output_type == OutputType.GENERATION_DATA:
            output_path = self.generation_output_dir / filename
        elif output_type == OutputType.VALIDATION_RESULT:
            output_path = self.validation_output_dir / filename
        elif output_type == OutputType.PERFORMANCE_METRICS:
            output_path = self.performance_output_dir / filename
        elif output_type == OutputType.ERROR_LOG:
            output_path = self.error_output_dir / filename
        else:
            output_path = self.test_output_dir / filename
        
        # Save to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(test_output), f, indent=2, default=str)
            
            logger.info(f"Saved test output to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to save test output: {e}")
            return ""
    
    def save_generation_result(
        self,
        test_name: str,
        schema: Dict[str, Any],
        context: str,
        count: int,
        result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save generation result with detailed metadata"""
        
        # Extract metadata from result if available
        result_metadata = {}
        if hasattr(result, 'metadata'):
            result_metadata = result.metadata
        if hasattr(result, 'validation_result') and result.validation_result:
            result_metadata['validation_score'] = result.validation_result.score
            result_metadata['validation_errors'] = result.validation_result.errors
            result_metadata['validation_warnings'] = result.validation_result.warnings
        
        # Combine metadata
        full_metadata = {
            'model_used': result_metadata.get('model_used'),
            'strategy_used': result_metadata.get('strategy_used'),
            'validation_score': result_metadata.get('validation_score'),
            'success': getattr(result, 'success', None),
            'errors': getattr(result, 'errors', []),
            'execution_time': result_metadata.get('execution_time')
        }
        if metadata:
            full_metadata.update(metadata)
        
        # Prepare input data
        input_data = {
            'schema': schema,
            'context': context,
            'count': count,
            'configuration': metadata or {}
        }
        
        return self.save_test_output(
            test_name=test_name,
            input_data=input_data,
            output_data=result.data if hasattr(result, 'data') else result,
            metadata=full_metadata,
            output_type=OutputType.GENERATION_DATA
        )
    
    def save_validation_result(
        self,
        test_name: str,
        validation_result: Any,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save validation result"""
        
        validation_metadata = {
            'validation_score': getattr(validation_result, 'score', None),
            'is_valid': getattr(validation_result, 'is_valid', None),
            'errors': getattr(validation_result, 'errors', []),
            'warnings': getattr(validation_result, 'warnings', [])
        }
        if metadata:
            validation_metadata.update(metadata)
        
        return self.save_test_output(
            test_name=test_name,
            input_data=input_data,
            output_data=validation_result,
            metadata=validation_metadata,
            output_type=OutputType.VALIDATION_RESULT
        )
    
    def save_performance_metrics(
        self,
        test_name: str,
        metrics: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save performance metrics"""
        
        return self.save_test_output(
            test_name=test_name,
            input_data=metrics,
            output_data=metrics,
            metadata=metadata,
            output_type=OutputType.PERFORMANCE_METRICS
        )
    
    def save_error_log(
        self,
        test_name: str,
        error: Exception,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save error log"""
        
        error_metadata = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'success': False
        }
        if metadata:
            error_metadata.update(metadata)
        
        return self.save_test_output(
            test_name=test_name,
            input_data=input_data,
            output_data={'error': str(error), 'traceback': self._get_traceback()},
            metadata=error_metadata,
            output_type=OutputType.ERROR_LOG
        )
    
    def _get_traceback(self) -> str:
        """Get current traceback"""
        import traceback
        return traceback.format_exc()
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of all outputs"""
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_files': 0,
            'test_results': 0,
            'generation_data': 0,
            'validation_results': 0,
            'performance_metrics': 0,
            'error_logs': 0,
            'recent_outputs': []
        }
        
        # Count files in each directory
        for output_type, directory in [
            ('test_results', self.test_output_dir),
            ('generation_data', self.generation_output_dir),
            ('validation_results', self.validation_output_dir),
            ('performance_metrics', self.performance_output_dir),
            ('error_logs', self.error_output_dir)
        ]:
            files = list(directory.glob('*.json'))
            summary[f'{output_type.replace("_", "")}'] = len(files)
            summary['total_files'] += len(files)
            
            # Get recent files (last 5)
            recent_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            for file_path in recent_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        summary['recent_outputs'].append({
                            'file': file_path.name,
                            'type': output_type,
                            'test_name': data.get('metadata', {}).get('test_name', 'Unknown'),
                            'timestamp': data.get('metadata', {}).get('timestamp', 'Unknown'),
                            'success': data.get('metadata', {}).get('success', 'Unknown')
                        })
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        # Save summary report
        summary_path = self.base_output_dir / f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return str(summary_path)
    
    def display_output_summary(self):
        """Display a summary of outputs in the console"""
        
        table = Table(title="Output Summary")
        table.add_column("Output Type", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Directory", style="green")
        
        for output_type, directory in [
            ("Test Results", self.test_output_dir),
            ("Generation Data", self.generation_output_dir),
            ("Validation Results", self.validation_output_dir),
            ("Performance Metrics", self.performance_output_dir),
            ("Error Logs", self.error_output_dir)
        ]:
            count = len(list(directory.glob('*.json')))
            table.add_row(output_type, str(count), str(directory.relative_to(self.base_output_dir)))
        
        console.print(table)
        console.print(f"\n[bold]Output Base Directory:[/bold] {self.base_output_dir.absolute()}")

# Global output manager instance
output_manager = OutputManager() 