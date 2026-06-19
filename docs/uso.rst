Uso
===

Esta página descreve como preparar o ambiente e executar o Neutron Star localmente.

Instalação
----------

1. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Instale as dependências de desenvolvimento e o pacote local:

   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

Execução
--------

Use o comando de módulo para rodar a CLI principal:

```bash
python -m Atoms.frontend.cli.main
```

Validação
----------

Recomenda-se usar estes comandos para verificar o código:

* `python -m pytest`
* `python -m ruff check Atoms Atoms/tests`

Notas de desenvolvimento
=============================

Para ambientes de CI seguros, o projeto mantém um lockfile hash-locked em
`requirements-dev.lock`. Use:

```bash
python -m pip install --no-deps --require-hashes -r requirements-dev.lock
```
