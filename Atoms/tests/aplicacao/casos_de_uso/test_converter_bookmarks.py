"""Testes para os casos de uso de conversão de bookmarks."""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pandas as pd
import pytest
from pandas import DataFrame, Series

from aplicacao.casos_de_uso.converter_bookmarks import (
    adicionar_favicon_url,
    converter_arquivos,
    parse_bookmarks_html,
)


@pytest.fixture
def caminho_da_fonte() -> Generator[Path, None, None]:
    """Cria um arquivo HTML temporário com bookmarks simples para testes."""
    content = """<DL><p>
        <DT><A HREF="https://example.com" ADD_DATE="123456">Exemplo</A>
    </DL>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        file_path: str = f.name
    yield Path(file_path)
    os.unlink(file_path)


@pytest.fixture
def html_aninhado() -> Generator[Path, None, None]:
    """Cria um arquivo HTML temporário com bookmarks aninhados em pastas para testes."""
    content = """<DL><p>
        <DT><H3 ADD_DATE="100000">Pasta A</H3>
        <DL><p>
            <DT><A HREF="https://a.com" ADD_DATE="111111">Link A</A>
            <DT><H3 ADD_DATE="200000">Subpasta</H3>
            <DL><p>
                <DT><A HREF="https://b.com" ADD_DATE="222222">Link B</A>
            </DL>
        </DL>
        <DT><A HREF="https://c.com" ADD_DATE="333333">Link C</A>
    </DL>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        file_path: str = f.name
    yield Path(file_path)
    os.unlink(file_path)


@pytest.fixture
def html_vazio() -> Generator[Path, None, None]:
    """Cria um arquivo HTML temporário vazio para testes."""
    content = """<DL><p></p></DL>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        file_path: str = f.name
    yield Path(file_path)
    os.unlink(file_path)


# ---------------------------------------------------------------------------
# Testes do parse_bookmarks_html
# ---------------------------------------------------------------------------


def test_parse_simples(caminho_da_fonte: Path) -> None:
    """Testa o parse de um arquivo HTML simples com bookmarks."""
    df: DataFrame = parse_bookmarks_html(html_path=caminho_da_fonte)
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Exemplo"
    assert df.iloc[0]["url"] == "https://example.com"
    assert df.iloc[0]["add_date"] == "123456"
    assert df.iloc[0]["folder"] == ""
    assert "icon" not in df.columns


def test_parse_com_icone(caminho_da_fonte: Path) -> None:
    """Testa o parse de um arquivo HTML simples com bookmarks, extraindo o ícone."""
    df: DataFrame = parse_bookmarks_html(html_path=caminho_da_fonte, extrair_icone=True)
    assert "icon" in df.columns


def test_parse_aninhado(html_aninhado: Path) -> None:
    """Testa o parse de um arquivo HTML com bookmarks aninhados em pastas."""
    df: DataFrame = parse_bookmarks_html(html_path=html_aninhado)
    assert len(df) == 3
    link_a: Series = df[df["title"] == "Link A"].iloc[0]
    assert link_a["folder"] == "Pasta A"
    link_b: Series = df[df["title"] == "Link B"].iloc[0]
    assert link_b["folder"] == "Pasta A/Subpasta"
    link_c: Series = df[df["title"] == "Link C"].iloc[0]
    assert link_c["folder"] == ""


def test_parse_vazio(html_vazio: Path) -> None:
    """Testa o comportamento do parse_bookmarks_html quando o arquivo HTML está vazio."""
    df: DataFrame = parse_bookmarks_html(html_path=html_vazio)
    assert df.empty


def test_parse_arquivo_inexistente() -> None:
    """Testa o comportamento do parse_bookmarks_html quando o arquivo HTML não existe."""
    with pytest.raises(expected_exception=FileNotFoundError):
        parse_bookmarks_html(html_path=Path("/arquivo/inexistente.html"))


# ---------------------------------------------------------------------------
# Testes do favicon
# ---------------------------------------------------------------------------


def test_adicionar_favicon_url_normal() -> None:
    """Testa a adição de URL de favicon para URLs válidas."""
    df = pd.DataFrame(data={"url": ["https://github.com/explore", "https://chat.deepseek.com/"]})
    result: DataFrame = adicionar_favicon_url(df, size=16)
    assert "favicon_url" in result.columns
    assert "domain=github.com" in result.iloc[0]["favicon_url"]
    assert "domain=chat.deepseek.com" in result.iloc[1]["favicon_url"]
    assert "sz=16" in result.iloc[0]["favicon_url"]


def test_adicionar_favicon_url_invalida() -> None:
    """Testa a adição de URL de favicon para uma URL inválida."""
    df = pd.DataFrame(data={"url": ["not_a_valid_url"]})
    result: DataFrame = adicionar_favicon_url(df)
    assert result.iloc[0]["favicon_url"] == "Icone nao encontrado"


# ---------------------------------------------------------------------------
# Testes da função converter_arquivos
# ---------------------------------------------------------------------------


def test_converter_basico(caminho_da_fonte: Path, caminho_de_destino: Path) -> None:
    """Testa a conversão de um arquivo HTML para CSV e JSON."""
    shutil.copy(caminho_da_fonte, caminho_de_destino / "book.html")
    entrada: Path = caminho_de_destino / "book.html"
    res: list[Path] = converter_arquivos(lista_paths=[entrada], output_formats=[".csv", ".json"])
    assert len(res) == 2
    for p in res:
        assert p.exists()


def test_converter_com_sufixo(caminho_da_fonte: Path, caminho_de_destino: Path) -> None:
    """Testa a conversão de um arquivo HTML para XLSX com sufixo no nome do arquivo de saída."""
    shutil.copy(caminho_da_fonte, caminho_de_destino / "book.html")
    entrada: Path = caminho_de_destino / "book.html"
    res: list[Path] = converter_arquivos(
        lista_paths=[entrada], output_formats=[".xlsx"], sufixo_saida="_dados"
    )
    assert len(res) == 1
    assert res[0].name == "book_dados.xlsx"


def test_converter_formato_invalido(
    caminho_da_fonte: Path, caminho_de_destino: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Testa a conversão de um arquivo HTML para um formato inválido, verificando se o log de aviso é gerado corretamente."""
    caplog.set_level("WARNING")
    shutil.copy(caminho_da_fonte, caminho_de_destino / "book.html")
    entrada: Path = caminho_de_destino / "book.html"
    res: list[Path] = converter_arquivos(lista_paths=[entrada], output_formats=[".docx"])
    assert not res
    assert "não possui escritor" in caplog.text


def test_converter_dataframe_vazio(
    html_vazio: Path, caminho_de_destino: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Testa o comportamento do conversor quando o DataFrame resultante da leitura do arquivo HTML está vazio."""
    caplog.set_level("WARNING")
    shutil.copy(html_vazio, caminho_de_destino / "empty.html")
    entrada: Path = caminho_de_destino / "empty.html"
    res: list[Path] = converter_arquivos(lista_paths=[entrada])
    assert not res
    assert "DataFrame vazio" in caplog.text


def test_converter_erro_parser(caminho_de_destino: Path) -> None:
    """Testa o comportamento do conversor quando o parser falha durante a leitura do arquivo."""

    def bad_parser(path: Path) -> DataFrame:
        raise ValueError(f"Falha simulada no arquivo {path}")

    p: Path = caminho_de_destino / "test.html"
    p.write_text("dummy", encoding="utf-8")
    res: list[Path] = converter_arquivos(lista_paths=[p], parser=bad_parser)
    assert not res
