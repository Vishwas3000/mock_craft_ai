.PHONY: setup install test run clean

setup:
	python3 -m venv venv
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
