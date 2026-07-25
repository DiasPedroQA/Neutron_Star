"""Adaptador de exportação de bookmarks para documentos PDF.

Implementa um exportador concreto que gera um arquivo PDF simples a
partir de uma hierarquia de favoritos, formatando títulos e URLs em blocos legíveis.
"""

from pathlib import Path

from aplicacao.portas.exportador import Exportador
from dominio.entidades import TagA, VirtualFolder
from dominio.travessia import iterar_bookmarks

try:
    from fpdf import FPDF
except Exception as erro_pdf:  # pylint: disable=W0718
    print(f"Erro de importação {erro_pdf}")
    from infraestrutura.pdf_stub import FPDF


class ExportadorPDF(Exportador):
    """Exportador de bookmarks para arquivo PDF."""

    def exportar(self, raiz: VirtualFolder, caminho_saida: Path | None = None) -> None:
        """Exporta bookmarks como PDF simples (ver Exportador.exportar).

        Sempre retorna None: o conteúdo binário é gravado direto em arquivo.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(family="Helvetica", size=12)
        pdf.cell(0, 10, "Bookmarks exportados", "C")
        pdf.ln(10)
        pdf.set_font(family="Helvetica", size=10)
        for bm in iterar_bookmarks(pasta=raiz):
            self._montar_celula_pdf(pdf=pdf, bm=bm)
        if caminho_saida:
            pdf.output(str(caminho_saida))

    @staticmethod
    def _montar_celula_pdf(pdf: FPDF, bm: TagA) -> None:
        """Adiciona um favorito (título + URL) como bloco formatado no PDF."""
        pdf.set_font(style="B")
        pdf.multi_cell(0, 6, bm.titulo)
        pdf.set_font(style="")
        pdf.set_text_color(r=0, g=0, b=255)
        pdf.multi_cell(0, 5, bm.url)
        pdf.set_text_color(r=0)
        pdf.ln(h=2)
