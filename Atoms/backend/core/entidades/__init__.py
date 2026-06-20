# Atoms/backend/core/entidades/__init__.py

"""Entidades de domínio do projeto."""

import logging

from .entidade_arquivo import ModeloArquivo
from .entidade_bookmark import Favorito
from .entidade_diretorio import ModeloPasta
from .entidade_processamento import (
    EstatisticasProcessamento,
    ResultadoProcessamento,
)
from .entidade_sistema_operacional import ModeloSistemaOperacional

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'entidades' carregado.")

__all__: list[str] = [
    "Favorito",
    "ModeloArquivo",
    "ModeloPasta",
    "ModeloSistemaOperacional",
    "EstatisticasProcessamento",
    "ResultadoProcessamento",
]
