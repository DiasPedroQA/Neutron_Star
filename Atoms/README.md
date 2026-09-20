# 🌌 Neutron Star Atoms

> Núcleo de processamento do ecossistema **Neutron Star**. Arquitetura Hexagonal, Flask, SSE.

O **Neutron Star Atoms** é o núcleo de processamento do ecossistema Neutron Star. Foi reestruturado sob os rígidos princípios da **Arquitetura Hexagonal (Portas e Adaptadores)**, utilizando:

- **Flask** para a camada de controle de rede;
- **validações robustas de payloads** sem dependências pesadas externas;
- **Server-Sent Events (SSE)** para transmissão reativa de progresso em tempo real.

A aplicação opera sobre caminhos disponíveis no mesmo sistema de arquivos do servidor, com barreiras de segurança física ativas.

---

## 🏗️ Arquitetura

### Fluxo entre camadas

```text
┌─────────────────────────────────────────────────────────┐
│  adaptadores/         (HTTP, Schemas)      ← ENTRADA    │
│  api.py  ──→  schemas.py                                │
└───────────────────────┬─────────────────────────────────┘
                        │ depende de
                        ▼
┌─────────────────────────────────────────────────────────┐
│  aplicacao/           (Casos de Uso + Portas)           │
│  casos_uso.py  ──→  portas.py (interfaces)              │
└───────────────────────┬─────────────────────────────────┘
                        │ depende de
                        ▼
┌─────────────────────────────────────────────────────────┐
│  dominio/             (Entidades + Exceções) ← NÚCLEO   │
│  entidades.py  ──→  excecoes.py                         │
└─────────────────────────────────────────────────────────┘
                        ▲
                        │ implementa portas
┌───────────────────────┴─────────────────────────────────┐
│  infra/               (Adaptadores de Saída) ← I/O      │
│  leitor.py, parser.py, escritores.py, ...               │
└─────────────────────────────────────────────────────────┘
```

**Regra de ouro:** `dominio/` não importa **nada** de fora (nem Flask, nem BS4). Se importa, é bug arquitetural.

### As quatro camadas

| # | Camada | Papel | Responsabilidade |
| --- | -------- | ------- | ------------------ |
| 1 | **`dominio`** | Núcleo Puro | Entidades imutáveis (`Favorito`) e exceções de negócio. 100% livre de frameworks. |
| 2 | **`aplicacao`** | Casos de Uso e Portas | Orquestra os fluxos (varredura, coleta ambiental, processador de lotes por streaming). Define as interfaces abstratas (Portas de Entrada/Saída). |
| 3 | **`infra`** | Adaptadores de Saída | Acesso físico ao SO: varredura de diretórios, abertura resiliente de HTML de bookmarks, escritores sob o padrão *Strategy* (CSV e JSON). |
| 4 | **`adaptadores`** | Adaptadores de Entrada | Expõe as portas da aplicação: validadores de contrato (`schemas.py`) e controladores HTTP do Flask (`api.py`). |

---

## ⚡ Recursos

- **Varredura inteligente e segura** — localiza e detalha metadados de arquivos HTML de favoritos no disco do servidor.
- **Parser BeautifulSoup altamente resiliente** — extrai recursivamente toda a estrutura de pastas do padrão Netscape Bookmarks, preservando hierarquias em múltiplos níveis, datas originais de adição e URLs válidas.
- **Mapeador de saídas customizáveis** — converte a árvore de favoritos para JSON estruturado ou CSV com codificação UTF-8 com BOM e separadores `;` (otimizado para Excel brasileiro).
- **Streaming de progresso real (SSE)** — comunicação unidirecional em tempo real, atualizando porcentagem e arquivo atual no milissegundo em que a conversão ocorre.
- **Proteção ativa contra invasão de caminhos** — filtro dinâmico contra *Path Traversal* (bloqueia caminhos fora do diretório HOME do usuário).

---

## 📡 Endpoints da API

Todas as comunicações usam o prefixo modular `/api`.

| Método |       Rota        |        Tipo         |                         Finalidade                          |
|--------|-------------------|---------------------|-------------------------------------------------------------|
| `GET`  | `/`               | `text/html`         |                SPA reativa, tema *Obsidian*.                |
| `GET`  | `/api/sistema`    | `application/json`  |        Metadados do SO hospedeiro + atalhos rápidos.        |
| `GET`  | `/api/escanear`   | `application/json`  |       Varre caminhos em busca de HTMLs de favoritos.        |
| `POST` | `/api/processar`  | `text/event-stream` | Converte o lote transmitindo progresso em tempo real (SSE). |

### Exemplo — conversão em lote via SSE

```bash
curl -X POST http://127.0.0.1:5000/api/processar \
  -H 'Content-Type: application/json' \
  -d '{
    "arquivos_selecionados": [
      "/home/diaspedro/Documentos/bookmarks_chrome.html",
      "/home/diaspedro/Downloads/favoritos_backup.html"
    ],
    "extensao_destino": "csv"
  }'
```

**Stream de eventos recebidos:**

```text
data: {"progresso": 50, "arquivo_atual": "bookmarks_chrome.html", "concluido": false}

data: {"progresso": 100, "arquivo_atual": "favoritos_backup.html", "concluido": true, "sucesso": true, "arquivos_convertidos": [...]}
```

---

## 🚀 Executar localmente

As dependências e o `.venv` ficam na raiz do repositório. Execute a partir de lá:

```bash
cd /home/diaspedro/Desktop/PyProject/Neutron_Star/

# Configura o .venv e instala tudo
make setup

# Levanta o Flask com debug ativo na porta 5000
make run
```

Manualmente, com o `.venv` já ativo:

```bash
source .venv/bin/activate
cd Atoms
export FLASK_DEBUG=1
python3 main.py
```

Painel e API disponíveis em: **`http://127.0.0.1:5000`**

---

## 🔒 Segurança

> ⚠️ **Nunca exponha esta aplicação diretamente na internet sem autenticação prévia.**

O backend possui validações profundas:

- **`PathInseguroError`** → `403 Forbidden`. Disparado em tentativas de `../../etc/passwd` ou caminhos fora do HOME.
- **`DiretorioInexistenteError`** → `404 Not Found`. Disparado quando o diretório não pode ser resolvido no filesystem.

---

## 🧪 Testes

O ecossistema é validado com **pytest** para garantir regressão zero. Os testes cobrem desde validações isoladas do extrator BeautifulSoup até simulações de fluxo HTTP completo no Flask.

Pelo Makefile, na raiz:

```bash
make test
```

Diretamente dentro de `Atoms/`:

```bash
cd Atoms/
pytest -v
```

Com cobertura:

```bash
pytest --cov=src --cov-report=term-missing
```

> ⚠️ Testes escritos com `unittest.TestCase` continuam funcionando — pytest coleta `unittest` nativamente.
