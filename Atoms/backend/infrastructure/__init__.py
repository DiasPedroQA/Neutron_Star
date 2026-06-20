# Atoms/backend/infrastructure/__init__.py

"""Implementações de infraestrutura (exporters, scanners, etc.)."""

import logging

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'infrastructure' carregado.")
