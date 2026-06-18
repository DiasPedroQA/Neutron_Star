# pylint: disable=import-outside-toplevel,too-many-locals

"""Exportador PDF de favoritos."""

import logging
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import StyleSheet1, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.interfaces.bookmark_exporter import BookmarkExporter

logger: logging.Logger = logging.getLogger(name=__name__)


class PDFExporter(BookmarkExporter):
    """Exporta favoritos para PDF."""

    def obter_formatos_suportados(self) -> str:
        """Retorna os formatos suportados por este exportador."""
        return "pdf"

    def exportar(self, lista_favoritos: list[Favorito], saida: Path) -> None:
        """Gera um PDF contendo os favoritos extraídos."""

        documento = SimpleDocTemplate(filename=str(saida), pagesize=letter)
        estilos: StyleSheet1 = getSampleStyleSheet()
        conteudo: list = []

        for favorito in lista_favoritos:
            data_formatada: str = favorito.data_adicao.strftime(
                format="%Y-%m-%d %H:%M:%S"
            )
            linha: str = f"<b>{favorito.titulo}</b><br/>- {favorito.url}<br/><i>{data_formatada}</i>"
            conteudo.extend(
                [
                    Paragraph(text=linha, style=estilos["Normal"]),
                    Spacer(width=1, height=12),
                ]
            )

        documento.build(flowables=conteudo)
        logger.info(
            msg=f"Exportados {len(lista_favoritos)} favoritos para PDF: {saida}"
        )
