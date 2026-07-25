"""Testes do exportador PDF.

Enquanto o import aponta para infraestrutura.pdf_stub (dependência
opcional fpdf2 não instalada), o comportamento esperado é falhar de
forma clara e explicativa, não com um ImportError genérico.
"""

import importlib.util

import adaptadores.exportadores.pdf_exportador as pdf_mod
import pytest
from dominio.entidades import TagA, VirtualFolder

_RAIZ = VirtualFolder(nome="Raiz", filhos_da_pasta=[TagA(url="https://a.com", titulo="A")])


class TestExportadorPDF:
    """Comportamento do exportador PDF com a dependência opcional ausente."""

    @pytest.mark.skipif(
        condition=importlib.util.find_spec(name="fpdf") is not None,
        reason="fpdf2 está instalado, este teste só faz sentido sem ele",
    )
    def test_sem_fpdf2_instalado_levanta_erro_claro(self, monkeypatch) -> None:
        """Se fpdf2 não estiver instalado, deve levantar ImportError ao tentar exportar."""
        # Simula ausência da biblioteca (já que o módulo pode ter sido importado,
        # precisamos forçar o estado; em testes reais, a flag _FPDF_AVAILABLE será False)
        # Para testar, podemos mockar a variável global ou usar um import fake.
        # Vamos usar pytest monkeypatch para definir _FPDF_AVAILABLE como False.
        monkeypatch.setattr(pdf_mod, "_FPDF_AVAILABLE", False)
        exportador = pdf_mod.ExportadorPDF()
        with pytest.raises(ImportError, match="fpdf2"):
            exportador.exportar(raiz=_RAIZ)
