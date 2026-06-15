# pylint: disable=redefined-outer-name

"""Testes de infraestrutura, serviços e apresentação do Neutron Star."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from Atoms.backend.core.entidades.entidade_bookmark import Favorito
from Atoms.backend.infrastructure.exporters.csv_exporter import CSVExporter
from Atoms.backend.infrastructure.exporters.json_exporter import JSONExporter
from Atoms.backend.infrastructure.exporters.pdf_exporter import PDFExporter


class TestExporters:
    """Testes para os exportadores de favoritos em diferentes formatos.

    Esta classe verifica se os exportadores geram arquivos válidos e lidam corretamente com casos especiais como listas vazias.
    """

    def test_json_exporter_writes_json(self, tmp_path: Path) -> None:
        """Verifica se o exportador JSON grava um arquivo JSON válido.

        Este teste garante que os dados persistidos podem ser carregados como JSON e preservam os campos principais do bookmark.

        Args:
            tmp_path: Diretório temporário usado como destino para o arquivo JSON exportado.
        """
        favoritos: list[Favorito] = [
            Favorito(
                titulo="Example",
                url="https://example.com",
                data_adicao=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out.json"

        JSONExporter().export(favoritos=favoritos, saida=saida)

        assert saida.exists()
        data = json.loads(saida.read_text(encoding="utf-8"))
        assert data[0]["url"] == "https://example.com"

    def test_csv_exporter_writes_csv(self, tmp_path: Path) -> None:
        """Verifica se o exportador CSV grava um arquivo CSV válido.

        Este teste garante que o arquivo gerado contém as colunas esperadas e preserva os dados dos favoritos.

        Args:
            tmp_path: Diretório temporário usado como destino para o arquivo CSV exportado.
        """
        favoritos: list[Favorito] = [
            Favorito(
                titulo="Example",
                url="https://example.com",
                data_adicao=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out.csv"

        CSVExporter().export(favoritos=favoritos, saida=saida)

        assert saida.exists()
        with saida.open(encoding="utf-8", newline="") as f:
            reader: csv.DictReader[str] = csv.DictReader(f)
            rows: list[dict[str | Any, str | Any]] = list(reader)

        assert rows[0]["titulo"] == "Example"

    def test_csv_exporter_ignora_lista_vazia(self, tmp_path: Path) -> None:
        """Verifica se o exportador CSV não cria arquivos quando a lista está vazia.

        Este teste garante que nenhuma saída é gerada em disco quando não há favoritos para exportar.

        Args:
            tmp_path: Diretório temporário usado como destino potencial para o arquivo CSV.
        """
        saida: Path = tmp_path / "out.csv"

        CSVExporter().export(favoritos=[], saida=saida)

        assert not saida.exists()

    def test_json_exporter_writes_empty_array(self, tmp_path: Path) -> None:
        """Verifica se o exportador JSON grava um array vazio quando não há favoritos.

        Este teste garante que o arquivo gerado existe e representa corretamente uma coleção vazia em formato JSON.

        Args:
            tmp_path: Diretório temporário usado como destino para o arquivo JSON exportado.
        """
        saida: Path = tmp_path / "out.json"

        JSONExporter().export(favoritos=[], saida=saida)

        assert saida.exists()
        assert json.loads(saida.read_text(encoding="utf-8")) == []

    def test_pdf_exporter_builds_file(self, tmp_path: Path) -> None:
        """Verifica se o exportador PDF gera um arquivo PDF não vazio.

        Este teste garante que, dado ao menos um bookmark, o arquivo PDF é criado no disco com algum conteúdo gravado.

        Args:
            tmp_path: Diretório temporário usado como destino para o arquivo PDF exportado.
        """
        pytest.importorskip("reportlab")

        favoritos: list[Favorito] = [
            Favorito(
                titulo="Example",
                url="https://example.com",
                data_adicao=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out.pdf"

        PDFExporter().export(favoritos=favoritos, saida=saida)

        assert saida.exists()
        assert saida.stat().st_size > 0
