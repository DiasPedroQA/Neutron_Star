"""Testes do caso de uso de processamento de bookmarks em lote."""

from pathlib import Path

from aplicacao.casos_de_uso.processar_lote import (
    processar_arquivo_individual,
    processar_arquivos_em_lote,
)
from dominio.entidades import VirtualFolder
from dominio.excecoes import ErroBookmarks

_HTML_VALIDO = """
<DL><p>
    <DT><A HREF="https://a.com">Site A</A>
</DL><p>
"""


class TestProcessarArquivoIndividual:
    """Extração e exportação de um único arquivo nos formatos pedidos."""

    def test_exporta_nos_formatos_pedidos_ao_lado_do_original(self, tmp_path: Path) -> None:
        """Sem diretorio_saida, os arquivos exportados devem ficar ao lado do original."""
        arquivo: Path = tmp_path / "bookmarks.html"
        arquivo.write_text(data=_HTML_VALIDO, encoding="utf-8")

        raiz: VirtualFolder | None = processar_arquivo_individual(arquivo=arquivo, formatos=[".json", ".md"])

        assert isinstance(raiz, VirtualFolder)
        assert (tmp_path / "bookmarks.json").exists()
        assert (tmp_path / "bookmarks.md").exists()

    def test_usa_diretorio_saida_quando_informado(self, tmp_path: Path) -> None:
        """Com diretorio_saida, os arquivos exportados devem ir para essa pasta, não ao lado do original."""
        origem: Path = tmp_path / "origem"
        origem.mkdir()
        arquivo: Path = origem / "bookmarks.html"
        arquivo.write_text(data=_HTML_VALIDO, encoding="utf-8")
        destino: Path = tmp_path / "saida"

        processar_arquivo_individual(arquivo=arquivo, formatos=[".json"], diretorio_saida=destino)

        assert (destino / "bookmarks.json").exists()
        assert not (origem / "bookmarks.json").exists()


class TestProcessarArquivosEmLote:
    """Processamento de múltiplos arquivos sem interromper no primeiro erro."""

    def test_processa_todos_os_arquivos_validos(self, tmp_path: Path) -> None:
        """Todos os arquivos válidos devem ser processados e não retornar falhas."""
        arquivo_a: Path = tmp_path / "a.html"
        arquivo_b: Path = tmp_path / "b.html"
        arquivo_a.write_text(data=_HTML_VALIDO, encoding="utf-8")
        arquivo_b.write_text(data=_HTML_VALIDO, encoding="utf-8")

        falhas: dict[Path, ErroBookmarks] = processar_arquivos_em_lote(
            arquivos=[arquivo_a, arquivo_b], formatos=[".json"]
        )

        assert not falhas
        assert (tmp_path / "a.json").exists()
        assert (tmp_path / "b.json").exists()

    def test_arquivo_invalido_nao_interrompe_o_processamento_dos_demais(self, tmp_path: Path) -> None:
        """Um arquivo que falha na extração deve ser registrado em falhas, sem parar o lote."""
        arquivo_invalido: Path = tmp_path / "invalido.html"
        arquivo_invalido.write_text(data="<html>sem bookmarks aqui</html>", encoding="utf-8")
        arquivo_valido: Path = tmp_path / "valido.html"
        arquivo_valido.write_text(data=_HTML_VALIDO, encoding="utf-8")

        falhas: dict[Path, ErroBookmarks] = processar_arquivos_em_lote(
            arquivos=[arquivo_invalido, arquivo_valido], formatos=[".json"]
        )

        assert list(falhas.keys()) == [arquivo_invalido]
        assert (tmp_path / "valido.json").exists()
