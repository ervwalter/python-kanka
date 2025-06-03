.PHONY: install test lint format check clean coverage help

# Default target
help:
	@echo "Available commands:"
	@echo "  make install   - Install development dependencies"
	@echo "  make test      - Run all tests"
	@echo "  make lint      - Run code linting"
	@echo "  make format    - Format code with black and sort imports with isort"
	@echo "  make check     - Run all checks (lint + test)"
	@echo "  make clean     - Clean up temporary files"
	@echo "  make coverage  - Run tests with coverage report"

# Install development dependencies
install:
	pip install -r requirements.txt
	pip install -r dev-requirements.txt
	pip install -e .

# Run all tests
test:
	pytest tests/ -v

# Run linting
lint:
	ruff check .
	black --check .
	isort --check-only .

# Format code
format:
	black .
	isort .
	ruff check --fix .

# Run all checks
check: lint test

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# Run tests with coverage
coverage:
	pytest tests/ -v --cov=kanka --cov-report=html --cov-report=term