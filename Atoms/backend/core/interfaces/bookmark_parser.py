# core/interfaces/bookmark_parser.py

"""Interface para parsing de arquivos de bookmarks."""

from __future__ import annotations

from abc import ABC, abstractmethod

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Bookmark


class BookmarkParser(ABC):
    """Define como extrair bookmarks de um arquivo."""

    @abstractmethod
    def parse_file(self, arquivo: ModeloArquivo) -> list[Bookmark]:
        """Extrai todos os bookmarks de um arquivo HTML."""

    @abstractmethod
    def supports_file(self, arquivo: ModeloArquivo) -> bool:
        """Verifica se o parser é capaz de processar o arquivo informado."""
