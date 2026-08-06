Uso
===

Esta página descreve como preparar o ambiente e executar o Neutron Star localmente.

Instalação
----------

1. Crie e ative um ambiente virtual:

   .. code-block:: bash

      python -m venv Atoms/.venv
      source Atoms/.venv/bin/activate

2. Instale o pacote em modo desenvolvimento (dependências de runtime + dev vêm
   todas de ``Atoms/pyproject.toml``, fonte única de verdade):

   .. code-block:: bash

      pip install -e "Atoms[dev]"

Execução
--------

Use o entry point instalado pelo pacote:

.. code-block:: bash

   neutron

Ou execute o módulo diretamente:

.. code-block:: bash

   python -m Atoms.src.main

Validação
---------

Comandos usados no fluxo de shift-left do projeto (também rodam na CI):

* ``python -m pytest`` — testes com cobertura (``fail_under = 85`` em ``pyproject.toml``)
* ``python -m ruff check Atoms/src Atoms/tests`` — lint
* ``python -m ruff format --check Atoms/src Atoms/tests`` — formatação
* ``python -m mypy Atoms/src`` — tipagem estática
* ``python -m bandit -c Atoms/pyproject.toml -r Atoms/src`` — segurança
