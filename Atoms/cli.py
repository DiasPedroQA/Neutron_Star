#!/usr/bin/env python3
# Atoms/cli.py

"""Ponto de entrada executável para a CLI do Neutron Star.

Execução: ``python cli.py <comando>`` a partir da pasta ``Atoms/`` (o Python
já inclui o diretório do script no ``sys.path``, então ``src`` é importável).
"""

import sys

from src.controllers.cli_controller import CLIController

if __name__ == "__main__":
    sys.exit(CLIController.main())
