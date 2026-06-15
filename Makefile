.PHONY: help setup install lint format typecheck test coverage check build clean \
        review-code review-tests review-full review-docs review-ci apply-fix \
        pre-commit quick-check full-check dev-setup bump release review-all ci-pipeline \
        test-ubuntu-docker test-debian-docker test-alpine-docker test-all-docker \
        test-parallel-docker docker-clean test-cov clean-docker reset docs-html docs-clean

# Build e limpeza
# ==========================================
# ==========================================
# Testes cross-platform com Docker
# ==========================================

test-ubuntu-docker: ## Roda testes em container Ubuntu (python:3.11)
	@echo "🐧 Testando no Ubuntu (Docker)..."
	docker run --rm \
		-v "$$PWD":/app \
		-w /app \
		-e PYTHONDONTWRITEBYTECODE=1 \
		python:3.11 \
		bash -c "pip install -q -r requirements-dev.txt && pytest -v --tb=short"

test-debian-docker: ## Roda testes em container Debian
	@echo "🎯 Testando no Debian (Docker)..."
	docker run --rm \
		-v "$$PWD":/app \
		-w /app \
		debian:latest \
		bash -c "apt-get update -qq && apt-get install -y -qq python3-venv python3-pip > /dev/null && python3 -m venv /tmp/venv && /tmp/venv/bin/pip install --upgrade pip > /dev/null && /tmp/venv/bin/pip install -q -r requirements-dev.txt && /tmp/venv/bin/pytest -v --tb=short"

test-alpine-docker: ## Roda testes em container Alpine (imagem leve)
	@echo "🏔️ Testando no Alpine (Docker)..."
	docker run --rm \
		-v "$$PWD":/app \
		-w /app \
		python:3.11-alpine \
		sh -c "apk add --no-cache gcc musl-dev linux-headers > /dev/null && python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -q -r requirements-dev.txt && /tmp/venv/bin/pytest -v --tb=short"

test-all-docker: test-ubuntu-docker test-debian-docker test-alpine-docker ## Roda testes Docker em todas distros
	@echo "✅ Testes Docker concluídos em Ubuntu, Debian e Alpine."

test-parallel-docker: ## Roda testes Docker em paralelo via docker-compose
	@echo "🚀 Executando testes Docker em paralelo..."
	@if [ -f docker-compose.test.yml ]; then \
		if command -v docker-compose >/dev/null 2>&1; then \
			docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test-ubuntu; \
		elif docker compose version >/dev/null 2>&1; then \
			docker compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test-ubuntu; \
		else \
			echo "⚠️ Nenhum docker-compose disponível para test-parallel-docker"; exit 1; \
		fi; \
	else \
		echo "⚠️ docker-compose.test.yml não encontrado; pulando test-parallel-docker"; exit 1; \
	fi

docker-clean: ## Limpa containers/volumes relacionados a testes Docker
	@echo "🧹 Limpando containers e volumes Docker..."
	@if [ -f docker-compose.test.yml ]; then \
		if command -v docker-compose >/dev/null 2>&1; then \
			docker-compose -f docker-compose.test.yml down -v; \
		elif docker compose version >/dev/null 2>&1; then \
			docker compose -f docker-compose.test.yml down -v; \
		else \
			echo "⚠️ Nenhum docker-compose disponível para docker-clean"; \
		fi; \
	else \
		echo "⚠️ docker-compose.test.yml não encontrado; pulando docker-clean"; \
	fi
	docker container prune -f
	docker volume prune -f

clean-docker: docker-clean ## Alias para limpeza de Docker

