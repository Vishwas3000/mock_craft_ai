"""
Comprehensive Feedback System for JSON Generation Pipeline

This module provides real-time monitoring, error detection, pattern analysis,
and intelligent recovery suggestions for the entire JSON generation process.

Features:
- Multi-level error detection and classification
- Phase-by-phase monitoring
- Intelligent error analysis and root cause detection
- Automated feedback and recovery systems
- Performance monitoring and optimization
- Learning system for continuous improvement
"""

import json
import time
import traceback
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

logger = logging.getLogger(__name__)
console = Console()

class ErrorCategory(Enum):
    """Error categories for classification"""
    LLM_ERROR = "llm_error"
    VALIDATION_ERROR = "validation_error"
    PARSING_ERROR = "parsing_error"
    SCHEMA_ERROR = "schema_error"
    TIMEOUT_ERROR = "timeout_error"
    CONFIGURATION_ERROR = "configuration_error"
    PARTIAL_SUCCESS = "partial_success"
    DATA_QUALITY_ERROR = "data_quality_error"
    NETWORK_ERROR = "network_error"
    RATE_LIMIT_ERROR = "rate_limit_error"

class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"    # Complete failure
    HIGH = "high"           # Major issues affecting quality
    MEDIUM = "medium"       # Minor issues, partial success
    LOW = "low"            # Warnings, still usable
    INFO = "info"          # Informational messages

class GenerationPhase(Enum):
    """Phases of the generation process"""
    INITIALIZATION = "initialization"
    SCHEMA_ANALYSIS = "schema_analysis"
    PROMPT_BUILDING = "prompt_building"
    LLM_GENERATION = "llm_generation"
    OUTPUT_PARSING = "output_parsing"
    VALIDATION = "validation"
    POST_PROCESSING = "post_processing"
    RETRY = "retry"
    COMPLETION = "completion"

class RecoveryAction(Enum):
    """Types of recovery actions"""
    RETRY_SAME_STRATEGY = "retry_same_strategy"
    SWITCH_STRATEGY = "switch_strategy"
    ADJUST_PARAMETERS = "adjust_parameters"
    SIMPLIFY_SCHEMA = "simplify_schema"
    USE_FALLBACK_MODEL = "use_fallback_model"
    REDUCE_COMPLEXITY = "reduce_complexity"
    MANUAL_INTERVENTION = "manual_intervention"

@dataclass
class ErrorDetails:
    """Detailed error information"""
    error_id: str
    timestamp: str
    phase: GenerationPhase
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception_type: str
    context: Dict[str, Any]
    stack_trace: str
    suggested_fixes: List[str]
    recovery_actions: List[RecoveryAction]
    related_errors: List[str] = field(default_factory=list)
    resolution_status: str = "pending"  # pending, resolved, ignored

@dataclass
class PhaseMetrics:
    """Metrics for a single phase"""
    phase: GenerationPhase
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = False
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationSession:
    """Tracking information for a single generation session"""
    session_id: str
    test_name: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"  # running, completed, failed, cancelled
    
    # Input information
    input_schema: Dict[str, Any] = field(default_factory=dict)
    input_context: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Phase tracking
    phases: List[PhaseMetrics] = field(default_factory=list)
    current_phase: Optional[GenerationPhase] = None
    
    # Error tracking
    errors: List[ErrorDetails] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Performance metrics
    total_duration: float = 0.0
    retry_count: int = 0
    strategy_switches: int = 0
    
    # Results
    final_result: Optional[Any] = None
    validation_score: Optional[float] = None
    success_rate: float = 0.0
    
    # Recovery actions taken
    recovery_actions: List[Dict[str, Any]] = field(default_factory=list)

