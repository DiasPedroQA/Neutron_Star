# Atoms/backend/infrastructure/exporters/pdf_exporter.py
# pylint: disable=import-outside-toplevel,too-many-locals

"""Exportador PDF de favoritos."""

import logging
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import StyleSheet1, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.interfaces.bookmark_exporter import FavoritoExporter

logger: logging.Logger = logging.getLogger(name=__name__)


class PDFExporter(FavoritoExporter):
    """Exporta favoritos para PDF."""

    def obter_formatos_suportados(self) -> str:
        """Retorna os formatos suportados por este exportador."""
        return "pdf"

    def exportar(self, lista_favoritos: list[Favorito], saida: Path) -> None:
        """Gera um PDF contendo os favoritos extraídos."""
        logger.debug(
            "Iniciando exportação PDF: %d favoritos para %s",
            len(lista_favoritos),
            saida,
        )

        if not lista_favoritos:
            logger.warning("Nenhum favorito para exportar em PDF.")
            return

        # Garante que o diretório pai exista
        diretorio_pai = saida.parent
        if not diretorio_pai.exists():
            logger.info("Criando diretório para exportação PDF: %s", diretorio_pai)
            diretorio_pai.mkdir(parents=True, exist_ok=True)
        elif not diretorio_pai.is_dir():
            logger.error(
                "Caminho do diretório pai não é um diretório: %s", diretorio_pai
            )
            raise NotADirectoryError(f"Não é um diretório: {diretorio_pai}")

        try:
            self._extrair_conteudo(saida, lista_favoritos)
        except Exception:
            logger.exception("Erro ao exportar PDF para %s", saida)
            raise

    def _extrair_conteudo(self, saida, lista_favoritos) -> None:
        documento = SimpleDocTemplate(filename=str(saida), pagesize=letter)
        estilos: StyleSheet1 = getSampleStyleSheet()
        conteudo: list = []

        for i, favorito in enumerate(lista_favoritos, start=1):
            data_formatada: str = favorito.data_adicao.strftime(
                format="%Y-%m-%d %H:%M:%S"
            )
            linha: str = (
                f"<b>{favorito.titulo}</b><br/>"
                f"- {favorito.url}<br/>"
                f"<i>{data_formatada}</i>"
            )
            conteudo.extend(
                [
                    Paragraph(text=linha, style=estilos["Normal"]),
                    Spacer(width=1, height=12),
                ]
            )
            logger.debug(
                "Favorito %d/%d adicionado ao PDF: %s",
                i,
                len(lista_favoritos),
                favorito.url,
            )

        logger.debug("Construindo documento PDF...")
        documento.build(flowables=conteudo)
        logger.info(
            "Exportados %d favoritos para PDF: %s",
            len(lista_favoritos),
            saida,
        )
