<!-- Atoms/README.md -->

# 🛸 Neutron Star (módulo `Atoms`)

> Localiza, extrai e converte favoritos HTML (Netscape) para **JSON**, **CSV** e **Markdown**.
> Arquitetura **MVC** — Flask (web/SSE) + CLI compartilhando o mesmo serviço.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://mypy-lang.org/)

## Estrutura real

```text
Atoms/
├── main.py                 # Fábrica Flask: criar_aplicacao(diretorio_logs=None)
├── cli.py                  # Entrypoint da CLI (`python cli.py <comando>`)
├── src/
│   ├── models/             # Regras de negócio: buscador, conversor, escritores, entidades, excecoes
│   ├── controllers/        # api_controller (REST + SSE) e cli_controller
│   ├── views/              # templates/ e static/ (SPA, OpenAPI)
│   └── utils/              # leitor (encodings), parser (Netscape), validadores, logger_manager
└── tests/
    ├── models/  utils/  controllers/     # unitários e integração
    ├── arquitetura/                      # guardas (ex.: convenção de imports)
    ├── regressao/                        # livro de bugs (xfail strict)
    └── e2e/                              # Playwright (a implementar)
```

## Convenções obrigatórias

1. **Import único**: código importado sempre como `src.*` (relativo dentro de `src/`).
   Proibido `from models...` / `from utils...`. Guardado por `tests/arquitetura/`.
2. **Sem `__init__.py` na raiz `Atoms/`** (duplicaria a identidade dos módulos).
3. **Testes**: pytest puro, tipagem explícita, nomes em português, ciclo Red → Green → Refactor.
4. **Bug confirmado sem correção imediata** → teste em `tests/regressao/` com `xfail(strict=True)`.
5. **Testes nunca escrevem em `Atoms/logs/`**: usar `criar_aplicacao(diretorio_logs=tmp_path)`.

## Comandos (a partir da raiz do repositório)

| Comando | O que faz |
| :--- | :--- |
| `make env` | Cria `.venv`, instala `Atoms[dev]`, hooks e Playwright |
| `make quality` | Ruff + Pylint + MyPy |
| `make test` | Pytest com cobertura (gera `Atoms/coverage.xml`; falha abaixo de `fail_under`) |
| `make test-e2e` | Testes ponta a ponta (Playwright) |
| `make ci` | `quality` + `test` (gate de merge) |
| `make app-web` / `make app-cli ARGS="sistema"` | Executa a aplicação |

## API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/sistema` | SO, usuário e atalhos da Home |
| `GET` | `/api/escanear` | Varredura de pastas (`caminho`, `extensao`, `profundidade`) |
| `POST` | `/api/processar` | Conversão em lote com progresso via SSE |

Contrato completo: `src/views/static/openapi.yaml`.

## Débitos conhecidos

Ver `tests/regressao/test_bugs_conhecidos.py` (BUG-001 a BUG-003) e o backlog no relatório de auditoria.
