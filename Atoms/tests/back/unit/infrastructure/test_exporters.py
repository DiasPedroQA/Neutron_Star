# Atoms/tests/back/unit/infrastructure/test_exporters.py
# pylint: disable=redefined-outer-name

"""Testes para os exportadores CSV, JSON e PDF."""

from typing import Any
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from backend.core.entidades.entidade_bookmark import Favorito
from backend.infrastructure.exporters.csv_exporter import CSVExporter
from backend.infrastructure.exporters.json_exporter import JSONExporter
from backend.infrastructure.exporters.pdf_exporter import PDFExporter


FAVORITOS: list[Favorito] = [
    Favorito(
        titulo="Google",
        url="https://google.com",
        data_adicao=datetime(
            year=2025,
            month=1,
            day=1,
            tzinfo=timezone.utc,
        ),
    ),
    Favorito(
        titulo="Example",
        url="http://example.com",
    ),
]


class TestCSVExporter:
    """Testes para a exportação em CSV."""

    def test_exportar_cria_arquivo_csv(self, tmp_path: Path) -> None:
        """Verifica se o arquivo CSV é criado com os dados esperados."""
        saida: Path = tmp_path / "out.csv"

        CSVExporter().exportar(
            lista_favoritos=FAVORITOS,
            saida=saida,
        )

        assert saida.exists()

        with open(file=saida, newline="", encoding="utf-8") as f:
            reader: csv.DictReader[str] = csv.DictReader(f=f)
            rows: list[dict[str | Any, str | Any]] = list(reader)

        assert len(rows) == 2
        assert rows[0]["titulo"] == "Google"

    def test_lista_vazia_apenas_loga(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verifica se nenhum arquivo é criado para uma lista vazia."""
        saida: Path = tmp_path / "out.csv"

        CSVExporter().exportar(
            lista_favoritos=[],
            saida=saida,
        )

        assert not saida.exists()
        assert "Nenhum favorito" in caplog.text


class TestJSONExporter:
    """Testes para a exportação em JSON."""

    def test_exportar_cria_arquivo_json(self, tmp_path: Path) -> None:
        """Verifica se o arquivo JSON é criado com os dados esperados."""
        saida: Path = tmp_path / "out.json"

        JSONExporter().exportar(
            lista_favoritos=FAVORITOS,
            saida=saida,
        )

        assert saida.exists()

        with open(file=saida, encoding="utf-8") as f:
            data: dict[int, Any] = json.load(fp=f)

        assert len(data) == 2
        assert data[0]["titulo"] == "Google"

    def test_lista_vazia_apenas_loga(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verifica se nenhum arquivo é criado para uma lista vazia."""
        saida: Path = tmp_path / "out.json"

        JSONExporter().exportar(
            lista_favoritos=[],
            saida=saida,
        )

        assert not saida.exists()
        assert "Nenhum favorito" in caplog.text


class TestPDFExporter:
    """Testes para a exportação em PDF."""

    def test_exportar_cria_arquivo_pdf(self, tmp_path: Path) -> None:
        """Verifica se o arquivo PDF é gerado com conteúdo."""
        saida: Path = tmp_path / "out.pdf"

        PDFExporter().exportar(
            lista_favoritos=FAVORITOS,
            saida=saida,
        )

        assert saida.exists()
        assert saida.stat().st_size > 0
