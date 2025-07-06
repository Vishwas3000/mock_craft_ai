# JSON Generator with Multi-LLM Support

A sophisticated JSON data generator that uses multiple LLM backends (OpenAI, Ollama, Local models) with advanced prompt engineering, schema analysis, and multi-strategy generation capabilities.

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   make setup
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Tests**
   ```bash
   make test
   ```

4. **Start Development**
   ```bash
   make run
   ```

## 📁 Project Structure

```
json-generator/
├── src/
│   ├── core/                    # Core generation logic
│   │   ├── __init__.py
│   │   ├── base_llm.py         # Base LLM interface
│   │   ├── config.py           # Configuration management
│   │   ├── generation_engine.py # Main generation orchestrator
│   │   ├── llm_manager.py      # Multi-LLM manager
│   │   ├── output_parser.py    # JSON parsing and validation
│   │   ├── prompt_engineer.py  # Advanced prompt engineering
│   │   ├── schema_analyzer.py  # Schema analysis and validation
│   │   └── llm_providers/      # LLM provider implementations
│   │       ├── __init__.py
│   │       ├── openai_llm.py   # OpenAI API integration
│   │       └── ollama_llm.py   # Ollama local server integration
│   ├── api/                    # FastAPI application (future)
│   ├── utils/                  # Utility functions
│   └── tests/                  # Comprehensive test suite
│       ├── __init__.py
│       ├── test_llm_integration.py  # LLM provider tests
│       └── test_multi_strategy.py   # Multi-strategy generation tests
├── config/                     # Configuration files
├── scripts/                    # Utility and validation scripts
│   ├── quick_start.py         # Interactive demo script
│   └── validate_llm_integration.py  # LLM integration validator
├── models/                     # Local model files
├── data/                      # Data and cache
└── venv/                      # Virtual environment
```

## 🧪 Test Suite

### Core Test Files

#### `src/tests/test_llm_integration.py`
**Purpose**: Comprehensive testing of LLM provider integrations and core functionality.

**Test Categories**:
- **Connection Tests**: Verify connectivity to OpenAI, Ollama, and local models
- **Generation Tests**: Test basic text generation, JSON generation, and streaming
- **Fallback Tests**: Test automatic fallback mechanisms between providers
- **Performance Tests**: Benchmark models and test concurrent generation
- **Integration Tests**: End-to-end testing with all available models

**Key Features**:
- Async test framework with pytest
- Automatic model detection and testing
- Performance benchmarking
- Error handling validation
- Multi-provider fallback testing

**Usage**:
```bash
# Run all LLM integration tests
pytest src/tests/test_llm_integration.py -v

# Run specific test categories
pytest src/tests/test_llm_integration.py::TestGeneration -v
pytest src/tests/test_llm_integration.py::TestFallback -v
```

#### `src/tests/test_multi_strategy.py`
**Purpose**: Test advanced multi-strategy prompt engineering and generation capabilities.

**Test Categories**:
- **Multi-Strategy Generation**: Test different prompt strategies (Chain-of-Thought, Few-Shot, Structured)
- **Schema Complexity Testing**: Test with simple, medium, and complex schemas
- **Adaptive Generation**: Test automatic strategy selection and refinement
- **Validation Testing**: Test output validation and quality scoring

**Key Features**:
- Rich console output with progress tracking
- Comprehensive schema testing (user profiles, e-commerce orders, company data)
- Strategy comparison and benchmarking
- Quality scoring and validation
- Adaptive generation with automatic retry

**Usage**:
```bash
# Run multi-strategy tests
pytest src/tests/test_multi_strategy.py -v

# Run specific test functions
pytest src/tests/test_multi_strategy.py::test_multi_strategy -v
pytest src/tests/test_multi_strategy.py::test_specific_strategies -v
```

## 🔧 Core Modules

### Generation Engine (`src/core/generation_engine.py`)
**Purpose**: Main orchestration engine for JSON generation with multiple strategies.

**Key Features**:
- **Three Generation Modes**: Single, Batch, Progressive
- **Multi-Strategy Support**: Automatic strategy selection based on complexity
- **Model Fallback**: Automatic fallback to alternative models
- **Rich Console Integration**: Beautiful progress bars and status updates
- **Validator Caching**: Performance optimization for repeated schemas

**Classes**:
- `GenerationMode`: Enum for generation strategies
- `GenerationRequest`: Complete request specification
- `GenerationResult`: Structured results with validation
- `JSONGenerationEngine`: Main orchestration engine

### Schema Analyzer (`src/core/schema_analyzer.py`)
**Purpose**: Advanced schema analysis and field constraint detection.

**Key Features**:
- **Complexity Scoring**: Automatic complexity assessment
- **Pattern Detection**: Email, phone, URL, date, UUID patterns
- **Constraint Analysis**: Min/max values, enums, relationships
- **Generation Hints**: Provides hints for optimal generation
- **Field Type Inference**: Automatic data type detection

### Prompt Engineer (`src/core/prompt_engineer.py`)
**Purpose**: Advanced prompt engineering with multiple strategies.

**Key Features**:
- **Multiple Strategies**: Zero-shot, Few-shot, Chain-of-Thought, Structured
- **Multi-Strategy Templates**: Combines multiple approaches
- **Model Optimization**: Tailors prompts for specific models
- **Example Library**: Domain-specific examples
- **Dynamic Prompt Building**: Context-aware prompt construction

### Output Parser (`src/core/output_parser.py`)
**Purpose**: Robust JSON parsing and validation with multiple extraction methods.

