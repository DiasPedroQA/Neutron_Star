# Atoms/backend/core/interfaces/__init__.py

"""Interfaces (contratos) do domínio."""

import logging

from .bookmark_exporter import FavoritoExporter
from .bookmark_parser import FavoritoParser
from .bookmark_repository import FavoritoRepository
from .file_scanner import FileScanner

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'interfaces' carregado.")

__all__: list[str] = [
    "FavoritoExporter",
    "FavoritoParser",
    "FavoritoRepository",
    "FileScanner",
]
