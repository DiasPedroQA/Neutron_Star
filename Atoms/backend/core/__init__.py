# Atoms/backend/core/__init__.py

"""Núcleo do domínio: entidades, interfaces e serviços."""

import logging

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'core' carregado.")
