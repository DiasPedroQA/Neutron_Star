# Guia de uso do projeto Neutron Star

Este documento reúne os passos essenciais para executar, testar e validar a aplicação localmente.

## Requisitos

- Python 3.12 ou superior
- Ambiente virtual configurado no diretório `.venv/`
- Dependências do projeto instaladas via `make env` ou `pip install -e .[dev]`

## Preparação do ambiente

A partir da raiz do repositório, execute:

```bash
make env
```

Esse comando cria o ambiente virtual, instala as dependências de desenvolvimento e prepara o projeto para testes e validação.

## Execução da aplicação

Para iniciar a interface web e o backend Flask:

```bash
make app-web
```

Em seguida, acesse:

```text
http://127.0.0.1:5000
```

Também é possível iniciar o servidor diretamente a partir da pasta `Atoms/`:

```bash
cd Atoms
python main.py
```

## Execução via CLI

O projeto também expõe um comando para uso em terminal:

```bash
make app-cli ARGS="--help"
```

ou:

```bash
cd Atoms
python cli.py --help
```

## Testes

### Testes unitários e de integração

```bash
make test
```

### Testes de ponta a ponta (E2E)

```bash
make test-e2e
```

### Validação completa (qualidade + testes)

```bash
make ci
```

## Boas práticas

- Sempre execute os comandos a partir da raiz do repositório.
- Mantenha o padrão de imports `src.*` em todo o código Python.
- Não escreva testes na pasta de logs do projeto; use `tmp_path` quando necessário.
- Para mudanças de comportamento, priorize testes focados antes de refatorações.

## Estrutura relevante

- `Atoms/src/` — domínio, controladores e adaptadores
- `Atoms/tests/` — testes automáticos e regressões
- `Atoms/logs/` — arquivos gerados em execução local
- `Atoms/src/views/static/openapi.yaml` — contrato da API
