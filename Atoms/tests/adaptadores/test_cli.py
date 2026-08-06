"""Testes de integração da CLI de bookmarks que exercitam os comandos de busca e conversão.

Verifica o comportamento de main() ao receber diferentes argumentos de linha de comando,
cobrindo cenários com resultados, ausência de saídas e erros de uso.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.adaptadores.cli import main


@pytest.fixture
def pasta_com_bookmarks(tmp_path: Path) -> Path:
    """
    Fixture que cria uma pasta com um arquivo de bookmarks HTML.

    :param tmp_path: Caminho temporário para a pasta
    :type tmp_path: Path
    :return: Caminho da pasta com os arquivos de bookmarks
    :rtype: Path
    """
    (tmp_path / "bookmarks.html").write_text(data="<DL><DT><A HREF='https://x.com'>X</A></DL>")
    return tmp_path


def test_comando_buscar_encontra_arquivos(
    pasta_com_bookmarks: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Docstring para test_comando_buscar_encontra_arquivos

    :param pasta_com_bookmarks: Caminho da pasta com os arquivos de bookmarks
    :type pasta_com_bookmarks: Path
    :param capsys: Fixture para capturar a saída do sistema
    :type capsys: pytest.CaptureFixture[str]
    """
    codigo: int = main(argv=["buscar", str(pasta_com_bookmarks)])
    saida: str = capsys.readouterr().out
    assert codigo == 0
    assert "bookmarks.html" in saida
    assert "1 links" in saida


def test_comando_buscar_pasta_vazia(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Docstring para test_comando_buscar_pasta_vazia

    :param tmp_path: Caminho temporário para a pasta
    :type tmp_path: Path
    :param capsys: Fixture para capturar a saída do sistema
    :type capsys: pytest.CaptureFixture[str]
    """
    codigo: int = main(argv=["buscar", str(tmp_path)])
    saida: str = capsys.readouterr().out
    assert codigo == 0
    assert "Encontrados: 0" in saida


def test_comando_converter_gera_arquivos(
    pasta_com_bookmarks: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Docstring para test_comando_converter_gera_arquivos

    :param pasta_com_bookmarks: Caminho da pasta com os arquivos de bookmarks
    :type pasta_com_bookmarks: Path
    :param capsys: Fixture para capturar a saída do sistema
    :type capsys: pytest.CaptureFixture[str]
    """
    entrada: Path = pasta_com_bookmarks / "bookmarks.html"
    codigo: int = main(argv=["converter", str(entrada), "--formatos", ".csv"])
    saida: str = capsys.readouterr().out
    assert codigo == 0
    assert "Gerado(s) 1 arquivo(s)" in saida
    assert (pasta_com_bookmarks / "bookmarks.csv").exists()


def test_comando_converter_sem_saida(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Docstring para test_comando_converter_sem_saida

    :param tmp_path: Caminho temporário para a pasta
    :type tmp_path: Path
    :param capsys: Fixture para capturar a saída do sistema
    :type capsys: pytest.CaptureFixture[str]
    """
    vazio: Path = tmp_path / "vazio.html"
    vazio.write_text("<DL><p></p></DL>")
    codigo: int = main(argv=["converter", str(vazio)])
    saida: str = capsys.readouterr().out
    assert codigo == 1
    assert "Nenhum arquivo gerado" in saida


def test_sem_comando_exige_subcomando() -> None:
    """
    Docstring para test_sem_comando_exige_subcomando

    :return: None
    """
    with pytest.raises(expected_exception=SystemExit):
        main(argv=[])
