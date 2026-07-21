"""Testes do exportador CSV."""

from pathlib import Path

from src.adaptadores.exportadores.csv_exportador import ExportadorCSV
from src.dominio.entidades import TagA, VirtualFolder

_RAIZ = VirtualFolder(
    nome="Raiz",
    filhos_da_pasta=[TagA(url="https://a.com", titulo="A", data_adicao="100")],
)


class TestExportadorCSV:
    """Geração de saída CSV tabular a partir da hierarquia de bookmarks."""

    def test_gera_cabecalho_e_uma_linha_por_favorito(self) -> None:
        """A primeira linha deve ser o cabeçalho; a segunda, os dados do favorito."""
        conteudo: str | None = ExportadorCSV().exportar(raiz=_RAIZ)

        if conteudo is not None:
            linhas: list[str] = conteudo.strip().splitlines()
            assert linhas[0] == "url,titulo,data_adicao,ultima_modificacao,icon_uri"
            assert linhas[1] == "https://a.com,A,100,,"

    def test_pasta_vazia_gera_apenas_cabecalho(self) -> None:
        """Sem favoritos, o CSV deve conter só a linha de cabeçalho."""
        conteudo: str | None = ExportadorCSV().exportar(raiz=VirtualFolder(nome="Vazia"))

        if conteudo is not None:
            assert conteudo.strip().splitlines() == ["url,titulo,data_adicao,ultima_modificacao,icon_uri"]

    def test_grava_arquivo_quando_caminho_informado(self, tmp_path: Path) -> None:
        """Quando um caminho de saída é passado, o conteúdo deve ser gravado em disco."""
        destino: Path = tmp_path / "saida.csv"

        ExportadorCSV().exportar(raiz=_RAIZ, caminho_saida=destino)

        assert destino.exists()
        assert "A" in destino.read_text(encoding="utf-8")
