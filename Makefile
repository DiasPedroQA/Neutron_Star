.PHONY: help setup install lint format test coverage check build clean \
        review-code review-tests review-full review-docs review-ci apply-fix \
        pre-commit quick-check full-check dev-setup bump release review-all ci-pipeline \
        reset docs-html docs-clean

# Build e limpeza
# ==========================================
# Configuração do ambiente (valores fixos)
# ==========================================
VENV      := .venv
PYTHON    := $(VENV)/bin/python
PIP       := $(VENV)/bin/pip

# Modelo de IA e URL – fixos, sem necessidade de sobrescrever
AI_MODEL     := llama3.2:1b
AI_BASE_URL  := http://localhost:11434

# ==========================================
# Ajuda
# ==========================================
help: ## Mostra esta ajuda
	@echo "🐚 Neutron Star - Comandos disponíveis:"
	@echo ""
	@echo "Setup:"
	@echo "  make setup         - Configura ambiente completo (venv + dependências + check)"
	@echo "  make install       - Cria venv e instala dependências"
	@echo "  make dev-setup     - Prepara ambiente de desenvolvimento"
	@echo ""
	@echo "Testes:"
	@echo "  make test          - Executa testes localmente"
	@echo "  make test-cov      - Executa testes com cobertura"
	@echo ""
	@echo "Qualidade:"
	@echo "  make lint          - Lint (ruff)"
	@echo "  make format        - Formatação (ruff)"
	@echo "  make check         - Lint + format + test"
	@echo "  make docs-html     - Gera documentação Sphinx em docs/_build/html"
	@echo ""
	@echo "Limpeza:"
	@echo "  make clean         - Remove artefatos de build e cache"
	@echo "  make reset         - Limpa tudo (venv, caches) e prepara para novo setup"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ==========================================
# Ambiente e dependências
# ==========================================
setup: install check ## Configura o ambiente completo (instalar + verificações)
	@echo "✅ Ambiente configurado."

install: ## Cria o ambiente virtual e instala dependências
	@echo "🔧 Criando ambiente virtual e instalando dependências..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	@echo "✅ Ambiente pronto!"

# ==========================================
# Qualidade de código (lint, formatação, tipagem, testes)
# ==========================================
lint: ## Roda o lint (ruff)
	$(PYTHON) -m ruff check Atoms Atoms/tests

format: ## Formata o código (ruff format)
	$(PYTHON) -m ruff format Atoms Atoms/tests

test: ## Roda os testes unitários
	$(PYTHON) -m pytest

coverage: ## Roda os testes com cobertura (atalho antigo)
	$(PYTHON) -m pytest --cov=Atoms --cov-report=term-missing

test-cov: ## Executa testes com cobertura detalhada (HTML, XML, term)
	@echo "📊 Executando testes com cobertura..."
	$(PYTHON) -m pytest Atoms/tests/ -v --cov=Atoms --cov-report=term --cov-report=html --cov-report=xml
	@echo "Relatório HTML gerado em htmlcov/index.html"

check: lint format test ## Roda todas as verificações (sem coverage)

dev:  ## Atalho para desenvolvimento rápido (instalação + verificações)
	@echo "📦 Instalando dependências de desenvolvimento..."
	$(PIP) install -r requirements-dev.txt
	$(PIP) install pre-commit

quick-check: lint format ## Verificações rápidas (sem testes)
	@echo "✅ Lint, formatação e tipagem OK."

full-check: lint format test coverage ## Verificações completas + cobertura
	@echo "✅ Todas as verificações e testes passaram."

pre-commit: lint format ## Verificações para pré-commit (rápido)

# ==========================================
# Documentação
# ==========================================
docs-html: ## Gera documentação HTML com Sphinx
	$(PYTHON) -m sphinx -b html docs docs/_build/html

docs-clean: ## Remove documentação gerada pelo Sphinx
	rm -rf docs/_build

# ==========================================
# Build e limpeza
# ==========================================
build: ## Gera o executável com PyInstaller
	$(PYTHON) -m PyInstaller --onefile --name neutron-star Atoms/frontend/cli/main.py

clean: ## Remove artefatos de build e cache
	@echo "🧹 Limpando arquivos temporários..."
	rm -rf build/ dist/ *.spec
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find docs -type d -name "_build" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true  # ← LINHA CORRIGIDA
	@echo "✅ Clean completed!"


# ==========================================
# Combinações e fluxos de trabalho
# ==========================================
dev-setup: install check ## Prepara o ambiente de desenvolvimento
	@echo "🚀 Ambiente de desenvolvimento pronto!"

bump: clean install test ## Atualiza dependências e testa
	@echo "📦 Dependências atualizadas e testadas."

release: clean full-check build ## Gera uma versão para distribuição
	@echo "📦 Pacote de release criado."

ci-pipeline: clean install full-check build ## Pipeline completa de CI/CD
	@echo "🏁 Pipeline concluída. Artefato em dist/"

# Mantido por compatibilidade
all: ci-pipeline ## Atalho para a pipeline completa (CI/CD)

reset: clean ## Reset completo do ambiente local
	@echo "🔄 Reset completo do ambiente..."
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf htmlcov
	@echo "Execute 'make install' ou 'make setup' para recriar o ambiente"
