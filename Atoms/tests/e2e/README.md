# Testes E2E do Neutron Star

A pasta `tests/e2e/` reúne cenários de ponta a ponta que validam a experiência real do usuário na aplicação web.

## Objetivo

Garantir que o fluxo principal da aplicação continue funcionando conforme o contrato esperado:

1. localizar arquivos HTML válidos;
2. revisar resultados e metadados;
3. converter favoritos em JSON, CSV ou Markdown;
4. verificar a renderização e a resposta final para o usuário.

## Execução

A partir da raiz do repositório:

```bash
make test-e2e
```

Se preferir rodar apenas o diretório E2E:

```bash
cd Atoms
./.venv/bin/pytest tests/e2e -q
```

## Observações

- Os testes E2E devem garantir isolamento de arquivos e logs usando `tmp_path` ou fixtures locais.
- As verificações visuais devem preferir asserts em conteúdo renderizado em vez de dependências frágeis de CSS.
- Caso um comportamento seja conhecido e temporariamente quebrado, utilize a convenção de regressão com `xfail(strict=True)` no arquivo de testes apropriado.

## Estrutura esperada

```text
Atoms/tests/e2e/
├── conftest.py
├── test_fluxo_web.py
└── README.md
```
