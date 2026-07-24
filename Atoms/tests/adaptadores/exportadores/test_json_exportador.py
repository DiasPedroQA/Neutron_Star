"""Testes do exportador JSON."""

import json
from pathlib import Path

from adaptadores.exportadores.json_exportador import ExportadorJSON
from dominio.entidades import TagA, VirtualFolder

_RAIZ = VirtualFolder(
    nome="Raiz",
    filhos_da_pasta=[TagA(url="https://a.com", titulo="A")],
)


class TestExportadorJSON:
    """Geração de saída JSON estruturada a partir da hierarquia de bookmarks."""

    def test_gera_json_valido_espelhando_to_dict(self) -> None:
        """O JSON gerado deve ser exatamente o to_dict() da raiz, sem perdas."""
        conteudo: str | None = ExportadorJSON().exportar(raiz=_RAIZ)

        assert json.loads(str(conteudo)) == _RAIZ.to_dict()

    def test_json_usa_indentacao_legivel(self) -> None:
        """A saída deve ser formatada (indent=2), não uma linha única compacta."""
        conteudo: str | None = ExportadorJSON().exportar(raiz=_RAIZ)

        assert "\n" in str(conteudo)

    def test_grava_arquivo_quando_caminho_informado(self, tmp_path: Path) -> None:
        """Quando um caminho de saída é passado, o conteúdo deve ser gravado em disco."""
        destino: Path = tmp_path / "saida.json"

        ExportadorJSON().exportar(raiz=_RAIZ, caminho_saida=destino)

        assert json.loads(destino.read_text(encoding="utf-8")) == _RAIZ.to_dict()
