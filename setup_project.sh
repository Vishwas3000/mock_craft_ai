#!/bin/bash
# setup_project.sh - Run this first to create project structure

echo "🚀 Setting up JSON Generator Project..."

# Create project structure
mkdir -p json-generator/{src/{core,api,utils,tests},config,scripts,models,data}
cd json-generator

# Create essential files
touch src/__init__.py
touch src/core/__init__.py
touch src/api/__init__.py
touch src/utils/__init__.py
touch src/tests/__init__.py

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core dependencies
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.5
openai==1.10.0
ollama==0.1.7
llama-cpp-python==0.2.32
transformers==4.37.0
torch==2.1.0

# API Framework
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
python-dotenv==1.0.0

# Utilities
aiohttp==3.9.1
requests==2.31.0
tqdm==4.66.1
colorama==0.4.6
rich==13.7.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0

# Development tools
black==23.12.1
ruff==0.1.11
pre-commit==3.6.0
EOF

# Create requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
-r requirements.txt
ipython==8.19.0
jupyter==1.0.0
httpx==0.26.0
EOF

# Create .env.example
cat > .env.example << 'EOF'
# API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:latest

# Local Model Configuration
LOCAL_MODEL_PATH=./models/llama-2-7b-chat.gguf
LOCAL_MODEL_TYPE=llama_cpp

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Project specific
models/*.gguf
models/*.bin
data/cache/
logs/
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# OS
.DS_Store
Thumbs.db
EOF

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.pytest.ini_options]
testpaths = ["src/tests"]
asyncio_mode = "auto"
EOF

# Create Makefile
cat > Makefile << 'EOF'
.PHONY: setup install test run clean

setup:
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements-dev.txt

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest src/tests/ -v --cov=src

test-integration:
	pytest src/tests/integration/ -v

format:
	black src/
	ruff --fix src/

lint:
	ruff src/
	black --check src/

run:
	python -m src.main

run-api:
	uvicorn src.api.main:app --reload --port 8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov .pytest_cache

docker-build:
	docker build -t json-generator .

docker-run:
	docker run -p 8000:8000 --env-file .env json-generator
EOF

# Create README.md
cat > README.md << 'EOF'
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
EOF

echo "✅ Project structure created!"
echo ""
echo "Next steps:"
echo "1. cd json-generator"
echo "2. make setup"
echo "3. source venv/bin/activate"
echo "4. cp .env.example .env"
echo "5. Edit .env with your API keys"
echo ""
echo "Run ./setup_project.sh to begin!" 