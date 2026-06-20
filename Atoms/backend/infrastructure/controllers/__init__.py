# Atoms/backend/infrastructure/controllers/__init__.py

"""Controladores de infraestrutura (scanners, parsers, identificadores)."""

import logging

from .file_scanners import VarredorSistemaArquivos
from .parser import AnalisadorTags
from .so_identifier import DetectarSistemaOperacional

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'controllers' carregado.")

__all__: list[str] = [
    "VarredorSistemaArquivos",
    "AnalisadorTags",
    "DetectarSistemaOperacional",
]
