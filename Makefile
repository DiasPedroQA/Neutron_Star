# Mapeamento do interpretador do ambiente virtual na raiz
PYTHON := $(CURDIR)/.venv/bin/python
PROJECT_DIR := Atoms
SRC_DIRS := src tests main.py
RUN := cd $(PROJECT_DIR) && PYTHONPATH=src:. $(PYTHON)

.PHONY: help \
    setup install \
    run \
    lint mypy fix format quality \
    test ci \
    clean \
    e2e-install e2e

help:
	@echo "Comandos disponíveis no Neutron Star:"
	@echo ""
	@echo "  Ambiente"
	@echo "    setup         Cria o .venv e instala todas as dependências"
	@echo "    install       Instala as dependências (runtime + dev: ruff/mypy/pylint) no .venv"
	@echo ""
	@echo "  Execução"
	@echo "    run           Inicia o servidor de desenvolvimento Flask"
	@echo ""
	@echo "  Qualidade"
	@echo "    lint          Executa análise estática de código (Ruff + Pylint)"
	@echo "    mypy          Executa checagem de tipos estáticos"
	@echo "    quality       Roda lint + mypy de uma vez"
	@echo "    fix           Aplica correções automáticas e formata o código"
	@echo "    format        Formata o código usando o Ruff"
	@echo ""
	@echo "  Testes e CI"
	@echo "    test          Executa todos os testes unitários e de integração (pytest)"
	@echo "    ci            Valida todo o projeto (quality + test) antes de subir"
	@echo ""
	@echo "  E2E"
	@echo "    e2e-install   Instala os navegadores do Playwright"
	@echo "    e2e           Executa os testes End-to-End"
	@echo ""
	@echo "  Limpeza"
	@echo "    clean         Limpa caches temporários do Python (preserva o .venv)"

##@ Ambiente -------------------------------------------------------------

setup:
	@if [ ! -d ".venv" ]; then \
		echo "📦 Criando ambiente virtual .venv..."; \
		python3 -m venv .venv; \
	fi
	@$(MAKE) install

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e "$(PROJECT_DIR)[dev]"

##@ Execução --------------------------------------------------------------

run:
	cd $(PROJECT_DIR) && FLASK_DEBUG=1 PYTHONPATH=src:. $(PYTHON) main.py

##@ Qualidade --------------------------------------------------------------

lint:
	$(RUN) -m ruff check $(SRC_DIRS)
	$(RUN) -m pylint --rcfile=pyproject.toml src tests main.py

mypy:
	$(RUN) -m mypy src

quality: lint mypy

fix:
	$(RUN) -m ruff check --fix $(SRC_DIRS)
	$(RUN) -m ruff format $(SRC_DIRS)

format:
	$(RUN) -m ruff format $(SRC_DIRS)

##@ Testes e CI --------------------------------------------------------------

test:
	$(RUN) -m pytest tests --cov=src --cov-report=term-missing -m "not e2e"

ci: quality test

##@ Testes E2E -------------------------------------------------------------

e2e-install:
	$(PYTHON) -m playwright install chromium --with-deps

e2e:
	$(RUN) -m pytest tests/e2e -m e2e

##@ Limpeza --------------------------------------------------------------

clean:
	find . -path "*/.venv" -prune -o -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name ".coverage" -delete 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name "coverage.xml" -delete 2>/dev/null || true
