.PHONY: help install lint format typecheck test clean build

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Cria o ambiente virtual e instala dependências
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

lint: ## Roda o lint (ruff)
	$(PYTHON) -m ruff check src tests

format: ## Formata o código (ruff format)
	$(PYTHON) -m ruff format src tests

typecheck: ## Verifica tipagem (mypy)
	$(PYTHON) -m mypy src

test: ## Roda os testes
	$(PYTHON) -m pytest

check: lint format typecheck test ## Roda todas as verificações

build: ## Gera o executável com PyInstaller
	$(PYTHON) -m PyInstaller --onefile --name neutron-star src/presentation/cli.py

clean: ## Remove artefatos de build
	rm -rf build/ dist/ *.spec
	find . -type d -name __pycache__ -exec rm -rf {} +
