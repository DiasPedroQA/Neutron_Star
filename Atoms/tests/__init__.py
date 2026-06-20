# Atoms/__init__.py

"""Pacote raiz do projeto Neutron Star."""

import logging

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'Atoms' carregado.")
