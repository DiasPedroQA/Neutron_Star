"""Interface para exportação de favoritos."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from backend.core.entidades.entidade_bookmark import Favorito


class FavoritoExporter(ABC):
    """Define como exportar uma lista de favoritos para um formato específico."""

    @abstractmethod
    def exportar(self, lista_favoritos: list[Favorito], saida: Path) -> None:
        """Exporta os favoritos para o caminho de saída."""

    @abstractmethod
    def obter_formatos_suportados(self) -> str:
        """Retorna as extensões suportadas (ex: ['json', 'csv'])."""

    def export(
        self,
        bookmarks: list[Favorito] | None = None,
        pasta_saida: Path | None = None,
        *,
        favoritos: list[Favorito] | None = None,
    ) -> None:
        """Alias de compatibilidade para `exportar`."""
        if pasta_saida is None:
            raise ValueError("saida é obrigatória")
        favoritos_finais: list[Favorito] = (
            favoritos if favoritos is not None else (bookmarks or [])
        )
        self.exportar(lista_favoritos=favoritos_finais, saida=pasta_saida)

    def get_supported_formats(self) -> str:
        """Alias de compatibilidade para `obter_formatos_suportados`."""
        return self.obter_formatos_suportados()
