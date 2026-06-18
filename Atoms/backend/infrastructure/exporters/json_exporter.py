"""Exportador JSON de favoritos."""

import json
import logging
from pathlib import Path

from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.interfaces.bookmark_exporter import BookmarkExporter

logger: logging.Logger = logging.getLogger(name=__name__)


class JSONExporter(BookmarkExporter):
    """Exporta favoritos para JSON."""

    def obter_formatos_suportados(self) -> list[str]:
        """Retorna os formatos suportados por este exportador."""
        return ["json"]

    def exportar(self, favoritos: list[Favorito], saida: Path) -> None:
        """Grava favoritos em um arquivo JSON legível."""
        dados: list[dict[str, str]] = [
            {
                "titulo": favorito.titulo,
                "url": favorito.url,
                "data_adicao": favorito.data_adicao.isoformat(),
            }
            for favorito in favoritos
        ]
        with open(file=saida, mode="w", encoding="utf-8") as arquivo_saida:
            json.dump(obj=dados, fp=arquivo_saida, indent=4, ensure_ascii=False)
        logger.info("Exportados %d favoritos para JSON: %s", len(favoritos), saida)
