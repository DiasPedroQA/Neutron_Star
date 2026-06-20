# Atoms/backend/core/interfaces/bookmark_exporter.py

"""Interface para exportação de favoritos."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from backend.core.entidades.entidade_bookmark import Favorito

logger: logging.Logger = logging.getLogger(name=__name__)


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
            logger.error("Tentativa de exportar sem caminho de saída")
            raise ValueError("saida é obrigatória")

        # Log de uso de parâmetros legados
        if favoritos is None and bookmarks is not None:
            logger.info(
                "Usando parâmetro 'bookmarks' em vez de 'favoritos' (%d itens)",
                len(bookmarks),
            )
        elif favoritos is not None and bookmarks is not None:
            logger.warning(
                "Ambos 'favoritos' e 'bookmarks' fornecidos, usando 'favoritos' (%d itens)",
                len(favoritos),
            )

        favoritos_finais: list[Favorito] = (
            favoritos if favoritos is not None else (bookmarks or [])
        )

        logger.debug(
            "Exportando %d favoritos para %s",
            len(favoritos_finais),
            pasta_saida,
        )

        self.exportar(lista_favoritos=favoritos_finais, saida=pasta_saida)

    def get_supported_formats(self) -> str:
        """Alias de compatibilidade para `obter_formatos_suportados`."""
        logger.debug("Usando alias 'get_supported_formats'")
        return self.obter_formatos_suportados()
