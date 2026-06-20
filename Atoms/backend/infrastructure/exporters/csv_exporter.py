# Atoms/backend/infrastructure/exporters/csv_exporter.py

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
        logger.debug(
            "Iniciando exportação CSV: %d favoritos para %s",
            len(lista_favoritos),
            saida,
        )

        if not lista_favoritos:
            logger.warning("Nenhum favorito para exportar em CSV.")
            return

        # Garante que o diretório pai exista
        diretorio_pai = saida.parent
        if not diretorio_pai.exists():
            logger.info("Criando diretório para exportação CSV: %s", diretorio_pai)
            diretorio_pai.mkdir(parents=True, exist_ok=True)
        elif not diretorio_pai.is_dir():
            logger.error(
                "Caminho do diretório pai não é um diretório: %s", diretorio_pai
            )
            raise NotADirectoryError(f"Não é um diretório: {diretorio_pai}")

        try:
            with open(
                file=saida, mode="w", newline="", encoding="utf-8"
            ) as arquivo_saida:
                escritor: csv.DictWriter[str] = csv.DictWriter(
                    f=arquivo_saida, fieldnames=["titulo", "url", "data_adicao"]
                )
                escritor.writeheader()
                logger.debug("Cabeçalho CSV escrito")

                for i, favorito in enumerate(lista_favoritos, start=1):
                    escritor.writerow(
                        rowdict={
                            "titulo": favorito.titulo,
                            "url": favorito.url,
                            "data_adicao": favorito.data_adicao.isoformat(),
                        }
                    )
                    logger.debug(
                        "Favorito %d/%d exportado: %s",
                        i,
                        len(lista_favoritos),
                        favorito.url,
                    )

        except OSError:
            logger.exception("Erro de I/O ao exportar CSV para %s", saida)
            raise

        logger.info(
            "Exportados %d favoritos para CSV: %s",
            len(lista_favoritos),
            saida,
        )
