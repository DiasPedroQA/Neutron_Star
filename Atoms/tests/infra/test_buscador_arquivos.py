"""Testes do adaptador de diretório local."""

from pathlib import Path

from dominio.entidades import ArquivoTemp
from infra.buscador import PastaBuscadora


def test_extrair_stats_cria_entidade_com_metadados_do_arquivo(tmp_path: Path) -> None:
    """O adaptador transforma os metadados de um arquivo em uma entidade de domínio."""
    caminho: Path = tmp_path / "bookmarks.html"
    caminho.write_text("<html></html>", encoding="utf-8")

    arquivo: ArquivoTemp = PastaBuscadora().extrair_stats_do_arquivo(caminho)

    assert arquivo.nome == "bookmarks.html"
    assert arquivo.caminho_absoluto == str(caminho.resolve())
    assert arquivo.tamanho == len("<html></html>")
    assert arquivo.conteudo is None
