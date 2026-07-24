"""Testes do exportador de texto simples."""

from pathlib import Path

from adaptadores.exportadores.txt_exportador import ExportadorTXT
from dominio.entidades import TagA, VirtualFolder

_RAIZ = VirtualFolder(
    nome="Raiz",
    filhos_da_pasta=[
        TagA(url="https://a.com", titulo="A"),
        TagA(url="https://b.com", titulo="B"),
    ],
)


class TestExportadorTXT:
    """Geração de listagem em texto simples (título + URL por favorito)."""

    def test_cada_favorito_vira_titulo_e_url_em_linhas_separadas(self) -> None:
        """Cada bloco deve ter o título na primeira linha e a URL na segunda."""
        conteudo: str | None = ExportadorTXT().exportar(raiz=_RAIZ)

        assert "A\nhttps://a.com" in str(conteudo)
        assert "B\nhttps://b.com" in str(conteudo)

    def test_favoritos_separados_por_linha_em_branco(self) -> None:
        """Blocos de favoritos diferentes devem ficar separados por uma linha em branco."""
        conteudo: str | None = ExportadorTXT().exportar(raiz=_RAIZ)

        assert "\n\n" in str(conteudo)

    def test_pasta_vazia_gera_conteudo_vazio(self) -> None:
        """Sem favoritos, o exportador deve gerar uma string vazia."""
        conteudo: str | None = ExportadorTXT().exportar(raiz=VirtualFolder(nome="Vazia"))

        assert not str(conteudo)

    def test_grava_arquivo_quando_caminho_informado(self, tmp_path: Path) -> None:
        """Quando um caminho de saída é passado, o conteúdo deve ser gravado em disco."""
        destino: Path = tmp_path / "saida.txt"

        ExportadorTXT().exportar(raiz=_RAIZ, caminho_saida=destino)

        assert destino.exists()
        assert "A" in destino.read_text(encoding="utf-8")
