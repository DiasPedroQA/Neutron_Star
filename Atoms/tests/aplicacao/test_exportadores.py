"""
Testes para os exportadores de DataFrame para diferentes formatos de arquivo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from pandas import DataFrame

from src.aplicacao.exportadores import (
    write_csv,
    write_excel,
    write_json,
    write_md,
    write_parquet,
    write_xml,
)


@pytest.fixture
def df_exemplo() -> DataFrame:
    """Cria um DataFrame de exemplo para os testes."""
    return pd.DataFrame(
        {
            "title": ["Site 1", "Site 2"],
            "url": ["https://example.com/um", "https://example.org/dois"],
            "add_date": ["123", "456"],
            "folder": ["Pasta", ""],
        }
    )


def test_write_csv(df_exemplo: DataFrame, tmp_path: Path) -> None:
    """Testa a exportação para CSV e a leitura de volta."""
    out: Path = tmp_path / "test.csv"
    write_csv(df=df_exemplo, output_path=out)
    assert out.exists()
    df_back: DataFrame = pd.read_csv(filepath_or_buffer=out)
    assert len(df_back) == 2


def test_write_excel(df_exemplo: DataFrame, tmp_path: Path) -> None:
    """Testa a exportação para Excel e a leitura de volta."""
    out: Path = tmp_path / "test.xlsx"
    write_excel(df=df_exemplo, output_path=out)
    assert out.exists()
    df_back: DataFrame = pd.read_excel(out)
    assert len(df_back) == 2


def test_write_json_sem_escape(df_exemplo: DataFrame, tmp_path: Path) -> None:
    """Testa a exportação para JSON e garante que não haja escape desnecessário de barras."""
    out: Path = tmp_path / "test.json"
    write_json(df=df_exemplo, output_path=out)
    assert out.exists()
    with open(file=out, encoding="utf-8") as f:
        texto: str = f.read()
    assert "\\/" not in texto
    data: Any = json.loads(texto)
    assert len(data) == 2
    assert data[0]["url"] == "https://example.com/um"


def test_write_xml(df_exemplo: DataFrame, tmp_path: Path) -> None:
    """Testa a exportação para XML e a leitura de volta."""
    out: Path = tmp_path / "test.xml"
    write_xml(df=df_exemplo, output_path=out)
    assert out.exists()
    soup: BeautifulSoup = BeautifulSoup(markup=out.read_text(encoding="utf-8"), features="xml")
    assert len(soup.find_all("link")) == 2


def test_write_md(df_exemplo: DataFrame, tmp_path: Path) -> None:
    """Testa a exportação para Markdown e verifica se o arquivo contém as colunas esperadas."""
    out: Path = tmp_path / "test.md"
    write_md(df=df_exemplo, output_path=out)
    assert out.exists()
    conteudo: str = out.read_text(encoding="utf-8")
    assert "| title" in conteudo
    assert "| url" in conteudo


def test_write_parquet(df_exemplo: DataFrame, tmp_path: Path) -> None:
    """Testa a exportação para Parquet e a leitura de volta."""
    out: Path = tmp_path / "test.parquet"
    write_parquet(df=df_exemplo, output_path=out)
    assert out.exists()
    df_back: DataFrame = pd.read_parquet(out)
    assert len(df_back) == 2
