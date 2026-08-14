PYTHON ?= python
PROJECT_DIR := Atoms

.PHONY: help install test lint format check run clean

help:
	@echo "Available targets:"
	@echo "  install   Install dependencies"
	@echo "  test      Run tests with coverage"
	@echo "  fix       Fixar as correções nos arquivos"
	@echo "  lint      Run linters (ruff, pylint, mypy)"
	@echo "  format    Format code with ruff"
	@echo "  check     Run lint + test"
	@echo "  run       Run the FastAPI server"
	@echo "  clean     Remove cache and build artifacts"

install:
	$(PYTHON) -m pip install -e "$(PROJECT_DIR)[dev]"

test:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m pytest tests --cov=src --cov-report=term --cov-report=xml -q

fix:
	cd Atoms && PYTHONPATH=src python -m ruff check --fix src tests main.py

lint:
	cd Atoms && PYTHONPATH=src python -m ruff check --fix src tests main.py
	cd Atoms && PYTHONPATH=src python -m pylint --rcfile=pyproject.toml src tests main.py

format:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m ruff format src tests main.py

check: test lint

run:
	cd $(PROJECT_DIR) && $(PYTHON) main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
