"""Testes para as funções de leitura e parsing de arquivos HTML de bookmarks."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from bs4 import BeautifulSoup, Tag

from src.aplicacao.leitura import (
    ler_arquivo_com_fallback,
    parsear_html,
    raiz_bookmarks,
)


@pytest.fixture
def caminho_da_fonte() -> Generator[Path, None, None]:
    """Cria um arquivo HTML temporário com um link simples."""
    content = """<DL><p>
        <DT><A HREF="https://example.com">Exemplo</A>
    </DL>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        path: str = f.name
    yield Path(path)
    os.unlink(path)


def test_ler_arquivo_utf8(caminho_da_fonte: Path) -> None:
    """Lê um arquivo UTF-8 e verifica se o conteúdo está correto."""
    conteudo: str = ler_arquivo_com_fallback(caminho=caminho_da_fonte)
    assert "Exemplo" in conteudo


def test_ler_arquivo_inexistente() -> None:
    """Garante que uma exceção é lançada ao tentar ler arquivo inexistente."""
    with pytest.raises(expected_exception=FileNotFoundError):
        ler_arquivo_com_fallback(caminho=Path("/arquivo/inexistente.html"))


def test_ler_arquivo_latin1(tmp_path: Path) -> None:
    """Garante o fallback de encoding quando o arquivo não é utf-8 válido."""
    path: Path = tmp_path / "latin1.html"
    path.write_text(data="<DL><DT><A HREF='café'>Café</A></DL>", encoding="latin-1")
    conteudo: str = ler_arquivo_com_fallback(caminho=path)
    assert "Café" in conteudo


def test_raiz_bookmarks_com_h1() -> None:
    """Encontra a tag <DL> após um <H1> (estrutura típica de bookmarks)."""
    soup: BeautifulSoup = parsear_html(conteudo="<h1>Bookmarks</h1><DL><DT><A HREF='x'>X</A></DL>")
    raiz: Tag | None = raiz_bookmarks(soup)
    assert raiz is not None
    assert raiz.name == "dl"


def test_raiz_bookmarks_sem_h1() -> None:
    """Encontra a tag <DL> diretamente quando não há <H1>."""
    soup: BeautifulSoup = parsear_html(conteudo="<DL><DT><A HREF='x'>X</A></DL>")
    raiz: Tag | None = raiz_bookmarks(soup)
    assert raiz is not None
    assert raiz.name == "dl"


def test_raiz_bookmarks_ausente() -> None:
    """Retorna None quando não existe tag <DL> no documento."""
    soup: BeautifulSoup = parsear_html(conteudo="<html><body>Sem DL</body></html>")
    assert raiz_bookmarks(soup) is None
