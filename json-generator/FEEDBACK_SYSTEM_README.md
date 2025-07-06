# Comprehensive Feedback System

A powerful feedback and monitoring system for the JSON Generation Pipeline that provides real-time tracking, error analysis, performance monitoring, and intelligent recovery suggestions.

## 🚀 Features

### 1. **Multi-Level Error Detection & Classification**
- Automatic error categorization (LLM, Validation, Parsing, Schema, etc.)
- Severity assessment (Critical, High, Medium, Low, Info)
- Detailed error context and stack traces
- Pattern detection for recurring issues

### 2. **Phase-by-Phase Monitoring**
- Track each generation phase (Schema Analysis, Prompt Building, LLM Generation, etc.)
- Performance metrics for each phase
- Success/failure tracking
- Timing and duration analysis

### 3. **Intelligent Recovery System**
- Automated recovery suggestions based on error type
- Priority-based recommendations
- Success probability estimates
- Strategy switching recommendations

### 4. **Performance Monitoring**
- Real-time performance tracking
- Trend analysis and optimization insights
- Throughput and latency metrics
- Resource utilization monitoring

### 5. **Comprehensive Reporting**
- Detailed session reports
- System health dashboards
- Pattern analysis reports
- Performance summaries

## 📦 Installation

The feedback system is already integrated into the project. No additional installation required.

## 🔧 Usage

### Basic Usage with Decorators

```python
from src.core.enhanced_test_decorators import comprehensive_test_tracking

@comprehensive_test_tracking("my_test")
async def my_test_function():
    # Your test code here
    result = await some_generation_function()
    return result
```

### Using the Feedback-Integrated Engine

```python
from src.core.feedback_integration import create_feedback_engine
from src.core.generation_engine import GenerationEngine, GenerationRequest

# Create feedback-integrated engine
engine = GenerationEngine(llm_manager, schema_analyzer, config)
feedback_engine = create_feedback_engine(engine)

# Generate with automatic feedback tracking
request = GenerationRequest(
    schema=your_schema,
    count=5,
    context="Your test context"
)

result = await feedback_engine.generate_with_feedback(request, "test_name")
```

### Using Context Managers

```python
from src.core.feedback_integration import feedback_tracking

with feedback_tracking("test_name", schema, "context"):
    # Your code here
    result = perform_some_operation()
```

### Manual Session Management

```python
from src.core.feedback_system import feedback_system, GenerationPhase

# Start session
session_id = feedback_system.start_session(
    test_name="manual_test",
    input_schema=schema,
    input_context="Manual tracking test",
    configuration={}
)

# Track phases
feedback_system.start_phase(session_id, GenerationPhase.SCHEMA_ANALYSIS)
# ... your code ...
feedback_system.end_phase(session_id, GenerationPhase.SCHEMA_ANALYSIS, success=True)

# Record errors
try:
    risky_operation()
except Exception as e:
    recovery_suggestions = feedback_system.record_error(
        session_id=session_id,
        error=e,
        phase=GenerationPhase.LLM_GENERATION
    )

# Complete session
feedback_system.complete_session(session_id, status="completed")
```

## 🎯 Integration Options

### 1. **Decorator-Based Integration** (Recommended)
- Minimal code changes
- Automatic session management
- Comprehensive tracking

### 2. **Engine Wrapper Integration**
- Seamless integration with existing code
- Automatic phase tracking
- No changes to existing GenerationRequest calls

### 3. **Context Manager Integration**
- Fine-grained control
- Explicit session boundaries
- Good for complex workflows

### 4. **Manual Integration**
- Maximum control
- Custom tracking logic
- Advanced use cases

## 📊 Available Decorators

### `@comprehensive_test_tracking`
Complete tracking with all features enabled:
```python
@comprehensive_test_tracking("test_name")
async def my_test():
    # Automatic session management
    # Phase tracking
    # Error detection
    # Performance monitoring
    # Recovery suggestions
    pass
```

### `@generation_test_tracking`
Focused on generation-specific tracking:
```python
@generation_test_tracking("generation_test")
async def test_generation():
    # Generation phase tracking
    # LLM interaction monitoring
    # Output analysis
    pass
```

### `@performance_test_tracking`
Performance-focused monitoring:
```python
@performance_test_tracking("perf_test")
async def performance_test():
    # Execution time tracking
    # Resource utilization
    # Throughput analysis
    pass
```

