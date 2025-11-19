.PHONY: help check build test test-cov publish-test publish release clean install install-dev

help: ## Show help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

check: ## Check project configuration (poetry check)
	@echo "Checking project configuration..."
	poetry check

lint: ## Run linters (isort, black)
	@echo "Running linters..."
	poetry run isort --check-only py_rutracker tests examples
	poetry run black --check py_rutracker tests examples

format: ## Format code (isort, black)
	@echo "Formatting code..."
	poetry run isort py_rutracker tests examples
	poetry run black py_rutracker tests examples

test: ## Run tests
	@echo "Running tests..."
	poetry run pytest tests/ -v

test-cov: ## Run tests with code coverage
	@echo "Running tests with coverage..."
	poetry run pytest tests/ -v --cov=py_rutracker --cov-report=html --cov-report=term

test-fast: ## Run tests quickly (without verbose output)
	@echo "Running tests (fast mode)..."
	poetry run pytest tests/ -q

build: check ## Build package
	@echo "Building package..."
	poetry build
	@echo "Package built successfully!"

clean: ## Clean temporary files and build artifacts
	@echo "Cleaning temporary files..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup completed!"

install: ## Install project dependencies
	@echo "Installing dependencies..."
	poetry install --no-root

install-dev: ## Install project dependencies including dev dependencies
	@echo "Installing dependencies (including dev)..."
	poetry install

publish-test: build ## Publish to TestPyPI
	@echo "Publishing to TestPyPI..."
	@if [ -z "$$POETRY_HTTP_BASIC_TESTPYPI_PASSWORD" ]; then \
		echo "Warning: Make sure TestPyPI token is configured:"; \
		echo "   poetry config http-basic.testpypi __token__ <your-token>"; \
		echo "   or set environment variables:"; \
		echo "   export POETRY_HTTP_BASIC_TESTPYPI_USERNAME=__token__"; \
		echo "   export POETRY_HTTP_BASIC_TESTPYPI_PASSWORD=<your-token>"; \
	fi
	poetry publish --repository testpypi
	@echo "Publishing to TestPyPI completed!"

publish: build ## Publish to PyPI
	@echo "Publishing to PyPI..."
	@if [ -z "$$POETRY_HTTP_BASIC_PYPI_PASSWORD" ]; then \
		echo "Warning: Make sure PyPI token is configured:"; \
		echo "   poetry config http-basic.pypi __token__ <your-token>"; \
		echo "   or set environment variables:"; \
		echo "   export POETRY_HTTP_BASIC_PYPI_USERNAME=__token__"; \
		echo "   export POETRY_HTTP_BASIC_PYPI_PASSWORD=<your-token>"; \
	fi
	poetry publish
	@echo "Publishing to PyPI completed!"

release-test: clean test build publish-test ## Full cycle: clean, test, build and publish to TestPyPI
	@echo "Full release cycle to TestPyPI completed!"

release: clean test build publish ## Full cycle: clean, test, build and publish to PyPI
	@echo "Full release cycle to PyPI completed!"

ci: check lint test-fast ## Commands for CI/CD (check, lint, fast tests)
	@echo "CI checks completed!"
