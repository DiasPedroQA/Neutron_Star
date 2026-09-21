<!-- Atoms/README.md -->

# 🛸 Neutron Star (Módulo Atoms)

> **Núcleo Técnico, API e Camada de Aplicação em Arquitetura Hexagonal (Ports & Adapters)**

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/architecture-Hexagonal%20(Ports%20%26%20Adapters)-orange.svg)]
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checker: mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://mypy-lang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)

---

## 📖 Visão Geral do Pacote

O diretório **`Atoms/`** contém o código-fonte executável, a suíte de testes e os contratos de infraestrutura do **Neutron Star**. A aplicação foi projetada para ser desacoplada, resiliente a falhas de arquivos e 100% tipada.

---

## 🏛️ Estrutura Interna das Camadas

A pasta `src/` está organizada de acordo com a **Arquitetura Hexagonal**:

```text
Atoms/
├── src/
│   ├── dominio/          # Camada de Domínio: Entidades puras imutáveis, tipos canônicos e exceções
│   │   ├── entidades.py  # Favorito (@dataclass frozen), TypedDicts de transporte
│   │   └── excecoes.py   # Hierarquia de erros de domínio (ErroDominio)
│   │
│   ├── aplicacao/        # Camada de Casos de Uso e Portas Abstratas (Inbound/Outbound)
│   │   ├── portas.py     # Contratos abstratos (LeitorHTMLPort, BuscadorPort, EscritorPort, etc.)
│   │   └── casos_uso.py  # Orquestração de negócio e barreira de segurança Path Traversal
│   │
│   ├── infra/            # Camada de Infraestrutura: Adaptadores concretos de I/O
│   │   ├── buscador.py   # Varredura do SO e montagem da árvore hierárquica
│   │   ├── conteiner.py  # Composition Root (Injeção de Dependências centralizada)
│   │   ├── escritores.py # Estratégias de persistência física (JSON e CSV)
│   │   ├── leitor.py     # Leitor físico resiliente com cascata de encodings
│   │   └── parser.py     # Parser recursivo Netscape usando BeautifulSoup4
│   │
│   ├── adaptadores/      # Camada de Interface / Delivery (HTTP / REST)
│   │   ├── api.py        # Flask Blueprint com rotas REST e streaming SSE
│   │   └── schemas.py    # Validação e higienização de contratos de entrada
│   │
│   ├── templates/        # Interface de Usuário (HTML SPA)
│   ├── static/           # Estilos (CSS), scripts (JS) e ícones
│   └── utils/            # Utilitários globais e gerenciador de logs rotativos
│
├── tests/                # Suíte de Testes Completa
│   ├── dominio/          # Testes unitários das entidades e regras de negócio
│   ├── aplicacao/        # Testes unitários dos casos de uso com mocks de portas
│   ├── infra/            # Testes unitários dos adaptadores de I/O
│   ├── adaptadores/      # Testes de integração das rotas HTTP Flask e validações
│   ├── e2e/              # Testes End-to-End via navegador com Playwright
│   └── conftest.py       # Fixtures compartilhadas e servidor de testes em background
│
├── pyproject.toml        # Configuração do pacote PEP 621, linters e pytest
└── main.py               # Entrypoint e Application Factory do Flask
```

---

## 🧪 Comandos de Desenvolvimento

Os comandos devem ser executados a partir da raiz do repositório via `Makefile`:

```bash
# Executar testes unitários e de integração
make test

# Executar testes End-to-End com Playwright
make e2e

# Executar linters e checagem de tipos estáticos
make quality

# Executar esteira completa de validação
make ci
```

---

## 📦 API Endpoints

| Método | Endpoint | Descrição | Resposta de Sucesso |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/sistema` | Coleta dados do SO, usuário e atalhos rápidos | `200 OK` (JSON com `InfoSistema`) |
| `GET` | `/api/escanear` | Varre pastas buscando arquivos de favoritos | `200 OK` (JSON com estatísticas e árvore) |
| `POST` | `/api/processar` | Processa lote de favoritos em tempo real | `200 OK` (`text/event-stream` SSE) |