class ErrorPatternDetector:
    """Detects patterns in errors for intelligent analysis"""
    
    def __init__(self):
        self.error_history: deque = deque(maxlen=1000)  # Keep last 1000 errors
        self.pattern_cache: Dict[str, List[str]] = {}
    
    def add_error(self, error: ErrorDetails):
        """Add error to history for pattern analysis"""
        self.error_history.append(error)
        self._update_patterns()
    
    def _update_patterns(self):
        """Update detected patterns"""
        if len(self.error_history) < 5:
            return
        
        # Analyze recent errors for patterns
        recent_errors = list(self.error_history)[-10:]
        
        # Pattern 1: Recurring error types
        error_types = [e.category.value for e in recent_errors]
        if len(set(error_types)) == 1 and len(error_types) >= 3:
            pattern_key = f"recurring_{error_types[0]}"
            if pattern_key not in self.pattern_cache:
                self.pattern_cache[pattern_key] = []
            self.pattern_cache[pattern_key].append(
                f"Recurring {error_types[0]} errors detected"
            )
        
        # Pattern 2: Phase-specific failures
        phase_errors = defaultdict(int)
        for error in recent_errors:
            phase_errors[error.phase.value] += 1
        
        for phase, count in phase_errors.items():
            if count >= 3:
                pattern_key = f"phase_failure_{phase}"
                self.pattern_cache[pattern_key] = [
                    f"Multiple failures in {phase} phase"
                ]
    
    def get_patterns(self) -> Dict[str, List[str]]:
        """Get detected error patterns"""
        return self.pattern_cache.copy()

class PerformanceMonitor:
    """Monitors performance metrics and trends"""
    
    def __init__(self):
        self.session_history: List[GenerationSession] = []
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
    
    def add_session(self, session: GenerationSession):
        """Add completed session for analysis"""
        self.session_history.append(session)
        self._update_trends(session)
    
    def _update_trends(self, session: GenerationSession):
        """Update performance trends"""
        self.performance_trends['duration'].append(session.total_duration)
        self.performance_trends['retry_count'].append(session.retry_count)
        self.performance_trends['success_rate'].append(session.success_rate)
        
        if session.validation_score is not None:
            self.performance_trends['validation_score'].append(session.validation_score)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.session_history:
            return {}
        
        recent_sessions = self.session_history[-10:]  # Last 10 sessions
        
        return {
            'total_sessions': len(self.session_history),
            'recent_avg_duration': sum(s.total_duration for s in recent_sessions) / len(recent_sessions),
            'recent_avg_retries': sum(s.retry_count for s in recent_sessions) / len(recent_sessions),
            'recent_success_rate': sum(1 for s in recent_sessions if s.status == 'completed') / len(recent_sessions),
            'trends': {
                key: {
                    'current': values[-1] if values else 0,
                    'average': sum(values) / len(values) if values else 0,
                    'trend': 'improving' if len(values) >= 2 and values[-1] > values[-2] else 'declining'
                }
                for key, values in self.performance_trends.items()
            }
        }

