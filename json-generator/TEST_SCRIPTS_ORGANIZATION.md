# Test Scripts and Validation Scripts Organization

A comprehensive guide to all test scripts, validation scripts, and testing utilities in the JSON Generator project.

## 📋 Table of Contents

1. [Core Test Suite](#core-test-suite)
2. [Enhanced Test Suite](#enhanced-test-suite)
3. [Test Decorators](#test-decorators)
4. [Validation Scripts](#validation-scripts)
5. [Utility Scripts](#utility-scripts)
6. [Testing Workflows](#testing-workflows)
7. [Script Dependencies](#script-dependencies)
8. [Usage Examples](#usage-examples)

---

## 🧪 Core Test Suite

### 1. LLM Integration Tests (`src/tests/test_llm_integration.py`)

**Purpose**: Comprehensive testing of LLM provider integrations and core functionality.

**Key Features**:
- **Connection Tests**: Verify connectivity to OpenAI, Ollama, and local models
- **Generation Tests**: Test basic text generation, JSON generation, and streaming
- **Fallback Tests**: Test automatic fallback mechanisms between providers
- **Performance Tests**: Benchmark models and test concurrent generation
- **Integration Tests**: End-to-end testing with all available models

**Test Classes**:
- `TestLLMConnections`: Basic connection validation
- `TestGeneration`: Generation capabilities testing
- `TestFallback`: Fallback mechanism validation
- `TestPerformance`: Performance benchmarking
- `TestIntegration`: Full integration testing

**Test Functions**:
```python
# Connection Tests
async def test_openai_connection(self)
async def test_ollama_connection(self)
async def test_local_model_connection(self)

# Generation Tests
async def test_basic_generation(self, llm_manager)
async def test_json_generation(self, llm_manager)
async def test_generation_with_config(self, llm_manager)
async def test_streaming_generation(self, llm_manager)

# Fallback Tests
async def test_fallback_mechanism(self, llm_manager)
async def test_model_priority_selection(self, llm_manager)

# Performance Tests
async def test_benchmark_models(self, llm_manager)
async def test_concurrent_generation(self, llm_manager)

# Integration Tests
async def test_multi_model_generation(self, llm_manager)
async def test_error_handling(self, llm_manager)
```

**Usage**:
```bash
# Run all LLM integration tests
pytest src/tests/test_llm_integration.py -v

# Run specific test classes
pytest src/tests/test_llm_integration.py::TestGeneration -v
pytest src/tests/test_llm_integration.py::TestFallback -v
```

### 2. Multi-Strategy Tests (`src/tests/test_multi_strategy.py`)

**Purpose**: Test advanced multi-strategy prompt engineering and generation capabilities.

**Key Features**:
- **Strategy Comparison**: Test different prompt strategies (Chain-of-Thought, Few-Shot, Structured, Zero-Shot)
- **Schema Complexity Testing**: Test with simple, medium, and complex schemas
- **Adaptive Generation**: Test automatic strategy selection and refinement
- **Performance Analysis**: Compare strategy effectiveness and performance

**Test Functions**:
```python
async def test_multi_strategy()      # Main multi-strategy comparison test
async def test_specific_strategies() # Individual strategy testing
```

**Schema Complexity Levels**:
- **Simple**: Basic user profile (4-5 fields)
- **Medium**: E-commerce order with nested objects
- **Complex**: Company organizational data with deep nesting

**Usage**:
```bash
# Run multi-strategy tests
pytest src/tests/test_multi_strategy.py -v

# Run specific test functions
pytest src/tests/test_multi_strategy.py::test_multi_strategy -v
pytest src/tests/test_multi_strategy.py::test_specific_strategies -v
```

---

## 🌟 Enhanced Test Suite

### 3. Enhanced Multi-Strategy Tests (`src/tests/test_multi_strategy_enhanced.py`)

**Purpose**: Enhanced testing with comprehensive feedback system integration.

**Key Features**:
- **Comprehensive Feedback Tracking**: Automatic session management and phase tracking
- **Detailed Error Analysis**: Error categorization and recovery suggestions
- **Performance Monitoring**: Real-time performance metrics and optimization insights
- **Pattern Detection**: Identify recurring issues and optimization opportunities
- **Automated Reporting**: Generate detailed reports and dashboards

**Test Classes**:
```python
class TestMultiStrategyEnhanced:
    """Enhanced test suite with comprehensive feedback integration"""
```

**Test Functions**:
```python
@comprehensive_test_tracking("simple_schema_comprehensive")
def test_simple_schema_comprehensive(self)

@generation_test_tracking("complex_schema_generation")
def test_complex_schema_generation(self)

@performance_test_tracking("performance_benchmark")
def test_performance_benchmark(self)

@validation_test_tracking("validation_stress_test")
def test_validation_stress_test(self)

@with_comprehensive_analysis("error_recovery_simulation")
def test_error_recovery_simulation(self)

def test_comprehensive_system_analysis(self)
```

**Usage**:
```bash
# Run enhanced tests with feedback
pytest src/tests/test_multi_strategy_enhanced.py -v -s

# Run specific test methods
pytest src/tests/test_multi_strategy_enhanced.py::TestMultiStrategyEnhanced::test_simple_schema_comprehensive -v
```

---

## 🎨 Test Decorators

### 4. Basic Test Decorators (`src/utils/testing/test_decorators.py`)

**Purpose**: Automatic output management and result saving for tests.

**Key Features**:
- **Automatic Result Saving**: Save test outputs, errors, and metadata
- **Execution Tracking**: Track execution time and success/failure status
- **Rich Console Output**: Beautiful terminal output with progress indicators
- **Error Logging**: Comprehensive error logging with stack traces

**Available Decorators**:
```python
@save_test_output("test_name")                    # General test output saving
@save_generation_output("generation_test")       # Generation-specific output
@save_validation_output("validation_test")       # Validation-specific output
@with_output_summary                             # Display summary after tests
```

**Usage Example**:
```python
from src.utils.testing.test_decorators import save_test_output, save_generation_output

@save_test_output("my_test_name")
def my_test_function():
    # Your test code here
    return result

@save_generation_output("generation_test")
def test_generation():
    # Generation test code
    return generated_data
```

### 5. Enhanced Test Decorators (`src/utils/testing/enhanced_test_decorators.py`)

**Purpose**: Enhanced decorators with comprehensive feedback system integration.

**Key Features**:
- **Comprehensive Feedback Tracking**: Automatic session management and phase tracking
- **Error Detection**: Automatic error categorization and recovery suggestions
- **Performance Monitoring**: Real-time performance metrics and trend analysis
- **Pattern Analysis**: Detect recurring issues and optimization opportunities

**Available Decorators**:
```python
@comprehensive_test_tracking("test_name")         # Complete tracking with all features
@generation_test_tracking("generation_test")     # Generation-specific monitoring
@performance_test_tracking("perf_test")          # Performance-focused analysis
@validation_test_tracking("validation_test")     # Validation-specific tracking
@with_comprehensive_analysis("analysis_test")    # Advanced analysis capabilities
```

**Usage Example**:
```python
from src.utils.testing.enhanced_test_decorators import comprehensive_test_tracking

@comprehensive_test_tracking("my_enhanced_test")
async def my_enhanced_test():
    # Your test code here - automatic tracking enabled
    result = await some_generation_function()
    return result
```

---

## 🔍 Validation Scripts

### 6. LLM Integration Validator (`scripts/validate_llm_integration.py`)

**Purpose**: Comprehensive validation of LLM provider integrations.

**Key Features**:
- **Provider Testing**: Test individual or all providers (OpenAI, Ollama, Local)
- **Connection Validation**: Verify API keys and connectivity
- **Performance Benchmarking**: Latency and quality metrics
- **Error Reporting**: Detailed error analysis and troubleshooting
- **Rich Console Output**: Beautiful tables and progress indicators

**Test Functions**:
```python
async def test_openai()         # OpenAI API validation
async def test_ollama()         # Ollama server validation
async def test_local_model()    # Local model validation
async def test_llm_manager()    # LLM manager integration
```

**Usage**:
```bash
# Test all providers
python scripts/validate_llm_integration.py

# Test specific providers
python scripts/validate_llm_integration.py --openai
python scripts/validate_llm_integration.py --ollama
python scripts/validate_llm_integration.py --local
python scripts/validate_llm_integration.py --openai --ollama

# Test LLM manager
python scripts/validate_llm_integration.py --manager
```

### 7. Feedback System Test Script (`scripts/test_feedback_system.py`)

**Purpose**: Comprehensive testing and demonstration of the feedback system.

**Key Features**:
- **Comprehensive System Testing**: Test all feedback system components
- **Error Simulation**: Simulate various error conditions and recovery scenarios
- **Performance Monitoring**: Validate performance tracking capabilities
- **Dashboard Verification**: Test reporting and dashboard functionality
- **Integration Testing**: Test integration with generation engine

**Demo Functions**:
```python
async def demonstrate_basic_tracking()          # Basic feedback tracking demo
async def demonstrate_error_handling()         # Error detection and recovery demo
async def demonstrate_performance_monitoring() # Performance monitoring demo
async def demonstrate_validation_tracking()    # Validation tracking demo
async def demonstrate_comprehensive_analysis() # Comprehensive analysis demo
def demonstrate_context_manager()              # Context manager usage demo
```

**Usage**:
```bash
# Run all feedback system tests
python scripts/test_feedback_system.py

# Run specific categories (if supported)
python scripts/test_feedback_system.py --category error_detection
python scripts/test_feedback_system.py --category performance_monitoring
python scripts/test_feedback_system.py --category recovery_suggestions
```

---

## 🛠️ Utility Scripts

### 8. Quick Start Script (`scripts/quick_start.py`)

**Purpose**: Interactive demo and testing of the LLM system.

**Key Features**:
- **Interactive Demo**: Real-time prompt testing with user input
- **Model Selection**: Choose specific models or use automatic selection
- **JSON Generation**: Test JSON generation capabilities interactively
- **Example Runner**: Pre-built examples for quick testing
- **Rich Console Interface**: Beautiful user interface with progress indicators

**Usage**:
```bash
# Run interactive demo
python scripts/quick_start.py

# Available options:
# 1. Interactive Demo - Real-time testing
# 2. Run Examples - Pre-built test cases
# 3. Exit
```

---

## 🔄 Testing Workflows

### Standard Testing Workflow

```bash
# 1. Setup and validation
make setup
make validate

# 2. Run core tests
make test

# 3. Run enhanced tests
make test-enhanced

# 4. Run feedback system tests
make test-feedback

# 5. Run comprehensive validation
make test-all
```

### Development Testing Workflow

```bash
# 1. Quick validation
make demo

# 2. Specific test categories
make test-llm
make test-multi-strategy
make test-performance

# 3. Feedback system validation
make feedback-dashboard
make feedback-health

# 4. Clean up
make clean-all
```

### CI/CD Testing Workflow

```bash
# Complete CI/CD pipeline
make ci-test

# Individual CI steps
make lint
make test
make test-enhanced
make test-feedback
make validate
```

---

## 📊 Script Dependencies

### Core Dependencies
```
pytest>=7.4.4
pytest-asyncio>=0.23.3
pytest-cov>=4.1.0
rich>=13.7.0
```

### LLM Dependencies
```
openai>=1.10.0
ollama>=0.1.7
llama-cpp-python>=0.2.32
```

### Enhanced Feature Dependencies
```
langchain>=0.1.0
langchain-community>=0.0.10
langchain-openai>=0.0.5
```

### Dependency Graph
```
test_llm_integration.py
├── src.core.llm_manager
├── src.core.base_llm
├── src.core.config
└── src.core.llm_providers.*

test_multi_strategy.py
├── src.core.generation_engine
├── src.core.schema_analyzer
├── src.core.prompt_engineer
├── src.core.output_parser
├── src.utils.output.output_manager
└── src.utils.testing.test_decorators

test_multi_strategy_enhanced.py
├── All of test_multi_strategy.py
├── src.core.feedback_system
├── src.core.feedback_integration
└── src.utils.testing.enhanced_test_decorators

validate_llm_integration.py
├── src.core.llm_manager
├── src.core.config
└── src.core.llm_providers.*

test_feedback_system.py
├── src.core.feedback_system
├── src.core.feedback_integration
├── src.utils.testing.enhanced_test_decorators
└── src.core.generation_engine

Utility Dependencies:
├── src.utils.output.output_manager       # Output management
├── src.utils.testing.test_decorators     # Basic test decorators
├── src.utils.testing.enhanced_test_decorators # Enhanced decorators
└── src.utils.processing.uuid_processor   # UUID processing
```

---

## 💡 Usage Examples

### Running Individual Test Categories

```bash
# Connection tests only
pytest src/tests/test_llm_integration.py::TestLLMConnections -v

# Generation tests only
pytest src/tests/test_llm_integration.py::TestGeneration -v

# Performance tests only
pytest src/tests/test_llm_integration.py::TestPerformance -v

# Enhanced tests with feedback
pytest src/tests/test_multi_strategy_enhanced.py::TestMultiStrategyEnhanced::test_simple_schema_comprehensive -v
```

### Using Test Decorators

```python
# Basic test with output saving
from src.utils.testing.test_decorators import save_test_output

@save_test_output("my_custom_test")
def my_test():
    # Test implementation
    return {"status": "success", "data": [1, 2, 3]}

# Enhanced test with feedback tracking
from src.utils.testing.enhanced_test_decorators import comprehensive_test_tracking

@comprehensive_test_tracking("my_enhanced_test")
async def my_enhanced_test():
    # Test implementation with automatic feedback tracking
    result = await generate_data()
    return result
```

### Using Context Managers

```python
# Feedback tracking with context manager
from src.core.feedback_integration import feedback_tracking

with feedback_tracking("test_name", schema, "context"):
    # Your test code here
    result = perform_operation()
```

### Custom Validation Scripts

```python
# Custom validation using existing components
from scripts.validate_llm_integration import test_openai, test_ollama

async def custom_validation():
    openai_result = await test_openai()
    ollama_result = await test_ollama()
    
    print(f"OpenAI: {openai_result['status']}")
    print(f"Ollama: {ollama_result['status']}")
```

---

## 🎯 Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Include docstrings for complex tests
- Use appropriate fixtures for setup/teardown

### 2. Error Handling
- Test both success and failure cases
- Use appropriate exception handling
- Log errors with sufficient detail
- Provide meaningful error messages

### 3. Performance Testing
- Use async/await for concurrent operations
- Measure execution time for performance tests
- Test with different data sizes
- Monitor resource usage

### 4. Feedback System Integration
- Use appropriate decorators for test types
- Enable comprehensive tracking for critical tests
- Review feedback reports regularly
- Act on recovery suggestions

### 5. Validation Scripts
- Run validation scripts before major releases
- Test all configured providers
- Verify connectivity and performance
- Document any configuration requirements

---

## 📈 Test Metrics and Reporting

### Generated Reports
- **Session Reports**: `outputs/feedback/session_*.json`
- **Error Logs**: `outputs/errors/error_*.json`
- **Performance Metrics**: `outputs/performance/perf_*.json`
- **Validation Results**: `outputs/validation/validation_*.json`

### Dashboard Access
```bash
# Display system dashboard
make feedback-dashboard

# Show system health
make feedback-health

# List feedback reports
make feedback-reports
```

### Continuous Monitoring
- Monitor success rates over time
- Track performance trends
- Identify recurring error patterns
- Optimize based on feedback insights

---

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Local Model Configuration
LOCAL_MODEL_PATH=/path/to/model.gguf

# Testing Configuration
TEST_TIMEOUT=300
TEST_RETRIES=3
TEST_PARALLEL_WORKERS=4

# Feedback System Configuration
FEEDBACK_OUTPUT_DIR=outputs/feedback
FEEDBACK_ENABLE_DASHBOARD=true
FEEDBACK_AUTO_RECOVERY=true
```

### Test Configuration
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["src/tests"]
asyncio_mode = "auto"
addopts = "-v --cov=src --cov-report=html --cov-report=term-missing"
```

---

This comprehensive organization provides a complete overview of all test scripts and validation scripts in your JSON Generator project. Each script is categorized by purpose, documented with usage examples, and includes information about dependencies and relationships. 