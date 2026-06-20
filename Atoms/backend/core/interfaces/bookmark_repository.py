# Atoms/backend/core/interfaces/bookmark_repository.py

"""Interface para persistência de favoritos."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from backend.core.entidades.entidade_bookmark import Favorito

logger: logging.Logger = logging.getLogger(name=__name__)


class FavoritoRepository(ABC):
    """Define operações de salvamento e carregamento de favoritos."""

    @abstractmethod
    def salvar(self, favoritos: list[Favorito], identificador: str) -> None:
        """Persiste uma lista de favoritos associada a um identificador."""

    @abstractmethod
    def carregar(self, identificador: str) -> list[Favorito]:
        """Recupera os favoritos salvos para o identificador."""

    def save(self, bookmarks: list[Favorito], identifier: str) -> None:
        """Alias de compatibilidade para `salvar`."""
        logger.debug(
            "Usando alias 'save' para salvar %d favoritos com id=%r",
            len(bookmarks),
            identifier,
        )
        if not bookmarks:
            logger.info(
                "Tentativa de salvar lista vazia de favoritos (id=%r).", identifier
            )
        self.salvar(favoritos=bookmarks, identificador=identifier)

    def load(self, identifier: str) -> list[Favorito]:
        """Alias de compatibilidade para `carregar`."""
        logger.debug(
            "Usando alias 'load' para carregar favoritos com id=%r", identifier
        )
        return self.carregar(identificador=identifier)
