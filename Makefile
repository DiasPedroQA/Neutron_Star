.PHONY: help setup install lint format format-check test coverage test-cov \
        check dev security ci build clean pre-commit quick-check full-check \
        dev-setup bump release ci-pipeline all reset docs-html docs-clean

# Build e limpeza
# ==========================================
# Configuração do ambiente (valores fixos)
# ==========================================
VENV      := .venv
PYTHON    := $(VENV)/bin/python
PIP       := $(VENV)/bin/pip

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
	@echo "  make format        - Formatação (ruff, muta arquivos)"
	@echo "  make format-check  - Só verifica formatação, não muta"
	@echo "  make security      - Bandit + pip-audit (espelha a CI)"
	@echo "  make check         - Lint + format + test"
	@echo "  make ci            - Reproduz a pipeline de CI localmente, sem mutar nada"
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

install: ## Cria o ambiente virtual e instala dependências (dev + api, sem prod/build)
	@echo "🔧 Criando ambiente virtual e instalando dependências..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "Atoms[dev,api]"
	@echo "✅ Ambiente pronto!"

# ==========================================
# Qualidade de código (lint, formatação, tipagem, testes)
# ==========================================
lint: ## Roda o lint (ruff)
	$(PYTHON) -m ruff check Atoms Atoms/tests

format: ## Formata o código (ruff format) — MUTA os arquivos
	$(PYTHON) -m ruff format Atoms Atoms/tests

format-check: ## Só verifica formatação, sem mudar nada (o que a CI de fato roda)
	$(PYTHON) -m ruff format --check Atoms Atoms/tests

security: ## Auditoria de segurança (bandit + pip-audit), espelha o job "security" da CI
	@echo "🔒 Rodando bandit e pip-audit..."
	cd Atoms && $(CURDIR)/$(PIP) install --quiet bandit pip-audit
	cd Atoms && $(CURDIR)/$(PYTHON) -m bandit -c pyproject.toml -r src
	cd Atoms && $(PYTHON) -m pip freeze | grep -v ' @ ' > /tmp/neutron-requirements.txt
	cd Atoms && $(PYTHON) -m pip_audit -r /tmp/neutron-requirements.txt

test: ## Roda os testes unitários (usa a config completa de Atoms/pyproject.toml)
	cd Atoms && $(abspath $(PYTHON)) -m pytest

coverage: ## Roda os testes com cobertura (atalho antigo, usa addopts do pyproject.toml)
	cd Atoms && $(abspath $(PYTHON)) -m pytest --cov-report=term-missing

test-cov: ## Executa testes com cobertura detalhada (HTML, XML, term)
	@echo "📊 Executando testes com cobertura..."
	cd Atoms && $(abspath $(PYTHON)) -m pytest -v --cov-report=xml
	@echo "Relatório HTML gerado em Atoms/coverage_html/index.html"

check: lint format test ## Roda todas as verificações (sem coverage) — MUTA formatação

ci: lint format-check test-cov security ## Reproduz localmente exatamente o que a CI roda (nada muta arquivos)
	@echo "✅ Pipeline local igual à CI: passou."

dev:  ## Atalho para desenvolvimento rápido (instalação + verificações)
	@echo "📦 Instalando dependências de desenvolvimento..."
	$(PIP) install -e "Atoms[dev,api]"

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
build: ## Gera wheel e sdist (mesmo mecanismo usado na CI, job "release")
	$(PYTHON) -m pip install --quiet build
	cd Atoms && $(abspath $(PYTHON)) -m build

clean: ## Remove artefatos de build e cache
	@echo "🧹 Limpando arquivos temporários..."
	rm -rf Atoms/build/ Atoms/dist/ Atoms/*.spec
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
