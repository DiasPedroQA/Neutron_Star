PYTHON ?= python
PROJECT_DIR := Atoms

.PHONY: install test lint format check run

install:
	$(PYTHON) -m pip install -e "$(PROJECT_DIR)[dev]"

test:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m pytest tests -q

lint:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m ruff check src tests main.py
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m pylint src tests main.py

format:
	cd $(PROJECT_DIR) && PYTHONPATH=src $(PYTHON) -m ruff format src tests main.py

check: test lint

run:
	cd $(PROJECT_DIR) && $(PYTHON) main.py
