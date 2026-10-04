"""Testes de caracterização da neutralização de fórmulas no CSV."""

import csv
from pathlib import Path

import pytest

from src.models.entidades import FavoritoDict
from src.models.escritores import EscritorLocal


@pytest.mark.characterization
def test_csv_prefixa_formulas_nas_colunas_nao_titulo(tmp_path: Path) -> None:
    """Preserva o prefixo apostrofado nas colunas CSV que não são título."""
    favorito: FavoritoDict = {
        "titulo": "Título seguro",
        "url": "=https://exemplo.com",
        "pasta": "  @pasta",
        "data_adicao": "-01/01/2026",
    }
    destino: str = EscritorLocal().salvar_lote(
        caminho_original=tmp_path / "entrada.html",
        dados=[favorito],
        extensao="csv",
    )

    with open(file=destino, encoding="utf-8-sig", newline="") as arquivo:
        linha: dict[str, str] = next(csv.DictReader(arquivo, delimiter=";"))

    assert linha == {
        "titulo": "Título seguro",
        "url": "'=https://exemplo.com",
        "pasta": "'  @pasta",
        "data_adicao": "'-01/01/2026",
    }
