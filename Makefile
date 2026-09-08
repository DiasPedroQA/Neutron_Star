# Mapeamento do interpretador do ambiente virtual oculto na raiz
# $(CURDIR) é a raiz do repositório (onde o make foi chamado) — precisa ser
# caminho absoluto porque as receitas abaixo fazem "cd $(PROJECT_DIR)" antes
# de invocar o Python, e um caminho relativo quebraria depois desse cd.
PYTHON := $(CURDIR)/.venv/bin/python
PROJECT_DIR := Atoms
SRC_DIRS := src tests main.py
RUN := cd $(PROJECT_DIR) && PYTHONPATH=. $(PYTHON)

.PHONY: help \
	setup install \
	run \
	lint mypy fix format quality \
	test ci \
	clean

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
	@echo "  Limpeza"
	@echo "    clean         Limpa caches temporários do Python (preserva o .venv)"

##@ Ambiente -------------------------------------------------------------

# Cria o .venv físico se ele não existir e instala os pacotes
setup:
	@if [ ! -d ".venv" ]; then \
		echo "📦 Criando ambiente virtual oculto .venv..."; \
		python3 -m venv .venv; \
	fi
	@$(MAKE) install

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(PROJECT_DIR)/requirements-dev.txt

##@ Execução --------------------------------------------------------------

# Inicia o servidor Flask com depurador ativo
run:
	cd $(PROJECT_DIR) && FLASK_DEBUG=1 PYTHONPATH=. $(PYTHON) main.py

##@ Qualidade --------------------------------------------------------------

lint:
	$(RUN) -m ruff check $(SRC_DIRS)
	$(RUN) -m pylint --rcfile=pyproject.toml src tests main.py

mypy:
	$(RUN) -m mypy src

# Roda as duas checagens estáticas de uma vez só
quality: lint mypy

fix:
	$(RUN) -m ruff check --fix $(SRC_DIRS)
	$(RUN) -m ruff format $(SRC_DIRS)

format:
	$(RUN) -m ruff format $(SRC_DIRS)

##@ Testes e CI --------------------------------------------------------------

test:
	$(RUN) -m pytest tests

# Pipeline de checagem completo do CI: qualidade estática + testes
ci: quality test

##@ Limpeza --------------------------------------------------------------

# Limpeza profunda de resíduos temporários de build e cache
clean:
	find . -path "*/.venv" -prune -o -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name ".coverage" -delete 2>/dev/null || true
	find . -path "*/.venv" -prune -o -type f -name "coverage.xml" -delete 2>/dev/null || true
