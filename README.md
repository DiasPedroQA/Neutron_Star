# src

Descobre, lê e converte arquivos de bookmarks no formato Netscape (o
`.html` exportado por Chrome, Firefox etc.), via **linha de comando**
ou **API HTTP** — usando o mesmo núcleo de regras para as duas.

## Por que esse projeto existe

Este pacote nasceu de um conjunto de 3 módulos soltos (`bookmarks_core`,
`buscador_de_arquivos`, `conversor_bookmarks`) que já tinha uma boa
suíte de testes, mas escondia um bug real: o parser usado
(`html.parser`) não fecha automaticamente as tags `<p>`/`<DT>` como o
HTML5 exige — e todo export real de bookmarks vem justamente com essas
tags não fechadas. Isso fazia a árvore de pastas aninhadas sair errada
ou vazia em arquivos reais, mesmo com os testes "passando" (os testes
tinham o mesmo bug embutido nas fixtures).

A correção trocou o parser para `html5lib` e ajustou a busca pela
subpasta (`<DL>` é filho de `<DT>`, não irmão — ver
`src/dominio/arvore.py`).

## Arquitetura (leve)

```
src/
  dominio/          # entidades e regras puras — sem I/O, sem bs4/pandas na API pública
    entidades.py    # BookmarkNode
    tipos.py        # to_int, to_str
    arvore.py       # extrair_arvore, flatten_tree, contar_links
    filtros.py       # filtrar_por_caminhos_ocultos, filtrar_pelo_nome
  aplicacao/        # casos de uso + I/O (leitura de arquivo, escrita de formatos)
    leitura.py
    exportadores.py
    casos_de_uso/
      buscar_bookmarks.py
      converter_bookmarks.py
  adaptadores/      # pontos de entrada — sem regra de negócio
    cli.py
    api.py
```

Só três camadas, sem interfaces abstratas (portas) nem orquestração
genérica — CLI e API chamam os mesmos casos de uso diretamente. Se o
projeto crescer (novos formatos de entrada, filas, etc.), esse é o
lugar mais natural para introduzir uma camada de portas.

## Instalação

```bash
pip install -e ".[api,dev]"
```

## Uso — CLI

```bash
bookmarks-cli buscar ~/Downloads          # relatório de arquivos encontrados
bookmarks-cli converter bookmarks.html --formatos .csv .json --favicon
```

## Uso — API

```bash
bookmarks-api   # sobe em http://127.0.0.1:8000
```

- `GET /saude` — verificação simples
- `GET /buscar?origem=/caminho` — mesmo relatório da CLI
- `POST /converter` — corpo JSON: `{"caminhos": [...], "formatos": [...], "sufixo": "...", "favicon": bool}`

Documentação interativa automática em `/docs` (Swagger) quando a API
está rodando.

## Testes e cobertura

```bash
pytest
```

Estrutura de testes espelha a de produção (`tests/dominio/`,
`tests/aplicacao/`, `tests/adaptadores/`). Estado atual: 63 testes,
93% de cobertura, `ruff check .` limpo.

## Fora do escopo desta primeira versão (de propósito)

- Upload de arquivo pela API (hoje ela opera sobre caminhos já
  presentes no disco onde roda).
- CI/CD, Docker, autenticação na API.
- Camada de portas/interfaces abstratas.

Nenhum desses é difícil de adicionar depois — foram deixados de fora
para não antecipar complexidade que o projeto ainda não pediu.
