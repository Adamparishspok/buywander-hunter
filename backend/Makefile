# Makefile for backend development

.PHONY: help install dev lint format test clean

help:
	@echo "Backend Development Commands:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make dev        - Run development server"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Remove build artifacts"

install:
	pip install -r requirements.txt

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	ruff format .

format-check:
	ruff format --check .

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
