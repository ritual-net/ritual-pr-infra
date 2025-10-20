.PHONY: help format lint test all

help:
	@echo "Available targets:"
	@echo "  make format  - Format code with ruff"
	@echo "  make lint    - Lint code with ruff"
	@echo "  make test    - Run tests with pytest"
	@echo "  make all     - Run format, lint, and test"

format:
	uvx ruff format src/ tests/

lint:
	uvx ruff check src/ tests/

test:
	uv run pytest tests/ -v

all: format lint test

