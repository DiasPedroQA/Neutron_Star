"""Exportador CSV de favoritos."""

import csv
import logging
from pathlib import Path

from Atoms.backend.core.entidades.entidade_bookmark import Favorito
from Atoms.backend.core.interfaces.bookmark_exporter import BookmarkExporter

logger: logging.Logger = logging.getLogger(name=__name__)


class CSVExporter(BookmarkExporter):
    """Exporta favoritos para CSV."""

    def obter_formatos_suportados(self) -> list[str]:
        """Retorna os formatos suportados por este exportador."""
        return ["csv"]

    def exportar(self, favoritos: list[Favorito], saida: Path) -> None:
        """Grava favoritos em um arquivo CSV com cabeçalho."""
        if not favoritos:
            logger.warning("Nenhum favorito para exportar em CSV.")
            return

        with open(file=saida, mode="w", newline="", encoding="utf-8") as arquivo_saida:
            escritor: csv.DictWriter[str] = csv.DictWriter(
                arquivo_saida, fieldnames=["titulo", "url", "data_adicao"]
            )
            escritor.writeheader()
            for favorito in favoritos:
                escritor.writerow(
                    rowdict={
                        "titulo": favorito.titulo,
                        "url": favorito.url,
                        "data_adicao": favorito.data_adicao.isoformat(),
                    }
                )
        logger.info("Exportados %d favoritos para CSV: %s", len(favoritos), saida)
