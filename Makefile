# =============================================================================
# 🛸 NEUTRON STAR — AUTOMATION PIPELINE (MVC ARCHITECTURE)
# =============================================================================

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# 🔧 Configurações de Ambiente e Binários
# -----------------------------------------------------------------------------
VENV        := .venv
BIN         := $(VENV)/bin
PYTHON      := $(BIN)/python
PIP         := $(BIN)/pip
PYTEST      := $(BIN)/pytest
RUFF        := $(BIN)/ruff
MYPY        := $(BIN)/mypy
PYLINT      := $(BIN)/pylint
PLAYWRIGHT  := $(BIN)/playwright
PRE_COMMIT  := $(BIN)/pre-commit

# Prefixo padrão de execução contextualizada na pasta Atoms
RUN_ATOMS   := cd Atoms && PYTHONPATH=. ../

# -----------------------------------------------------------------------------
# 📖 Ajuda e Documentação do Pipeline
# -----------------------------------------------------------------------------
.PHONY: help
help:
	@echo "====================================================================="
	@echo "🛸 NEUTRON STAR — COMANDOS DE AUTOMAÇÃO"
	@echo "====================================================================="
	@echo "📦 1. GESTÃO DE AMBIENTE (ENV):"
	@echo "  make env                 - Instala e configura o ambiente completo"
	@echo "  make env-deps            - Atualiza dependências do projeto e dev"
	@echo "  make env-hooks           - Instala hooks de Git (pre-commit e pre-push)"
	@echo "  make env-e2e             - Instala navegadores do Playwright"
	@echo ""
	@echo "🔍 2. QUALIDADE E ANÁLISE ESTÁTICA (QUALITY):"
	@echo "  make quality             - Executa toda a suíte de qualidade (Ruff + Pylint + MyPy)"
	@echo "  make quality-lint        - Executa checagem de estilo com Ruff"
	@echo "  make quality-format      - Auto-formata todo o código com Ruff"
	@echo "  make quality-pylint      - Executa análise de conformidade do Pylint (10/10)"
	@echo "  make quality-types       - Executa checagem estática de tipos com MyPy"
	@echo ""
	@echo "🧪 3. SUÍTE DE TESTES (TEST):"
	@echo "  make test                - Executa todos os testes unitários e de integração com cobertura"
	@echo "  make test-models         - Executa apenas os testes da camada Model"
	@echo "  make test-controllers    - Executa apenas os testes dos Controladores (API + CLI)"
	@echo "  make test-utils          - Executa testes de utilitários e integridade de tipos"
	@echo "  make test-e2e            - Executa testes ponta a ponta (E2E Playwright)"
	@echo "  make test-report         - Gera relatório HTML de cobertura (htmlcov/index.html)"
	@echo ""
	@echo "🚀 4. EXECUÇÃO DA APLICAÇÃO (APP):"
	@echo "  make app-web             - Inicia o servidor Web Flask local"
	@echo "  make app-cli             - Executa comando na CLI (ex: make app-cli ARGS=\"sistema\")"
	@echo ""
	@echo "🚢 5. PIPELINES CONSOLIDADOS (CI/CD):"
	@echo "  make ci                  - Pipeline completo de validação (Quality + Testes)"
	@echo "  make clean               - Remove todos os caches, logs e artefatos de build"
	@echo "====================================================================="

# =============================================================================
# 📦 1. GESTÃO DE AMBIENTE (ENV)
# =============================================================================
.PHONY: env env-deps env-hooks env-e2e

env: env-deps env-hooks env-e2e
	@echo "✨ Ambiente configurado e pronto para desenvolvimento!"

env-deps:
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -e "Atoms[dev]"

env-hooks:
	@$(PRE_COMMIT) install
	@$(PRE_COMMIT) install --hook-type pre-push

env-e2e:
	@$(PLAYWRIGHT) install --with-deps chromium

# =============================================================================
# 🔍 2. QUALIDADE E ANÁLISE ESTÁTICA (QUALITY)
# =============================================================================
.PHONY: quality quality-lint quality-format quality-pylint quality-types

quality: quality-lint quality-pylint quality-types
	@echo "🛡️ Todas as checagens de qualidade passaram com sucesso!"

quality-lint:
	@echo "🔹 [1/3] Verificando linting e ordenação com Ruff..."
	@$(RUN_ATOMS)$(RUFF) check src tests cli.py main.py

quality-format:
	@echo "🔹 Auto-formatando código com Ruff..."
	@$(RUN_ATOMS)$(RUFF) check --fix src tests cli.py main.py
	@$(RUN_ATOMS)$(RUFF) format src tests cli.py main.py

quality-pylint:
	@echo "🔹 [2/3] Verificando regras de código com Pylint..."
	@$(RUN_ATOMS)$(PYLINT) src tests cli.py main.py

quality-types:
	@echo "🔹 [3/3] Checando tipagem estática com MyPy..."
	@$(RUN_ATOMS)$(MYPY) src tests cli.py main.py

# =============================================================================
# 🧪 3. SUÍTE DE TESTES (TEST)
# =============================================================================
.PHONY: test test-models test-controllers test-utils test-e2e test-report

test:
	@echo "🧪 Executando todos os testes unitários e de integração..."
	@$(RUN_ATOMS)$(PYTEST) -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml tests/

test-models:
	@echo "🧠 Executando testes da camada Model..."
	@$(RUN_ATOMS)$(PYTEST) -v tests/models/

test-controllers:
	@echo "🕹️ Executando testes dos Controllers..."
	@$(RUN_ATOMS)$(PYTEST) -v tests/controllers/

test-utils:
	@echo "🛠️ Executando testes dos Utilitários..."
	@$(RUN_ATOMS)$(PYTEST) -v tests/utils/

test-e2e:
	@echo "🎭 Executando testes End-to-End com Playwright..."
	@$(RUN_ATOMS)$(PYTEST) -v tests/e2e/

test-report:
	@echo "📊 Gerando relatório de cobertura em HTML..."
	@$(RUN_ATOMS)$(PYTEST) --cov=src --cov-report=html:../htmlcov tests/
	@echo "📄 Relatório disponível em: htmlcov/index.html"

# =============================================================================
# 🚀 4. EXECUÇÃO DA APLICAÇÃO (APP)
# =============================================================================
.PHONY: app-web app-cli run cli

app-web:
	@$(RUN_ATOMS)$(PYTHON) main.py

app-cli:
	@$(RUN_ATOMS)$(PYTHON) cli.py $(ARGS)

# Aliases de compatibilidade rápida
run: app-web
cli: app-cli

# =============================================================================
# 🚢 5. PIPELINES CONSOLIDADOS (CI/CD) & LIMPEZA
# =============================================================================
.PHONY: ci clean clean-cache clean-logs clean-build

ci: quality test
	@echo "🚀 Pipeline de CI aprovado para deploy/push!"

clean: clean-cache clean-logs clean-build
	@echo "🧹 Limpeza completa concluída com sucesso!"

clean-cache:
	@rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

clean-logs:
	@rm -rf Atoms/logs/*.txt Atoms/logs/*.log test-results/ playwright-report/

clean-build:
	@rm -rf htmlcov/ dist/ build/ Atoms/build/ Atoms/dist/ *.egg-info Atoms/*.egg-info