**Key Features**:
- **Multiple Extraction Methods**: Code blocks, regex, repair attempts
- **Validation Levels**: Strict, Moderate, Lenient
- **Quality Scoring**: 0-1 score based on validation results
- **Auto-Repair**: Attempts to fix common issues
- **Pattern Validation**: Email, phone, URL validation

### LLM Manager (`src/core/llm_manager.py`)
**Purpose**: Multi-LLM provider management with fallback and load balancing.

**Key Features**:
- **Provider Management**: OpenAI, Ollama, Local models
- **Automatic Fallback**: Seamless provider switching
- **Model Selection**: Priority-based model selection
- **Performance Monitoring**: Latency and quality tracking
- **Concurrent Generation**: Parallel request handling

## 🛠️ Utility Scripts

### Quick Start Script (`scripts/quick_start.py`)
**Purpose**: Interactive demo and testing of the LLM system.

**Features**:
- **Interactive Demo**: Real-time prompt testing
- **Model Selection**: Choose specific models or auto-selection
- **JSON Generation**: Test JSON generation capabilities
- **Example Runner**: Pre-built examples for testing
- **Rich Console**: Beautiful user interface

**Usage**:
```bash
python scripts/quick_start.py
# Choose from:
# 1. Interactive Demo
# 2. Run Examples
# 3. Exit
```

### LLM Integration Validator (`scripts/validate_llm_integration.py`)
**Purpose**: Comprehensive validation of LLM provider integrations.

**Features**:
- **Provider Testing**: Test individual or all providers
- **Connection Validation**: Verify API keys and connectivity
- **Performance Benchmarking**: Latency and quality metrics
- **Error Reporting**: Detailed error analysis
- **Rich Output**: Beautiful tables and progress bars

**Usage**:
```bash
# Test all providers
python scripts/validate_llm_integration.py

# Test specific providers
python scripts/validate_llm_integration.py --openai --ollama

# Test only local model
python scripts/validate_llm_integration.py --local
```

## 🔌 LLM Providers

### OpenAI Provider (`src/core/llm_providers/openai_llm.py`)
**Purpose**: OpenAI API integration with advanced features.

**Features**:
- **Multiple Models**: GPT-3.5, GPT-4, and variants
- **Streaming Support**: Real-time response streaming
- **JSON Mode**: Native JSON generation
- **Error Handling**: Robust error recovery
- **Rate Limiting**: Automatic rate limit management

### Ollama Provider (`src/core/llm_providers/ollama_llm.py`)
**Purpose**: Local Ollama server integration.

**Features**:
- **Local Models**: Llama, Mistral, and other local models
- **Server Management**: Automatic server detection
- **Model Pulling**: Automatic model downloading
- **Performance Optimization**: Local inference optimization
- **Offline Capability**: Works without internet

## 🚀 Development Progress

### ✅ Completed Features
- [x] **Week 1**: Multi-LLM Integration (OpenAI, Ollama, Local)
- [x] **Week 2**: Advanced Schema Analysis and Validation
- [x] **Week 3**: Multi-Strategy Generation Engine
- [x] **Week 4**: Advanced Prompt Engineering
- [x] **Week 5**: Production-Ready Features

### 🔄 Current Status
- **Core Engine**: ✅ Complete with multi-strategy support
- **LLM Integration**: ✅ All providers working
- **Schema Analysis**: ✅ Advanced pattern detection
- **Prompt Engineering**: ✅ Multi-strategy templates
- **Output Parsing**: ✅ Robust validation and repair
- **Testing**: ✅ Comprehensive test suite

### 📋 Next Steps
- [ ] Web API development
- [ ] Web search integration
- [ ] Multi-modal capabilities
- [ ] Production deployment
- [ ] Performance optimization

## 🧪 Running Tests

### All Tests
```bash
make test
```

### Specific Test Categories
```bash
# LLM Integration Tests
pytest src/tests/test_llm_integration.py -v

# Multi-Strategy Tests
pytest src/tests/test_multi_strategy.py -v

# Individual Test Classes
pytest src/tests/test_llm_integration.py::TestGeneration -v
pytest src/tests/test_llm_integration.py::TestFallback -v

# Individual Test Functions
pytest src/tests/test_multi_strategy.py::test_multi_strategy -v
pytest src/tests/test_multi_strategy.py::test_specific_strategies -v
```

### Validation Scripts
```bash
# Validate LLM Integration
python scripts/validate_llm_integration.py

# Interactive Demo
python scripts/quick_start.py
```

## 📊 Test Coverage

The test suite provides comprehensive coverage of:

- **LLM Provider Integration**: 100% coverage of all providers
- **Generation Engine**: All modes and strategies tested
- **Schema Analysis**: Pattern detection and complexity scoring
- **Prompt Engineering**: All strategies and combinations
- **Output Parsing**: All extraction methods and validation levels
- **Error Handling**: Fallback mechanisms and error recovery
- **Performance**: Benchmarking and concurrent generation

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Ollama (optional)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Local Models (optional)
LOCAL_MODEL_PATH=/path/to/local/model.gguf
```

### Model Configuration
The system automatically detects and configures available models:
- **OpenAI**: Requires API key
- **Ollama**: Requires running Ollama server
- **Local**: Requires GGUF model file

## 📈 Performance

### Benchmark Results
- **OpenAI GPT-3.5**: ~2-3 seconds per generation
- **Ollama Llama3.1**: ~5-10 seconds per generation
- **Local Models**: ~10-30 seconds per generation (depending on hardware)

### Optimization Features
- **Validator Caching**: Reduces repeated validation overhead
- **Model Fallback**: Ensures high availability
- **Concurrent Generation**: Parallel processing for batch requests
- **Streaming Support**: Real-time response for better UX

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Run tests**: `make test`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
