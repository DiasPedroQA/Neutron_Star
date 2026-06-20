# Atoms/tests/back/unit/infrastructure/test_file_scanners.py
# pylint: disable=redefined-outer-name

"""Testes para o varredor de sistema de arquivos."""

import pytest
from pathlib import Path
from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.infrastructure.controllers.file_scanners import VarredorSistemaArquivos


@pytest.fixture
def scanner() -> VarredorSistemaArquivos:
    return VarredorSistemaArquivos()


@pytest.fixture
def estrutura_teste(tmp_path: Path) -> Path:
    """Cria uma estrutura de diretórios e arquivos de teste."""
    raiz: Path = tmp_path / "home"
    raiz.mkdir()
    (raiz / "bookmarks_25_12_2023.html").write_text(data="<html></html>")
    (raiz / "favorito_01_01_2024.htm").write_text(data="<html></html>")
    (raiz / "notas.txt").write_text(data="nada")
    (raiz / ".oculto").mkdir()
    (raiz / "sub").mkdir()
    (raiz / "sub" / "bookmark_10_05_2022.html").write_text(data="<html></html>")
    return raiz


def test_varredura_completa(
    scanner: VarredorSistemaArquivos, estrutura_teste: Path
) -> None:
    """Testa a varredura e coleta de HTMLs."""
    pasta_raiz = ModeloPasta(nome_pasta="home", caminho_absoluto=estrutura_teste)
    scanner.varrer_diretorio(pasta_raiz=pasta_raiz)
    htmls: list[ModeloArquivo] = scanner.localizar_arquivos_html(pasta=pasta_raiz)
    assert len(htmls) == 3  # 2 na raiz + 1 na subpasta


def test_diretorio_inexistente_loga_warning(
    scanner: VarredorSistemaArquivos, caplog: pytest.LogCaptureFixture
) -> None:
    import logging

    caplog.set_level(level=logging.WARNING)
    pasta = ModeloPasta(
        nome_pasta="fantasma", caminho_absoluto=Path("/caminho/inexistente")
    )
    scanner.varrer_diretorio(pasta)
    assert "não existe" in caplog.text


def test_ignora_diretorios_ocultos(
    scanner: VarredorSistemaArquivos, tmp_path: Path
) -> None:
    raiz: Path = tmp_path / "raiz"
    raiz.mkdir()
    (raiz / ".oculto").mkdir()
    (raiz / ".oculto" / "ignorado.html").write_text(data="<html></html>")
    pasta_raiz = ModeloPasta(nome_pasta="raiz", caminho_absoluto=raiz)
    scanner.varrer_diretorio(pasta_raiz=pasta_raiz)
    htmls: list[ModeloArquivo] = scanner.localizar_arquivos_html(pasta_raiz)
    assert len(htmls) == 0  # pasta oculta é ignorada


def test_alias_scan_recursive(
    scanner: VarredorSistemaArquivos, estrutura_teste: Path
) -> None:
    pasta = ModeloPasta(nome_pasta="home", caminho_absoluto=estrutura_teste)
    scanner._scan_recursive(pasta_atual=pasta)
    assert len(pasta.subpastas) == 1
