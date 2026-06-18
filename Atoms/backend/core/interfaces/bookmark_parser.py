"""Interface para análise de arquivos de favoritos."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito


class BookmarkParser(ABC):
    """Define como extrair favoritos de um arquivo."""

    @abstractmethod
    def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Favorito]:
        """Extrai todos os favoritos de um arquivo HTML."""

    @abstractmethod
    def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
        """Verifica se o analisador é capaz de processar o arquivo informado."""

    def parse_file(self, arquivo: ModeloArquivo) -> list[Favorito]:
        """Alias de compatibilidade para `analisar_arquivo`."""
        return self.analisar_arquivo(arquivo=arquivo)

    def supports_file(self, arquivo: ModeloArquivo) -> bool:
        """Alias de compatibilidade para `suporta_arquivo`."""
        return self.suporta_arquivo(arquivo=arquivo)


FavoritoParser = BookmarkParser