# ==========================================
# Build e limpeza
# =================================================
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
	@echo "  make test-ubuntu-docker   - Testes em Docker (Ubuntu)"
	@echo "  make test-debian-docker   - Testes em Docker (Debian)"
	@echo "  make test-alpine-docker   - Testes em Docker (Alpine)"
	@echo "  make test-all-docker      - Todos os testes Docker"
	@echo "  make test-parallel-docker - Testes Docker em paralelo (docker-compose)"
	@echo ""
	@echo "Qualidade:"
	@echo "  make lint          - Lint (ruff)"
	@echo "  make format        - Formatação (ruff)"
	@echo "  make typecheck     - Tipagem (mypy)"
	@echo "  make check         - Lint + format + typecheck + test"
	@echo "  make docs-html     - Gera documentação Sphinx em docs/_build/html"
	@echo ""
	@echo "Limpeza:"
	@echo "  make clean         - Remove artefatos de build e cache"
	@echo "  make clean-docker  - Remove containers e volumes Docker"
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

typecheck: ## Verifica tipagem (mypy)
	$(PYTHON) -m mypy Atoms

test: ## Roda os testes unitários
	$(PYTHON) -m pytest

coverage: ## Roda os testes com cobertura (atalho antigo)
	$(PYTHON) -m pytest --cov=Atoms --cov-report=term-missing

test-cov: ## Executa testes com cobertura detalhada (HTML, XML, term)
	@echo "📊 Executando testes com cobertura..."
	$(PYTHON) -m pytest Atoms/tests/ -v --cov=Atoms --cov-report=term --cov-report=html --cov-report=xml
	@echo "Relatório HTML gerado em htmlcov/index.html"

check: lint format typecheck test ## Roda todas as verificações (sem coverage)

dev:  ## Atalho para desenvolvimento rápido (instalação + verificações)
	@echo "📦 Instalando dependências de desenvolvimento..."
	$(PIP) install -r requirements-dev.txt
	$(PIP) install pre-commit

quick-check: lint format typecheck ## Verificações rápidas (sem testes)
	@echo "✅ Lint, formatação e tipagem OK."

full-check: lint format typecheck test coverage ## Verificações completas + cobertura
	@echo "✅ Todas as verificações e testes passaram."

pre-commit: lint format typecheck ## Verificações para pré-commit (rápido)

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
# Agentes de IA (review e aplicação)
# ==========================================
# Comportamento padrão: analisar TODO o código do projeto (diretório raiz '.')
# Para analisar apenas um arquivo ou pasta específica, use: make review-code FILE=Atoms/meu_arquivo.py

FILE ?= .

review-code: ## Placeholder: Análise de IA ainda não implementada localmente
	@echo "⚠️ O comando review-code ainda não está disponível. Implemente a CLI de IA ou remova este target."

review-tests: ## Placeholder: Análise de IA ainda não implementada localmente
	@echo "⚠️ O comando review-tests ainda não está disponível. Implemente a CLI de IA ou remova este target."

review-full: ## Placeholder: Análise de IA ainda não implementada localmente
	@echo "⚠️ O comando review-full ainda não está disponível. Implemente a CLI de IA ou remova este target."

review-dup: ## Placeholder: Análise de IA ainda não implementada localmente
	@echo "⚠️ O comando review-dup ainda não está disponível. Implemente a CLI de IA ou remova este target."

review-docs: ## Placeholder: Análise de IA ainda não implementada localmente
	@echo "⚠️ O comando review-docs ainda não está disponível. Implemente a CLI de IA ou remova este target."

review-ci: ## Placeholder: Análise de IA ainda não implementada localmente
	@echo "⚠️ O comando review-ci ainda não está disponível. Implemente a CLI de IA ou remova este target."

apply-fix: ## Placeholder: Aplica correções da IA diretamente em um arquivo (não implementado)
	@echo "⚠️ O comando apply-fix ainda não está disponível. Implemente a CLI de IA ou remova este target."

review-all: review-code review-tests review-full review-docs review-ci ## Dispara todas as revisões da IA
	@echo "🤖 Revisão completa pela IA finalizada."

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

reset: clean clean-docker ## Reset completo do ambiente local e Docker
	@echo "🔄 Reset completo do ambiente..."
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf htmlcov
	@echo "Execute 'make install' ou 'make setup' para recriar o ambiente"
