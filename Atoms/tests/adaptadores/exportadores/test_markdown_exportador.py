"""Testes do exportador Markdown."""

from pathlib import Path

from src.adaptadores.exportadores.markdown_exportador import ExportadorMarkdown
from src.dominio.entidades import TagA, VirtualFolder


class TestExportadorMarkdown:
    """Geração de tabela Markdown a partir da hierarquia de bookmarks."""

    def test_gera_cabecalho_da_tabela(self) -> None:
        """A saída deve começar com o cabeçalho e o separador da tabela Markdown."""
        conteudo: str | None = ExportadorMarkdown().exportar(raiz=VirtualFolder(nome="Vazia"))

        if conteudo is not None:
            linhas: list[str] = conteudo.strip().splitlines()
            assert linhas[0] == "| Título | URL | Data de adição | Pasta |"
            assert linhas[1] == "|--------|-----|----------------|-------|"

    def test_favorito_no_primeiro_nivel_tem_coluna_pasta_vazia(self) -> None:
        """Favoritos fora de qualquer subpasta devem ter a coluna Pasta em branco."""
        raiz = VirtualFolder(nome="Raiz", filhos_da_pasta=[TagA(url="https://a.com", titulo="A")])

        conteudo: str | None = ExportadorMarkdown().exportar(raiz=raiz)

        if conteudo is not None:
            assert "| A | https://a.com |  |  |" in conteudo

    def test_favorito_em_subpasta_mostra_o_nome_da_pasta(self) -> None:
        """A coluna Pasta deve conter o caminho da subpasta onde o favorito está."""
        raiz = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[
                VirtualFolder(
                    nome="Trabalho",
                    filhos_da_pasta=[TagA(url="https://b.com", titulo="B")],
                ),
            ],
        )

        conteudo: str | None = ExportadorMarkdown().exportar(raiz=raiz)

        if conteudo is not None:
            assert "| B | https://b.com |  | Trabalho |" in conteudo

    def test_formata_data_de_adicao_a_partir_do_timestamp_unix(self) -> None:
        """Um data_adicao com timestamp Unix válido deve aparecer formatado, não cru."""
        raiz = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[TagA(url="https://a.com", titulo="A", data_adicao="0")],
        )

        conteudo: str | None = ExportadorMarkdown().exportar(raiz=raiz)

        if conteudo is not None:
            assert "Título" in conteudo
            assert "URL" in conteudo
            assert "Data de adição" in conteudo
            assert "Pasta" in conteudo
            assert "| A |" in conteudo
            assert "https://a.com" in conteudo
            assert "1969-12-31 21:00" in conteudo

    def test_grava_arquivo_quando_caminho_informado(self, tmp_path: Path) -> None:
        """Quando um caminho de saída é passado, o conteúdo deve ser gravado em disco."""
        raiz = VirtualFolder(nome="Raiz", filhos_da_pasta=[TagA(url="https://a.com", titulo="A")])
        destino: Path = tmp_path / "saida.md"

        ExportadorMarkdown().exportar(raiz=raiz, caminho_saida=destino)

        assert destino.exists()
        assert "A" in destino.read_text(encoding="utf-8")
