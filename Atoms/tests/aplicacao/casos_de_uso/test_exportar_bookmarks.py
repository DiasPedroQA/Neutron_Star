"""Testes do caso de uso de exportação de bookmarks (exportar_bookmarks.py).

Cobre o roteamento para o exportador correto e o bug corrigido: o erro de
formato inválido é levantado sem contexto (por isso ErroBookmarks precisou
aceitar contexto opcional).
"""

from pathlib import Path

import pytest

from src.aplicacao.casos_de_uso.exportar_bookmarks import exportar_bookmarks
from src.dominio.entidades import TagA, VirtualFolder
from src.dominio.excecoes import ErroBookmarks

_RAIZ = VirtualFolder(nome="Raiz", filhos_da_pasta=[TagA(url="https://a.com", titulo="A")])


class TestExportarBookmarks:
    """Roteamento entre os exportadores registrados por formato."""

    @pytest.mark.parametrize(argnames="formato", argvalues=[".json", ".csv", ".txt", ".md"])
    def test_formatos_texto_retornam_conteudo_em_string(self, formato: str) -> None:
        """Formatos textuais devem devolver uma string não vazia com o favorito exportado."""
        resultado: str | None = exportar_bookmarks(raiz=_RAIZ, formato=formato)

        assert isinstance(resultado, str)
        assert "A" in resultado

    def test_formato_nao_suportado_levanta_erro_com_lista_de_validos(self) -> None:
        """Formato desconhecido deve levantar ErroBookmarks listando os formatos aceitos."""
        with pytest.raises(expected_exception=ErroBookmarks, match=r"\.docx.*não suportado"):
            exportar_bookmarks(raiz=_RAIZ, formato=".docx")

    def test_grava_arquivo_quando_caminho_saida_informado(self, tmp_path: Path) -> None:
        """Quando um caminho de saída é informado, o conteúdo deve ser gravado em disco."""
        destino: Path = tmp_path / "bookmarks.json"

        exportar_bookmarks(raiz=_RAIZ, formato=".json", caminho_saida=destino)

        assert destino.exists()
        assert "A" in destino.read_text(encoding="utf-8")
