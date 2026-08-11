# Neutron Star Atoms

API FastAPI para localizar arquivos HTML de bookmarks e extrair seus links. Ela
opera sobre caminhos disponíveis no mesmo sistema de arquivos do servidor.

## Recursos

- Localização de arquivos HTML de bookmarks.
- Extração de título, URL, datas, pasta e atributo `TAGS` dos links encontrados.
- Fluxo combinado de busca e extração.
- Documentação interativa OpenAPI em `/docs`.

## Executar localmente

```bash
python -m pip install -e ".[dev]"
python main.py
```

A API será servida em `http://127.0.0.1:8000`. Consulte a documentação
interativa em `http://127.0.0.1:8000/docs` e o contrato OpenAPI em
`http://127.0.0.1:8000/openapi.json`.

## Rotas

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/health` | Verifica se a API está disponível. |
| `GET` | `/listar_arquivos` | Localiza arquivos HTML e retorna seus metadados. |
| `POST` | `/extrair_tags_do_arquivo` | Extrai bookmarks de um arquivo específico. |
| `GET` | `/buscar_e_extrair_tags` | Localiza arquivos e extrai bookmarks de todos eles. |

Exemplo de extração:

```bash
curl -X POST http://127.0.0.1:8000/extrair_tags_do_arquivo \
  -H 'Content-Type: application/json' \
  -d '{"caminho":"/caminho/para/bookmarks.html"}'
```

Uma resposta com `tags: []` é válida: ela indica que o arquivo foi lido, mas
nenhum link de bookmark reconhecível foi extraído. Um caminho inexistente retorna
`404`.

## Segurança

Não exponha esta API diretamente na internet. Ela recebe caminhos de arquivo e
não possui autenticação nem upload; execute-a somente em ambiente confiável.

## Testes

```bash
PYTHONPATH=src python -m pytest tests
```

A aplicação organiza as regras em quatro camadas: `dominio`, `aplicacao`,
`infra` e `adaptadores`.
