# core/interfaces/bookmark_exporter.py

"""Interface para exportação de bookmarks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from Atoms.backend.core.entidades.entidade_bookmark import Bookmark


class BookmarkExporter(ABC):
    """Define como exportar uma lista de bookmarks para um formato específico."""

    @abstractmethod
    def export(self, bookmarks: list[Bookmark], saida: Path) -> None:
        """Exporta os bookmarks para o caminho de saída."""

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Retorna a lista de extensões suportadas (ex: ['json', 'csv'])."""
