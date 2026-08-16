PYTHON ?= python
PROJECT_DIR := Atoms
SRC_DIRS := src tests main.py

.PHONY: help install tests lint mypy fix format check ci run clean

help:
	@echo "Available targets:"
	@echo "  install   Install dependencies"
	@echo "  tests      Run tests with coverage"
	@echo "  lint      Run linters (ruff + pylint), read-only, no auto-fix"
	@echo "  mypy      Run static type checking"
	@echo "  fix       Auto-fix what ruff can fix, then format"
	@echo "  format    Format code with ruff"
	@echo "  check     Run lint + mypy + tests (same gate as CI)"
	@echo "  ci        Alias for check; mirrors .github/workflows/ci-cd.yml"
	@echo "  run       Run the FastAPI server"
	@echo "  clean     Remove cache and build artifacts (never touches .venv)"

install:
	$(PYTHON) -m pip install -e "$(PROJECT_DIR)[dev]"

tests:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m pytest tests --cov=src --cov-report=term-missing --cov-report=xml -q

lint:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m ruff check $(SRC_DIRS)
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m pylint --rcfile=pyproject.toml src tests main.py

mypy:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m mypy src

fix:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m ruff check --fix $(SRC_DIRS)
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m ruff format $(SRC_DIRS)

format:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m ruff format $(SRC_DIRS)

# Mesma ordem do job lint-and-tests em .github/workflows/ci-cd.yml:
# lint -> mypy -> tests. Falha rápido nos checks baratos antes da suíte.
check: lint mypy tests

ci: check

run:
    cd $(PROJECT_DIR) && $(PYTHON) -m uvicorn main:app --reload

clean:
	rm -rf $(PROJECT_DIR)/dist $(PROJECT_DIR)/build
	find . -path "*/.venv" -prune -o -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name ".coverage" -delete 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name "coverage.xml" -delete 2>/dev/null || true