class RecoverySystem:
    """Intelligent recovery system with automated suggestions"""
    
    def __init__(self):
        self.recovery_strategies = {
            ErrorCategory.LLM_ERROR: self._handle_llm_error,
            ErrorCategory.VALIDATION_ERROR: self._handle_validation_error,
            ErrorCategory.PARSING_ERROR: self._handle_parsing_error,
            ErrorCategory.TIMEOUT_ERROR: self._handle_timeout_error,
            ErrorCategory.CONFIGURATION_ERROR: self._handle_config_error,
        }
    
    def suggest_recovery(self, error: ErrorDetails, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest recovery actions for an error"""
        handler = self.recovery_strategies.get(error.category)
        if handler:
            return handler(error, context)
        return self._default_recovery(error, context)
    
    def _handle_llm_error(self, error: ErrorDetails, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LLM-related errors"""
        suggestions = []
        
        if "api" in error.message.lower():
            suggestions.append({
                'action': RecoveryAction.USE_FALLBACK_MODEL,
                'description': 'Switch to a different LLM provider',
                'priority': 'high',
                'estimated_success': 0.8
            })
        
        if "timeout" in error.message.lower():
            suggestions.append({
                'action': RecoveryAction.ADJUST_PARAMETERS,
                'description': 'Reduce max_tokens and increase timeout',
                'priority': 'medium',
                'estimated_success': 0.7
            })
        
        suggestions.append({
            'action': RecoveryAction.RETRY_SAME_STRATEGY,
            'description': 'Retry with same configuration after brief delay',
            'priority': 'low',
            'estimated_success': 0.5
        })
        
        return suggestions
    
    def _handle_validation_error(self, error: ErrorDetails, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle validation errors"""
        suggestions = []
        
        if "uuid" in error.message.lower() or "length" in error.message.lower():
            suggestions.append({
                'action': RecoveryAction.ADJUST_PARAMETERS,
                'description': 'Use more lenient validation settings',
                'priority': 'high',
                'estimated_success': 0.9
            })
        
        if "missing" in error.message.lower():
            suggestions.append({
                'action': RecoveryAction.SWITCH_STRATEGY,
                'description': 'Switch to structured prompt strategy',
                'priority': 'high',
                'estimated_success': 0.8
            })
        
        suggestions.append({
            'action': RecoveryAction.REDUCE_COMPLEXITY,
            'description': 'Generate fewer fields at once',
            'priority': 'medium',
            'estimated_success': 0.7
        })
        
        return suggestions
    
    def _handle_parsing_error(self, error: ErrorDetails, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle parsing errors"""
        return [{
            'action': RecoveryAction.SWITCH_STRATEGY,
            'description': 'Use more explicit JSON formatting instructions',
            'priority': 'high',
            'estimated_success': 0.8
        }, {
            'action': RecoveryAction.ADJUST_PARAMETERS,
            'description': 'Lower temperature for more consistent output',
            'priority': 'medium',
            'estimated_success': 0.7
        }]
    
    def _handle_timeout_error(self, error: ErrorDetails, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle timeout errors"""
        return [{
            'action': RecoveryAction.REDUCE_COMPLEXITY,
            'description': 'Reduce generation count or schema complexity',
            'priority': 'high',
            'estimated_success': 0.9
        }, {
            'action': RecoveryAction.USE_FALLBACK_MODEL,
            'description': 'Switch to a faster model',
            'priority': 'medium',
            'estimated_success': 0.7
        }]
    
    def _handle_config_error(self, error: ErrorDetails, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle configuration errors"""
        return [{
            'action': RecoveryAction.MANUAL_INTERVENTION,
            'description': 'Review and fix configuration settings',
            'priority': 'critical',
            'estimated_success': 0.95
        }]
    
    def _default_recovery(self, error: ErrorDetails, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Default recovery suggestions"""
        return [{
            'action': RecoveryAction.RETRY_SAME_STRATEGY,
            'description': 'Retry with current configuration',
            'priority': 'low',
            'estimated_success': 0.3
        }]

class FeedbackSystem:
    """Main feedback system coordinating all components"""
    
    def __init__(self, output_dir: str = "outputs/feedback"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.pattern_detector = ErrorPatternDetector()
        self.performance_monitor = PerformanceMonitor()
        self.recovery_system = RecoverySystem()
        
        # Active sessions
        self.active_sessions: Dict[str, GenerationSession] = {}
        self.session_history: List[GenerationSession] = []
        
        # Global metrics
        self.global_metrics = {
            'total_sessions': 0,
            'total_errors': 0,
            'total_recoveries': 0,
            'success_rate': 0.0
        }
    
    def start_session(
        self,
        test_name: str,
        input_schema: Dict[str, Any],
        input_context: str,
        configuration: Dict[str, Any]
    ) -> str:
        """Start a new generation session"""
        session_id = str(uuid.uuid4())
        
        session = GenerationSession(
            session_id=session_id,
            test_name=test_name,
            start_time=datetime.now().isoformat(),
            input_schema=input_schema,
            input_context=input_context,
            configuration=configuration
        )
        
        self.active_sessions[session_id] = session
        self.global_metrics['total_sessions'] += 1
        
        console.print(f"[green]Started feedback tracking for session: {test_name}[/green]")
        console.print(f"[dim]Session ID: {session_id}[/dim]")
        
        return session_id
    
    def start_phase(self, session_id: str, phase: GenerationPhase, metadata: Dict[str, Any] = None):
        """Start tracking a generation phase"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found")
            return
        
        session = self.active_sessions[session_id]
        session.current_phase = phase
        
        phase_metrics = PhaseMetrics(
            phase=phase,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        session.phases.append(phase_metrics)
        console.print(f"[cyan]📍 Started phase: {phase.value}[/cyan]")
    
    def end_phase(
        self,
        session_id: str,
        phase: GenerationPhase,
        success: bool = True,
        result: Any = None,
        warnings: List[str] = None
    ):
        """End tracking a generation phase"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # Find the current phase metrics
        for phase_metrics in reversed(session.phases):
            if phase_metrics.phase == phase and phase_metrics.end_time is None:
                phase_metrics.end_time = time.time()
                phase_metrics.duration = phase_metrics.end_time - phase_metrics.start_time
                phase_metrics.success = success
                phase_metrics.warnings = warnings or []
                
                if result is not None:
                    phase_metrics.metadata['result'] = str(result)[:200]  # Truncate for storage
                
                status_icon = "✅" if success else "❌"
                console.print(f"[cyan]{status_icon} Completed phase: {phase.value} ({phase_metrics.duration:.2f}s)[/cyan]")
                break
        
        session.current_phase = None
    
    def record_error(
        self,
        session_id: str,
        error: Exception,
        phase: GenerationPhase,
        context: Dict[str, Any] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH
    ) -> List[Dict[str, Any]]:
        """Record an error and get recovery suggestions"""
        if session_id not in self.active_sessions:
            return []
        
        session = self.active_sessions[session_id]
        
        # Categorize error
        category = self._categorize_error(error)
        
        # Create error details
        error_details = ErrorDetails(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            phase=phase,
            category=category,
            severity=severity,
            message=str(error),
            exception_type=type(error).__name__,
            context=context or {},
            stack_trace=traceback.format_exc(),
            suggested_fixes=[],
            recovery_actions=[]
        )
        
        # Add to session and global tracking
        session.errors.append(error_details)
        self.global_metrics['total_errors'] += 1
        self.pattern_detector.add_error(error_details)
        
        # Get recovery suggestions
        recovery_suggestions = self.recovery_system.suggest_recovery(error_details, context or {})
        error_details.suggested_fixes = [s['description'] for s in recovery_suggestions]
        error_details.recovery_actions = [RecoveryAction(s['action']) for s in recovery_suggestions]
        
        # Display error feedback
        self._display_error_feedback(error_details, recovery_suggestions)
        
        return recovery_suggestions
    
    def record_recovery_action(
        self,
        session_id: str,
        action: RecoveryAction,
        description: str,
        success: bool
    ):
        """Record a recovery action taken"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        recovery_record = {
            'action': action.value,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'success': success
        }
        
        session.recovery_actions.append(recovery_record)
        
        if success:
            self.global_metrics['total_recoveries'] += 1
            console.print(f"[green]🔧 Recovery successful: {description}[/green]")
        else:
            console.print(f"[yellow]⚠️ Recovery failed: {description}[/yellow]")
    
    def complete_session(
        self,
        session_id: str,
        final_result: Any = None,
        validation_score: float = None,
        status: str = "completed"
    ):
        """Complete a generation session"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now().isoformat()
        session.status = status
        session.final_result = final_result
        session.validation_score = validation_score
        
        # Calculate metrics
        start_time = datetime.fromisoformat(session.start_time)
        end_time = datetime.fromisoformat(session.end_time)
        session.total_duration = (end_time - start_time).total_seconds()
        
        # Calculate success rate
        successful_phases = sum(1 for p in session.phases if p.success)
        session.success_rate = successful_phases / max(len(session.phases), 1)
        
        # Update global metrics
        if status == "completed":
            successful_sessions = sum(1 for s in self.session_history if s.status == "completed")
            self.global_metrics['success_rate'] = (successful_sessions + 1) / self.global_metrics['total_sessions']
        
        # Add to history and remove from active
        self.session_history.append(session)
        self.performance_monitor.add_session(session)
        del self.active_sessions[session_id]
        
        # Save session data
        self._save_session_data(session)
        
        # Display completion feedback
        self._display_completion_feedback(session)
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize an error"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        if "llm" in error_message or "api" in error_message or "openai" in error_message:
            return ErrorCategory.LLM_ERROR
        elif "validation" in error_message or "constraint" in error_message:
            return ErrorCategory.VALIDATION_ERROR
        elif "json" in error_message or "parse" in error_message:
            return ErrorCategory.PARSING_ERROR
        elif "timeout" in error_message:
            return ErrorCategory.TIMEOUT_ERROR
        elif "config" in error_message or "setting" in error_message:
            return ErrorCategory.CONFIGURATION_ERROR
        elif "network" in error_message or "connection" in error_message:
            return ErrorCategory.NETWORK_ERROR
        elif "rate" in error_message and "limit" in error_message:
            return ErrorCategory.RATE_LIMIT_ERROR
        else:
            return ErrorCategory.LLM_ERROR  # Default fallback
    
    def _display_error_feedback(self, error: ErrorDetails, recovery_suggestions: List[Dict[str, Any]]):
        """Display error feedback to user"""
        error_panel = Panel(
            f"[red]Error in {error.phase.value}:[/red]\n"
            f"[yellow]Category:[/yellow] {error.category.value}\n"
            f"[yellow]Severity:[/yellow] {error.severity.value}\n"
            f"[yellow]Message:[/yellow] {error.message}\n\n"
            f"[cyan]Recovery Suggestions:[/cyan]\n" +
            "\n".join(f"• {s['description']} (Priority: {s['priority']})" for s in recovery_suggestions),
            title="🚨 Error Detected",
            border_style="red"
        )
        console.print(error_panel)
    
    def _display_completion_feedback(self, session: GenerationSession):
        """Display session completion feedback"""
        status_color = "green" if session.status == "completed" else "red"
        status_icon = "✅" if session.status == "completed" else "❌"
        
        feedback_text = f"[{status_color}]{status_icon} Session: {session.test_name}[/{status_color}]\n"
        feedback_text += f"[yellow]Duration:[/yellow] {session.total_duration:.2f}s\n"
        feedback_text += f"[yellow]Phases:[/yellow] {len(session.phases)} completed\n"
        feedback_text += f"[yellow]Errors:[/yellow] {len(session.errors)}\n"
        feedback_text += f"[yellow]Success Rate:[/yellow] {session.success_rate:.1%}\n"
        
        if session.validation_score is not None:
            score_color = "green" if session.validation_score > 0.8 else "yellow" if session.validation_score > 0.5 else "red"
            feedback_text += f"[yellow]Validation Score:[/yellow] [{score_color}]{session.validation_score:.2f}[/{score_color}]\n"
        
        if session.recovery_actions:
            feedback_text += f"[yellow]Recovery Actions:[/yellow] {len(session.recovery_actions)}\n"
        
        completion_panel = Panel(
            feedback_text,
            title="📊 Session Complete",
            border_style=status_color
        )
        console.print(completion_panel)
    
    def _save_session_data(self, session: GenerationSession):
        """Save session data to file"""
        session_file = self.output_dir / f"session_{session.session_id}.json"
        
        with open(session_file, 'w') as f:
            json.dump(asdict(session), f, indent=2, default=str)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        patterns = self.pattern_detector.get_patterns()
        performance = self.performance_monitor.get_performance_summary()
        
        return {
            'global_metrics': self.global_metrics,
            'active_sessions': len(self.active_sessions),
            'detected_patterns': patterns,
            'performance_summary': performance,
            'health_status': self._calculate_health_status()
        }
    
    def _calculate_health_status(self) -> str:
        """Calculate overall system health status"""
        if self.global_metrics['success_rate'] > 0.8:
            return "healthy"
        elif self.global_metrics['success_rate'] > 0.5:
            return "warning"
        else:
            return "critical"
    
    def display_system_dashboard(self):
        """Display comprehensive system dashboard"""
        health = self.get_system_health()
        
        # System Health Table
        health_table = Table(title="🏥 System Health Dashboard")
        health_table.add_column("Metric", style="cyan")
        health_table.add_column("Value", style="magenta")
        health_table.add_column("Status", style="green")
        
        health_status = health['health_status']
        status_color = "green" if health_status == "healthy" else "yellow" if health_status == "warning" else "red"
        
        health_table.add_row("Overall Health", health_status.title(), f"[{status_color}]●[/{status_color}]")
        health_table.add_row("Total Sessions", str(health['global_metrics']['total_sessions']), "")
        health_table.add_row("Success Rate", f"{health['global_metrics']['success_rate']:.1%}", "")
        health_table.add_row("Total Errors", str(health['global_metrics']['total_errors']), "")
        health_table.add_row("Active Sessions", str(health['active_sessions']), "")
        
        console.print(health_table)
        
        # Error Patterns
        if health['detected_patterns']:
            patterns_tree = Tree("🔍 Detected Patterns")
            for pattern_type, messages in health['detected_patterns'].items():
                pattern_branch = patterns_tree.add(f"[yellow]{pattern_type}[/yellow]")
                for message in messages:
                    pattern_branch.add(f"[dim]{message}[/dim]")
            console.print(patterns_tree)
        
        # Performance Summary
        if health['performance_summary']:
            perf = health['performance_summary']
            perf_table = Table(title="📈 Performance Summary")
            perf_table.add_column("Metric", style="cyan")
            perf_table.add_column("Current", style="blue")
            perf_table.add_column("Average", style="green")
            perf_table.add_column("Trend", style="yellow")
            
            for metric, data in perf.get('trends', {}).items():
                trend_icon = "📈" if data['trend'] == 'improving' else "📉"
                perf_table.add_row(
                    metric.replace('_', ' ').title(),
                    f"{data['current']:.2f}",
                    f"{data['average']:.2f}",
                    f"{trend_icon} {data['trend']}"
                )
            
            console.print(perf_table)

# Global feedback system instance
feedback_system = FeedbackSystem() 