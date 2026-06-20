# Atoms/backend/__init__.py

"""Camada de backend – domínio, serviços e infraestrutura."""

import logging

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'backend' carregado.")
