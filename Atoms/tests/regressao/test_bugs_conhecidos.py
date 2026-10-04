# Atoms/tests/regressao/test_bugs_conhecidos.py

"""Testes de regressão para defeitos de produto já corrigidos."""

import csv
import re
from pathlib import Path

import pytest

from src.models.entidades import FavoritoDict
from src.models.escritores import EscritorLocal


def _favorito(titulo: str = "ok", url: str = "https://exemplo.com") -> FavoritoDict:
    """Monta um favorito mínimo válido para os testes de regressão."""
    return {"titulo": titulo, "url": url, "pasta": "Geral", "data_adicao": "01/01/2026"}


@pytest.mark.parametrize("titulo", ["=1+1", "+cmd", "-2+3", "@SUM(A1)"])
def test_csv_neutraliza_formulas_no_titulo(tmp_path: Path, titulo: str) -> None:
    """CSV deve neutralizar títulos que começam com ``= + - @`` (CSV injection)."""
    destino: str = EscritorLocal().salvar_lote(
        caminho_original=tmp_path / "in.html",
        dados=[_favorito(titulo)],
        extensao="csv",
    )

    with open(file=destino, encoding="utf-8-sig", newline="") as arquivo:
        celula: str = next(csv.DictReader(arquivo, delimiter=";"))["titulo"]

    assert celula[0] not in "=+-@"


def test_markdown_nao_quebra_colunas_com_pipe_na_url(tmp_path: Path) -> None:
    """Markdown deve escapar ``|`` na URL para não quebrar a tabela."""
    destino: str = EscritorLocal().salvar_lote(
        caminho_original=tmp_path / "in.html",
        dados=[_favorito(url="https://x.com/a|b")],
        extensao="md",
    )

    linha: str = Path(destino).read_text(encoding="utf-8").splitlines()[-1]
    separadores_sem_escape: list[str] = re.findall(r"(?<!\\)\|", linha)
    assert len(separadores_sem_escape) == 5  # 4 colunas => 5 delimitadores
