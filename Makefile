# Makefile for PAN-OS Configuration API

.PHONY: help build test test-local test-docker run stop clean install lint

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

build:  ## Build Docker image
	docker-compose build

run:  ## Run API with Docker Compose
	docker-compose up -d
	@echo "API running at http://localhost:8000"
	@echo "Swagger UI at http://localhost:8000/docs"

stop:  ## Stop Docker containers
	docker-compose down

test-local:  ## Run tests locally (no Docker)
	./tests/run_tests_local.sh

test-docker:  ## Run tests with Docker
	./tests/run_tests.sh

test-full:  ## Run full test suite with error handling
	./tests/run_tests_full.sh

test: test-local  ## Run tests (alias for test-local)

test-basic:  ## Run basic smoke tests (API must be running)
	python tests/test_basic.py

test-validate:  ## Run simple validation tests (API must be running)
	python tests/test_simple_validation.py

test-coverage:  ## Run tests with coverage report
	pytest --cov=main --cov=parser --cov=models \
	       --cov-report=term-missing \
	       --cov-report=html:tests/htmlcov \
	       --cov-report=xml:tests/coverage.xml
	@echo "Coverage report: tests/htmlcov/index.html"

lint:  ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf tests/htmlcov tests/coverage_reports tests/coverage.xml .coverage .pytest_cache
	docker-compose down -v

logs:  ## Show Docker logs
	docker-compose logs -f

shell:  ## Shell into running container
	docker-compose exec pan-config-api /bin/bash

dev:  ## Run API locally for development
	CONFIG_FILES_PATH=config-files uvicorn main:app --reload --host 0.0.0.0 --port 8000