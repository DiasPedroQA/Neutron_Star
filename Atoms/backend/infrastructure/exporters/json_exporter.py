# Atoms/backend/infrastructure/exporters/json_exporter.py

"""Exportador JSON de favoritos."""

import json
import logging
from pathlib import Path

from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.interfaces.bookmark_exporter import FavoritoExporter

logger: logging.Logger = logging.getLogger(name=__name__)


class JSONExporter(FavoritoExporter):
    """Exporta favoritos para JSON."""

    def obter_formatos_suportados(self) -> str:
        """Retorna os formatos suportados por este exportador."""
        return "json"

    def exportar(self, lista_favoritos: list[Favorito], saida: Path) -> None:
        """Grava favoritos em um arquivo JSON legível."""
        logger.debug(
            "Iniciando exportação JSON: %d favoritos para %s",
            len(lista_favoritos),
            saida,
        )

        if not lista_favoritos:
            logger.warning("Nenhum favorito para exportar em JSON.")
            return

        # Garante que o diretório pai exista
        diretorio_pai = saida.parent
        if not diretorio_pai.exists():
            logger.info("Criando diretório para exportação JSON: %s", diretorio_pai)
            diretorio_pai.mkdir(parents=True, exist_ok=True)
        elif not diretorio_pai.is_dir():
            logger.error(
                "Caminho do diretório pai não é um diretório: %s", diretorio_pai
            )
            raise NotADirectoryError(f"Não é um diretório: {diretorio_pai}")

        dados: list[dict[str, str]] = [
            {
                "titulo": favorito.titulo,
                "url": favorito.url,
                "data_adicao": favorito.data_adicao.isoformat(),
            }
            for favorito in lista_favoritos
        ]
        logger.debug("Dados serializados para JSON: %d registros", len(dados))

        try:
            with open(file=saida, mode="w", encoding="utf-8") as arquivo_saida:
                json.dump(obj=dados, fp=arquivo_saida, indent=4, ensure_ascii=False)
        except OSError:
            logger.exception("Erro de I/O ao exportar JSON para %s", saida)
            raise

        logger.info(
            "Exportados %d favoritos para JSON: %s",
            len(lista_favoritos),
            saida,
        )
