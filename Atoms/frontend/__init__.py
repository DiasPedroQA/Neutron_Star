# Atoms/frontend/__init__.py

"""Camada de apresentação (frontend)."""

import logging

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(hdlr=logging.NullHandler())
logger.debug(msg="Pacote 'frontend' carregado.")
