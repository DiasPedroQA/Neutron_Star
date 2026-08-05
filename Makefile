.PHONY: all help install test lint format check ci build release clean docs

# ============================================================================
# 🐚 Neutron Star — comandos disponíveis
# ============================================================================

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

all: install ci build docs ## Executa todos os comandos principais em sequência (instala, verifica, constrói e gera docs)
	@echo ""
	@echo "🎉 Tudo pronto! O projeto foi instalado, verificado, empacotado e documentado."
	@echo ""

help: ## Mostra esta ajuda
	@echo ""
	@echo "🐚 Neutron Star — comandos disponíveis"
	@echo ""
	@echo "  make all      🚀 Executa tudo: install → ci → build → docs"
	@echo "  make install   📦 Cria o ambiente e instala tudo (comece por aqui)"
	@echo "  make test      🧪 Roda os testes"
	@echo "  make lint      🔍 Verifica o estilo do código (ruff)"
	@echo "  make format    🎨 Corrige o estilo do código automaticamente"
	@echo "  make check     ✅ lint + format + test, tudo de uma vez"
	@echo "  make ci        🤖 Reproduz a pipeline do GitHub Actions localmente"
	@echo "  make build     🏗️  Gera o pacote (wheel/sdist) para distribuição"
	@echo "  make release   🚀 clean + check + build, pronto para publicar"
	@echo "  make docs      📚 Gera a documentação (Sphinx)"
	@echo "  make clean     🧹 Remove caches e arquivos temporários"
	@echo ""

# ============================================================================
# 📦 Ambiente
# ============================================================================

install: ## Cria o venv e instala as dependências (dev + api)
	@echo "🔧 Preparando o ambiente..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -e "Atoms[dev,api]" --quiet
	@echo "✅ Pronto! Use 'make check' pra conferir se está tudo funcionando."

# ============================================================================
# 🧪 Qualidade de código
# ============================================================================

test: ## Roda os testes com cobertura
	cd Atoms && $(abspath $(PYTHON)) -m pytest --cov-report=term-missing

lint: ## Verifica o estilo do código, sem mudar nada
	$(PYTHON) -m ruff check Atoms Atoms/tests
	$(PYTHON) -m ruff format --check Atoms Atoms/tests

format: ## Corrige o estilo do código automaticamente
	$(PYTHON) -m ruff format Atoms Atoms/tests
	$(PYTHON) -m ruff check --fix Atoms Atoms/tests

check: lint test ## Roda lint + testes, tudo de uma vez (não muda nada)
	@echo "✅ Tudo certo — código limpo e testes passando."

# ============================================================================
# 🤖 Espelho da CI (o que roda no GitHub Actions)
# ============================================================================

ci: ## Reproduz localmente a pipeline inteira: lint, testes, segurança
	@echo "🤖 Rodando a mesma checagem da CI..."
	$(PYTHON) -m ruff check Atoms Atoms/tests
	$(PYTHON) -m ruff format --check Atoms Atoms/tests
	cd Atoms && $(abspath $(PYTHON)) -m pytest --cov-report=xml
	$(PIP) install --quiet bandit pip-audit
	cd Atoms && $(abspath $(PYTHON)) -m bandit -c pyproject.toml -r src
	cd Atoms && $(abspath $(PYTHON)) -m pip_audit
	@echo "✅ Pipeline local passou — pode dar push tranquilo."

# ============================================================================
# 🏗️ Build, release e documentação
# ============================================================================

build: ## Gera o pacote (wheel + sdist)
	$(PIP) install --quiet build
	cd Atoms && $(abspath $(PYTHON)) -m build

release: clean check build ## Prepara uma versão pronta para publicar
	@echo "📦 Release pronto em Atoms/dist/"

docs: ## Gera a documentação HTML (Sphinx)
	$(PYTHON) -m sphinx -b html docs docs/_build/html
	@echo "📚 Documentação em docs/_build/html/index.html"

# ============================================================================
# 🧹 Limpeza
# ============================================================================

clean: ## Remove caches, builds e arquivos temporários
	@echo "🧹 Limpando..."
	rm -rf Atoms/build Atoms/dist Atoms/*.egg-info
	rm -rf Atoms/coverage_html Atoms/.coverage Atoms/coverage.xml
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" \) -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Limpo."
