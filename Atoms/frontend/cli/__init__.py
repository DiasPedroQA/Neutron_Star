# Atoms/frontend/cli/__init__.py

"""Interface de linha de comando (CLI)."""

import logging

from .cli_display import (
    cli_exibir_estatisticas,
    cli_exibir_favoritos,
    cli_exibir_sistema_operacional,
    menu_exportar,
)

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'cli' carregado.")

__all__: list[str] = [
    "cli_exibir_estatisticas",
    "cli_exibir_favoritos",
    "cli_exibir_sistema_operacional",
    "menu_exportar",
]
