# core/interfaces/bookmark_repository.py

"""Interface para persistência de bookmarks."""

from __future__ import annotations

from abc import ABC, abstractmethod

from Atoms.backend.core.entidades.entidade_bookmark import Bookmark


class BookmarkRepository(ABC):
    """Define operações de salvamento e carregamento de bookmarks."""

    @abstractmethod
    def save(self, bookmarks: list[Bookmark], identifier: str) -> None:
        """Persiste uma lista de bookmarks associada a um identificador."""

    @abstractmethod
    def load(self, identifier: str) -> list[Bookmark]:
        """Recupera os bookmarks salvos para o identificador."""
