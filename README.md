<!-- README.md -->

# Neutron Star

> **Localizador, Extrator e Conversor Inteligente de Favoritos HTML (Netscape Standard) em Arquitetura Hexagonal**

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/architecture-Hexagonal%20(Ports%20%26%20Adapters)-orange.svg)]
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checker: mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://mypy-lang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📖 Visão Geral

O **Neutron Star** é uma aplicação robusta para localizar arquivos HTML de favoritos exportados por navegadores web, extrair sua estrutura hierárquica e convertê-los de forma inteligente para **CSV** (compatível com Microsoft Excel Brasil) ou **JSON**, utilizando uma interface web reativa com streaming em tempo real via Server-Sent Events (SSE).

O código-fonte e o núcleo executável estão isolados na subpasta [`Atoms/`](../Neutron_Star/README.md).

---

## 🚀 Recursos Principais

- **Arquitetura Hexagonal:** Desacoplamento absoluto entre as regras de negócio de domínio e as tecnologias de entrega (Flask, BeautifulSoup, etc.).
- **Varredura e Escaneamento Rápido:** Busca recursiva otimizada na Home (`~/`) do usuário em busca de arquivos HTML elegíveis de favoritos.
- **Streaming de Progresso Real (SSE):** Monitoramento visual do progresso de conversão de lote em tempo real através de Server-Sent Events no Flask.
- **Segurança Corporativa Ativa:** Tratamento de segurança que impede vulnerabilidades de *Path Traversal*, forçando caminhos seguros e válidos dentro do escopo da Home do usuário.
- **Interface Deep Space Obsidian:** Visual de alto padrão com efeitos de morfismo de vidro fosco (*glassmorphism*), feedback físico de linhas de tabela e barras de progresso dinâmicas.

---

## 📂 Estrutura de Pastas do Repositório

```text
Neutron_Star/
├── .github/                    # CI/CD (Workflows do GitHub Actions e Composite Actions)
├── Atoms/                      # Código-fonte centralizado da aplicação
│   ├── src/                    # Camadas Hexagonais (Domínio, Aplicação, Infra, Adaptadores)
│   ├── tests/                  # Suíte completa de testes (Unitários, Integração e E2E)
│   ├── main.py                 # Ponto de partida (Entrypoint) do servidor Flask
│   ├── pyproject.toml          # Configurações do pacote, linters (Ruff, Pylint, Mypy) e pytest
│   └── requirements.txt        # Dependências de execução
├── .venv/                      # Ambiente virtual Python isolado (não versionado)
├── Makefile                    # Automação de comandos e ciclo de vida do projeto
├── MANUAL_TESTES.md            # Guia completo de cobertura e cenários de teste
├── LICENSE                     # Termos de licença do software
├── run_app.sh                  # Script de execução rápida para Linux
└── run_app.bat                 # Script de execução rápida para Windows
```

---

## 🛠️ Desenvolvimento e Execução Rápida

O projeto fornece um **`Makefile`** na raiz para automatizar todo o ciclo de vida do ambiente local:

### 1. Provisionar o Ambiente (.venv + Dependências)

```bash
make setup
```

### 2. Rodar o Servidor Localmente

Inicia a aplicação Flask em modo de desenvolvimento em `http://127.0.0.1:5000`:

```bash
make run
```

*(Alternativamente, você também pode usar `./run_app.sh` no Linux ou `run_app.bat` no Windows).*

### 3. Rodar a Suíte de Testes (Unitários e Integração)

```bash
make test
```

### 4. Rodar Testes End-to-End (E2E com Playwright)

```bash
make e2e
```

### 5. Validação Geral e Linters (CI Gate)

Executa a esteira completa de validação estática de tipos, formatação e qualidade de código exigidas no CI/CD (Ruff + Pylint + Mypy + Testes):

```bash
make ci
```

---

## 🔒 Recomendações Importantes de Segurança

1. **Ambiente Confiável:** Não exponha a porta da API pública diretamente na internet sem uma camada robusta de proxy reverso e autenticação. O aplicativo lê e escreve arquivos locais do servidor com base nos caminhos autorizados.
2. **Restrição Física de Escopo:** O aplicativo possui segurança ativa que restringe varreduras estritamente a pastas dentro do diretório Home do usuário ativo. Tentativas de acessar pastas sistêmicas do S.O. (como `/etc`, `/var`, `/windows`) retornarão o status HTTP `403 Forbidden`.

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
