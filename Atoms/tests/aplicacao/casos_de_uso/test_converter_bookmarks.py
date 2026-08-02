from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pandas as pd
import pytest
from pandas import DataFrame

from src.aplicacao.casos_de_uso.converter_bookmarks import (
    adicionar_favicon_url,
    converter_arquivos,
    parse_bookmarks_html,
)


@pytest.fixture
def html_simples() -> Generator[Path, None, None]:
    content = """<DL><p>
        <DT><A HREF="https://example.com" ADD_DATE="123456">Exemplo</A>
    </DL>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        path: str = f.name
    yield Path(path)
    os.unlink(path)


@pytest.fixture
def html_aninhado() -> Generator[Path, None, None]:
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
        path: str = f.name
    yield Path(path)
    os.unlink(path)


@pytest.fixture
def html_vazio() -> Generator[Path, None, None]:
    content = """<DL><p></p></DL>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        path: str = f.name
    yield Path(path)
    os.unlink(path)


# ---------------------------------------------------------------------------
# Testes do parse_bookmarks_html
# ---------------------------------------------------------------------------


def test_parse_simples(html_simples: Path) -> None:
    df: DataFrame = parse_bookmarks_html(html_path=html_simples)
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Exemplo"
    assert df.iloc[0]["url"] == "https://example.com"
    assert df.iloc[0]["add_date"] == "123456"
    assert df.iloc[0]["folder"] == ""
    assert "icon" not in df.columns


def test_parse_com_icone(html_simples: Path) -> None:
    df: DataFrame = parse_bookmarks_html(html_path=html_simples, extrair_icone=True)
    assert "icon" in df.columns


def test_parse_aninhado(html_aninhado: Path) -> None:
    df: DataFrame = parse_bookmarks_html(html_path=html_aninhado)
    assert len(df) == 3
    link_a = df[df["title"] == "Link A"].iloc[0]
    assert link_a["folder"] == "Pasta A"
    link_b = df[df["title"] == "Link B"].iloc[0]
    assert link_b["folder"] == "Pasta A/Subpasta"
    link_c = df[df["title"] == "Link C"].iloc[0]
    assert link_c["folder"] == ""


def test_parse_vazio(html_vazio: Path) -> None:
    df: DataFrame = parse_bookmarks_html(html_path=html_vazio)
    assert df.empty


def test_parse_arquivo_inexistente() -> None:
    with pytest.raises(expected_exception=FileNotFoundError):
        parse_bookmarks_html(html_path=Path("/arquivo/inexistente.html"))


# ---------------------------------------------------------------------------
# Testes do favicon
# ---------------------------------------------------------------------------


def test_adicionar_favicon_url_normal() -> None:
    df = pd.DataFrame(data={"url": ["https://github.com/explore", "https://chat.deepseek.com/"]})
    result: DataFrame = adicionar_favicon_url(df, size=16)
    assert "favicon_url" in result.columns
    assert "domain=github.com" in result.iloc[0]["favicon_url"]
    assert "domain=chat.deepseek.com" in result.iloc[1]["favicon_url"]
    assert "sz=16" in result.iloc[0]["favicon_url"]


def test_adicionar_favicon_url_invalida() -> None:
    df = pd.DataFrame(data={"url": ["not_a_valid_url"]})
    result: DataFrame = adicionar_favicon_url(df)
    assert result.iloc[0]["favicon_url"] == "Icone nao encontrado"


# ---------------------------------------------------------------------------
# Testes da função converter_arquivos
# ---------------------------------------------------------------------------


def test_converter_basico(html_simples: Path, tmp_path: Path) -> None:
    shutil.copy(html_simples, tmp_path / "book.html")
    entrada: Path = tmp_path / "book.html"
    res: list[Path] = converter_arquivos(lista_paths=[entrada], output_formats=[".csv", ".json"])
    assert len(res) == 2
    for p in res:
        assert p.exists()


def test_converter_com_sufixo(html_simples: Path, tmp_path: Path) -> None:
    shutil.copy(html_simples, tmp_path / "book.html")
    entrada: Path = tmp_path / "book.html"
    res: list[Path] = converter_arquivos(
        lista_paths=[entrada], output_formats=[".xlsx"], sufixo_saida="_dados"
    )
    assert len(res) == 1
    assert res[0].name == "book_dados.xlsx"


def test_converter_formato_invalido(
    html_simples: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("WARNING")
    shutil.copy(html_simples, tmp_path / "book.html")
    entrada: Path = tmp_path / "book.html"
    res: list[Path] = converter_arquivos(lista_paths=[entrada], output_formats=[".docx"])
    assert not res
    assert "não possui escritor" in caplog.text


def test_converter_dataframe_vazio(
    html_vazio: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("WARNING")
    shutil.copy(html_vazio, tmp_path / "empty.html")
    entrada: Path = tmp_path / "empty.html"
    res: list[Path] = converter_arquivos(lista_paths=[entrada])
    assert not res
    assert "DataFrame vazio" in caplog.text


def test_converter_erro_parser(tmp_path: Path) -> None:
    def bad_parser(path: Path) -> DataFrame:
        raise ValueError("Falha simulada")

    p: Path = tmp_path / "test.html"
    p.write_text("dummy")
    res: list[Path] = converter_arquivos(lista_paths=[p], parser=bad_parser)
    assert not res
