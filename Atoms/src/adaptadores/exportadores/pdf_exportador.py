"""Adaptador de exportação de bookmarks para documentos PDF.

Implementa um exportador concreto que gera um arquivo PDF simples a
partir de uma hierarquia de favoritos, formatando títulos e URLs em blocos legíveis.
"""

from pathlib import Path

from aplicacao.portas.exportador import Exportador
from dominio.entidades import Bookmark, BookmarkFolder
from infraestrutura.pdf_stub import FPDF

# from fpdf import FPDF
from adaptadores.exportadores.iterador import _iterar_bookmarks


class ExportadorPDF(Exportador):  # pylint: disable=too-few-public-methods
    """Exportador de bookmarks para arquivo PDF."""

    def exportar(self, raiz: BookmarkFolder, caminho_saida: Path | None = None) -> str | None:
        """Exporta bookmarks como PDF simples (ver Exportador.exportar).

        Sempre retorna None: o conteúdo binário é gravado direto em arquivo.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(family="Helvetica", size=12)
        pdf.cell(w=0, h=10, txt="Bookmarks exportados", align="C")
        pdf.ln(10)
        pdf.set_font(family="Helvetica", size=10)
        for bm in _iterar_bookmarks(pasta=raiz):
            self._montar_celula_pdf(pdf=pdf, bm=bm)
        if caminho_saida:
            pdf.output(str(caminho_saida))
        return None

    @staticmethod
    def _montar_celula_pdf(pdf: FPDF, bm: Bookmark) -> None:
        """Adiciona um favorito (título + URL) como bloco formatado no PDF."""
        pdf.set_font(style="B")
        pdf.multi_cell(0, 6, bm.titulo)
        pdf.set_font(style="")
        pdf.set_text_color(0, 0, 255)
        pdf.multi_cell(0, 5, bm.url)
        pdf.set_text_color(0)
        pdf.ln(2)
