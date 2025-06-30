# JSON Generator with Multi-LLM Support

A sophisticated JSON data generator that uses multiple LLM backends (OpenAI, Ollama, Local models) with web search and multi-modal scraping capabilities.

## Quick Start

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

## Project Structure
```
json-generator/
├── src/
│   ├── core/          # Core LLM and generation logic
│   ├── api/           # FastAPI application
│   ├── utils/         # Utility functions
│   └── tests/         # Test suite
├── config/            # Configuration files
├── scripts/           # Utility scripts
├── models/            # Local model files
└── data/             # Data and cache
```

## Development Progress

- [ ] Week 1: LLM Integration (OpenAI, Ollama, Local)
- [ ] Week 2: Schema Analysis
- [ ] Week 3: Generation Engine
- [ ] Week 4: Web Search Integration
- [ ] Week 5: Production Features
