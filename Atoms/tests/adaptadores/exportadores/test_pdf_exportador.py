"""Testes do exportador PDF.

Enquanto o import aponta para infraestrutura.pdf_stub (dependência
opcional fpdf2 não instalada), o comportamento esperado é falhar de
forma clara e explicativa, não com um ImportError genérico.
"""

import pytest
from adaptadores.exportadores.pdf_exportador import ExportadorPDF
from dominio.entidades import TagA, VirtualFolder

_RAIZ = VirtualFolder(nome="Raiz", filhos_da_pasta=[TagA(url="https://a.com", titulo="A")])


class TestExportadorPDF:
    """Comportamento do exportador PDF com a dependência opcional ausente."""

    def test_sem_fpdf2_instalado_levanta_erro_claro(self) -> None:
        """Deve informar claramente que fpdf2 é necessário, em vez de estourar erro genérico."""
        exportador = ExportadorPDF()
        with pytest.raises(expected_exception=RuntimeError, match="fpdf2"):
            exportador.exportar(raiz=_RAIZ)
