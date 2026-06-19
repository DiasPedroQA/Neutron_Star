"""Exportador CSV de favoritos."""

import csv
import logging
from pathlib import Path

from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.interfaces.bookmark_exporter import FavoritoExporter

logger: logging.Logger = logging.getLogger(name=__name__)


class CSVExporter(FavoritoExporter):
    """Exporta favoritos para CSV."""

    def obter_formatos_suportados(self) -> str:
        """Retorna os formatos suportados por este exportador."""
        return "csv"

    def exportar(self, lista_favoritos: list[Favorito], saida: Path) -> None:
        """Grava favoritos em um arquivo CSV com cabeçalho."""
        if not lista_favoritos:
            logger.warning(msg="Nenhum favorito para exportar em CSV.")
            return

        if not saida.exists():
            print("Não encontrei a pasta de saída")

        with open(file=saida, mode="w", newline="", encoding="utf-8") as arquivo_saida:
            escritor: csv.DictWriter[str] = csv.DictWriter(
                f=arquivo_saida, fieldnames=["titulo", "url", "data_adicao"]
            )
            escritor.writeheader()
            for favorito in lista_favoritos:
                escritor.writerow(
                    rowdict={
                        "titulo": favorito.titulo,
                        "url": favorito.url,
                        "data_adicao": favorito.data_adicao.isoformat(),
                    }
                )
        logger.info(
            msg=f"Exportados {len(lista_favoritos)} favoritos para CSV: {saida}"
        )
