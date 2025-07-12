.PHONY: setup install test test-enhanced test-feedback test-integration test-llm test-multi-strategy test-performance run run-api run-quick-start run-validate-llm run-feedback-test format lint clean clean-feedback clean-all docker-build docker-run help

# Environment setup
setup:
	python3.11 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements-dev.txt

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# Testing commands
test:
	pytest src/tests/ -v --cov=src

test-enhanced:
	pytest src/tests/test_multi_strategy_enhanced.py -v --cov=src

test-feedback:
	python scripts/test_feedback_system.py

test-integration:
	pytest src/tests/test_llm_integration.py -v

test-llm:
	pytest src/tests/test_llm_integration.py -v

test-multi-strategy:
	pytest src/tests/test_multi_strategy.py -v

test-performance:
	pytest src/tests/ -v --cov=src -k "performance"

test-all:
	pytest src/tests/ -v --cov=src
	python scripts/testing/test_feedback_system.py
	python scripts/validation/validate_llm_integration.py

# Code quality
format:
	black src/
	ruff --fix src/

lint:
	ruff src/
	black --check src/

# Running applications
run:
	python -m src.main

run-api:
	uvicorn src.api.main:app --reload --port 8000

run-quick-start:
	python scripts/demos/quick_start.py

run-validate-llm:
	python scripts/validation/validate_llm_integration.py

run-feedback-test:
	python scripts/testing/test_feedback_system.py

# Feedback system specific commands
feedback-dashboard:
	python -c "from src.core.feedback_system import feedback_system; feedback_system.display_system_dashboard()"

feedback-health:
	python -c "from src.core.feedback_system import feedback_system; import json; print(json.dumps(feedback_system.get_system_health(), indent=2))"

feedback-reports:
	ls -la outputs/feedback/

# Development utilities
demo:
	python scripts/demos/quick_start.py

validate:
	python scripts/validation/validate_llm_integration.py

validate-openai:
	python scripts/validation/validate_llm_integration.py --openai

validate-ollama:
	python scripts/validation/validate_llm_integration.py --ollama

validate-local:
	python scripts/validation/validate_llm_integration.py --local

validate-all:
	python scripts/validation/validate_llm_integration.py --all

benchmark:
	pytest src/tests/test_multi_strategy.py -v -s --benchmark

# Cleaning commands
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov .pytest_cache

clean-feedback:
	rm -rf outputs/feedback/*.json
	rm -rf outputs/feedback/session_*.json

clean-outputs:
	rm -rf outputs/*.json
	rm -rf outputs/generation_*.json

clean-all: clean clean-feedback clean-outputs

# Docker commands
docker-build:
	docker build -t json-generator .

docker-run:
	docker run -p 8000:8000 --env-file .env json-generator

# Documentation and help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  make setup              - Create virtual environment and install dependencies"
	@echo "  make install            - Install production dependencies"
	@echo "  make install-dev        - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test               - Run standard test suite"
	@echo "  make test-enhanced      - Run enhanced tests with feedback system"
	@echo "  make test-feedback      - Run feedback system tests"
	@echo "  make test-integration   - Run LLM integration tests"
	@echo "  make test-llm           - Run LLM provider tests"
	@echo "  make test-multi-strategy - Run multi-strategy tests"
	@echo "  make test-performance   - Run performance tests"
	@echo "  make test-all           - Run all tests including validation scripts"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format             - Format code with black and ruff"
	@echo "  make lint               - Check code quality with ruff and black"
	@echo ""
	@echo "Running Applications:"
	@echo "  make run                - Run the main application"
	@echo "  make run-api            - Run the API server"
	@echo "  make run-quick-start    - Run interactive demo"
	@echo "  make run-validate-llm   - Run LLM validation"
	@echo "  make run-feedback-test  - Run feedback system tests"
	@echo ""
	@echo "Feedback System:"
	@echo "  make feedback-dashboard - Display system dashboard"
	@echo "  make feedback-health    - Show system health metrics"
	@echo "  make feedback-reports   - List feedback reports"
	@echo ""
	@echo "Development Utilities:"
	@echo "  make demo               - Run interactive demo"
	@echo "  make validate           - Validate all LLM integrations"
	@echo "  make validate-openai    - Validate OpenAI integration only"
	@echo "  make validate-ollama    - Validate Ollama integration only"
	@echo "  make validate-local     - Validate local model integration only"
	@echo "  make validate-all       - Validate all providers explicitly"
	@echo "  make benchmark          - Run performance benchmarks"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean              - Clean Python cache files"
	@echo "  make clean-feedback     - Clean feedback system outputs"
	@echo "  make clean-outputs      - Clean generation outputs"
	@echo "  make clean-all          - Clean everything"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build       - Build Docker image"
	@echo "  make docker-run         - Run Docker container"
	@echo ""
	@echo "Documentation:"
	@echo "  make help               - Show this help message"

# Create necessary directories
init-dirs:
	mkdir -p outputs/feedback
	mkdir -p outputs/generation
	mkdir -p data/cache
	mkdir -p models
	mkdir -p config

# Environment file setup
init-env:
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		echo "# OpenAI Configuration" > .env; \
		echo "OPENAI_API_KEY=your_openai_key_here" >> .env; \
		echo "" >> .env; \
		echo "# Ollama Configuration (optional)" >> .env; \
		echo "OLLAMA_HOST=http://localhost:11434" >> .env; \
		echo "OLLAMA_MODEL=llama3.1:8b" >> .env; \
		echo "" >> .env; \
		echo "# Local Models (optional)" >> .env; \
		echo "LOCAL_MODEL_PATH=/path/to/local/model.gguf" >> .env; \
		echo "" >> .env; \
		echo "# Feedback System Configuration" >> .env; \
		echo "FEEDBACK_OUTPUT_DIR=outputs/feedback" >> .env; \
		echo "FEEDBACK_ENABLE_DASHBOARD=true" >> .env; \
		echo "FEEDBACK_AUTO_RECOVERY=true" >> .env; \
		echo ".env file created! Please edit it with your configuration."; \
	else \
		echo ".env file already exists"; \
	fi

# Complete setup for new users
setup-complete: setup init-dirs init-env
	@echo "Setup complete! Next steps:"
	@echo "1. Edit .env file with your configuration"
	@echo "2. Run 'make test' to verify installation"
	@echo "3. Run 'make demo' for interactive demo"
	@echo "4. Run 'make help' for all available commands"

# Quick development start
dev-start: setup-complete
	@echo "Starting development environment..."
	@echo "Run 'source venv/bin/activate' to activate virtual environment"
	@echo "Then run 'make demo' to start interactive demo"

# CI/CD pipeline simulation
ci-test:
	make lint
	make test
	make test-enhanced
	make test-feedback
	make validate
