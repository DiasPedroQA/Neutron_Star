"""Interface para persistência de favoritos."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.entidades.entidade_bookmark import Favorito


class BookmarkRepository(ABC):
    """Define operações de salvamento e carregamento de favoritos."""

    @abstractmethod
    def salvar(self, favoritos: list[Favorito], identificador: str) -> None:
        """Persiste uma lista de favoritos associada a um identificador."""

    @abstractmethod
    def carregar(self, identificador: str) -> list[Favorito]:
        """Recupera os favoritos salvos para o identificador."""

    def save(self, bookmarks: list[Favorito], identifier: str) -> None:
        """Alias de compatibilidade para `salvar`."""
        self.salvar(favoritos=bookmarks, identificador=identifier)

    def load(self, identifier: str) -> list[Favorito]:
        """Alias de compatibilidade para `carregar`."""
        return self.carregar(identificador=identifier)


FavoritoRepository = BookmarkRepository