### `@validation_test_tracking`
Validation-specific tracking:
```python
@validation_test_tracking("validation_test")
async def validation_test():
    # Validation phase tracking
    # Error categorization
    # Score analysis
    pass
```

## 🔍 Monitoring and Analysis

### System Dashboard
```python
from src.core.feedback_system import feedback_system

# Display comprehensive dashboard
feedback_system.display_system_dashboard()

# Get system health data
health = feedback_system.get_system_health()
print(f"Success Rate: {health['global_metrics']['success_rate']:.1%}")
```

### Session Reports
Session data is automatically saved to `outputs/feedback/session_*.json` files containing:
- Complete session metadata
- Phase-by-phase timing
- Error details and recovery suggestions
- Performance metrics
- Validation results

## 🛠️ Error Categories

The system automatically categorizes errors into:

- **LLM_ERROR**: API failures, model issues
- **VALIDATION_ERROR**: Schema compliance failures
- **PARSING_ERROR**: JSON parsing failures
- **SCHEMA_ERROR**: Invalid schema definitions
- **TIMEOUT_ERROR**: Generation timeouts
- **CONFIGURATION_ERROR**: Setup issues
- **PARTIAL_SUCCESS**: Incomplete but partially successful operations
- **DATA_QUALITY_ERROR**: Quality issues in generated data
- **NETWORK_ERROR**: Network connectivity issues
- **RATE_LIMIT_ERROR**: API rate limiting

## 🔧 Recovery Suggestions

The system provides intelligent recovery suggestions:

### For LLM Errors:
- Switch to fallback model
- Adjust parameters (temperature, max_tokens)
- Retry with delay

### For Validation Errors:
- Use more lenient validation
- Switch to structured prompt strategy
- Reduce complexity

### For Parsing Errors:
- Use more explicit JSON formatting
- Lower temperature for consistency
- Switch prompt strategy

### For Timeout Errors:
- Reduce generation count
- Switch to faster model
- Simplify schema

## 📈 Performance Metrics

The system tracks:
- **Execution Time**: Total and per-phase timing
- **Throughput**: Records per second
- **Success Rate**: Percentage of successful operations
- **Validation Scores**: Quality metrics
- **Retry Counts**: Recovery attempt statistics
- **Resource Usage**: Memory and CPU utilization

## 🎮 Running the Demo

Test the feedback system with the comprehensive demo:

```bash
cd json-generator
python scripts/test_feedback_system.py
```

This will demonstrate:
- Basic tracking functionality
- Error detection and recovery
- Performance monitoring
- Validation tracking
- Comprehensive analysis
- Context manager usage
- System dashboard

## 📁 Output Files

The feedback system creates:
- `outputs/feedback/session_*.json`: Individual session reports
- `outputs/feedback/comprehensive_report.json`: System-wide analysis
- Console output with rich formatting and dashboards

## 🔄 Integration with Existing Tests

To integrate with your existing test suite:

1. **Add decorators to test functions:**
```python
@comprehensive_test_tracking("existing_test")
def test_existing_functionality():
    # Your existing test code
    pass
```

2. **Use the feedback engine wrapper:**
```python
# Replace your engine initialization
feedback_engine = create_feedback_engine(your_existing_engine)

# Use the same interface
result = await feedback_engine.generate_with_feedback(request, "test_name")
```

3. **Add context managers for fine control:**
```python
with feedback_tracking("test_name", schema):
    # Your existing test logic
    pass
```

## 🎯 Best Practices

1. **Use descriptive test names** for better tracking
2. **Include relevant context** in session initialization
3. **Handle errors gracefully** to get recovery suggestions
4. **Review session reports** for optimization opportunities
5. **Monitor system health** regularly
6. **Use appropriate validation levels** for your use case

## 🚀 Advanced Features

### Pattern Detection
The system automatically detects:
- Recurring error patterns
- Performance degradation trends
- Validation failure patterns
- Strategy effectiveness patterns

### Learning System
- Tracks strategy effectiveness over time
- Identifies optimal configurations
- Suggests improvements based on historical data

### Custom Metrics
Add custom metrics to sessions:
```python
feedback_system.start_phase(
    session_id, 
    GenerationPhase.CUSTOM,
    metadata={"custom_metric": "value"}
)
```

## 📞 Support

For questions or issues:
1. Check the session reports in `outputs/feedback/`
2. Review the system dashboard for insights
3. Examine error patterns for recurring issues
4. Use recovery suggestions for optimization

The feedback system is designed to be self-documenting through its comprehensive reporting and analysis features. 