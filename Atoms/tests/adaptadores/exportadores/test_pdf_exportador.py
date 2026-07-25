"""Testes do exportador PDF.

Enquanto o import aponta para infraestrutura.pdf_stub (dependência
opcional fpdf2 não instalada), o comportamento esperado é falhar de
forma clara e explicativa, não com um ImportError genérico.
"""

import importlib.util
import sys

import pytest


class TestExportadorPDF:
    """Comportamento do exportador PDF com a dependência opcional ausente."""

    @pytest.mark.skipif(
        condition=importlib.util.find_spec(name="fpdf") is not None,
        reason="fpdf2 está instalado, este teste só faz sentido sem ele",
    )
    def test_sem_fpdf2_instalado_levanta_erro_claro(self) -> None:
        """Garante que, sem fpdf2 instalado, o import do exportador PDF falha com mensagem clara."""
        # O teste só roda se fpdf2 NÃO estiver instalado
        # Força recarga do módulo, caso já tenha sido importado
        modulo_nome = "src.adaptadores.exportadores.pdf_exportador"
        if modulo_nome in sys.modules:
            del sys.modules[modulo_nome]

        # Ao tentar importar o módulo, esperamos um ImportError que cite fpdf2
        with pytest.raises(expected_exception=ImportError, match="fpdf2"):
            __import__(name=modulo_nome, fromlist=["*"])
