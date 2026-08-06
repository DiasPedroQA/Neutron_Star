# Neutron Star

Ferramenta Python para localizar, ler e converter arquivos de favoritos no
formato Netscape Bookmark (`.html`), exportados por navegadores como Chrome e
Firefox. Ela disponibiliza a mesma funcionalidade por linha de comando e por
uma API HTTP opcional.

> Os arquivos de favoritos do Netscape costumam conter HTML não estritamente
> válido. O projeto usa `html5lib` para interpretar corretamente estruturas
> comuns, incluindo pastas aninhadas com tags não fechadas.

## Recursos

- Busca recursiva por arquivos HTML de favoritos, ignorando diretórios ocultos.
- Extração de título, URL, data de adição, pasta e, opcionalmente, ícone.
- Conversão para CSV, JSON, Parquet, XML e Markdown.
- Inclusão opcional de uma URL de favicon para cada bookmark.
- CLI e API FastAPI usando os mesmos casos de uso.

## Requisitos

- Python 3.10 ou superior.
- `make` (opcional, para os atalhos do projeto).

## Instalação

A forma mais completa de preparar o ambiente de desenvolvimento é:

```bash
make install
source .venv/bin/activate
```

Para uma instalação manual apenas com a CLI e a API:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e "Atoms[api]"
```

Para incluir dependências de desenvolvimento, use `"Atoms[api,dev]"`. Os
formatos Parquet e Markdown exigem, respectivamente, os extras `parquet` e
`table`:

```bash
pip install -e "Atoms[api,parquet,table]"
```

## Uso pela linha de comando

Após a instalação, os comandos disponíveis são `bookmarks-cli` e
`bookmarks-api`.

### Localizar arquivos de favoritos

```bash
bookmarks-cli buscar ~/Downloads
```

Sem informar a pasta, a busca é feita no diretório inicial do usuário. O
comando procura arquivos `.html` cujo nome corresponda a favoritos/bookmarks e
exibe um relatório com o status e a quantidade de links de cada arquivo.

### Converter favoritos

```bash
bookmarks-cli converter ~/Downloads/bookmarks.html --formatos .csv .json
```

Os arquivos de saída são criados no mesmo diretório do arquivo de entrada. Por
padrão, são gerados CSV e JSON. É possível converter mais de um arquivo e
incluir dados adicionais:

```bash
bookmarks-cli converter bookmarks.html outro-bookmarks.html \
  --formatos .csv .json \
  --sufixo _convertido \
  --favicon \
  --icone
```

Opções principais:

- `--formatos`: extensões de saída entre `.csv`, `.json`, `.parquet`,
  `.xml` e `.md`.
- `--sufixo`: texto acrescentado ao nome de cada arquivo gerado.
- `--favicon`: acrescenta a coluna `favicon_url`, apontando para o serviço de
  favicons do Google.
- `--icone`: preserva a coluna `icon` com o conteúdo original em base64, quando
  disponível no arquivo de origem.

## Uso pela API

Instale o extra `api` e inicie o servidor:

```bash
bookmarks-api
```

O serviço fica disponível em `http://127.0.0.1:8000`; a documentação interativa
do FastAPI está em `http://127.0.0.1:8000/docs`.

| Rota | Descrição |
| --- | --- |
| `GET /saude` | Verifica se a API está disponível. |
| `GET /buscar?origem=/caminho` | Localiza e analisa arquivos de favoritos. |
| `POST /converter` | Converte os arquivos indicados no corpo JSON. |

Exemplo de conversão:

```bash
curl -X POST http://127.0.0.1:8000/converter \
  -H 'Content-Type: application/json' \
  -d '{"caminhos": ["/caminho/bookmarks.html"], "formatos": [".csv", ".json"], "favicon": true}'
```

Por segurança, exponha a API somente em ambientes confiáveis: ela recebe
caminhos do sistema de arquivos onde está sendo executada e não possui
autenticação nem upload de arquivos.

## Desenvolvimento e qualidade

Os alvos abaixo criam ou utilizam o ambiente virtual `.venv` na raiz do
repositório:

```bash
make test    # testes com cobertura
make lint    # Ruff: lint e verificação de formatação
make check   # lint e testes
make ci      # verificações locais equivalentes à pipeline
make docs    # gera a documentação Sphinx em Atoms/docs/_build/html/
```

Os testes estão organizados nas mesmas camadas do código de produção:

```text
Atoms/
├── src/
│   ├── dominio/       # entidades, árvore e filtros puros
│   ├── aplicacao/     # leitura, exportação e casos de uso
│   └── adaptadores/   # interfaces CLI e HTTP
├── tests/
└── docs/
```

## Limitações atuais

- A API opera apenas sobre arquivos já disponíveis no disco do servidor.
- Não há autenticação, conteinerização ou pipeline de entrega configuradas.
- A URL de favicon depende de um serviço externo; o ícone não é baixado pela
  ferramenta.

## Licença

Distribuído sob a [GNU GPLv3](LICENSE).
