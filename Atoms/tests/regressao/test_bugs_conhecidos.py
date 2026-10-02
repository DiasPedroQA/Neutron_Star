# Atoms/tests/regressao/test_bugs_conhecidos.py

"""Livro de bugs confirmados (defeitos de produto ainda NÃO corrigidos).

Cada teste descreve o comportamento CORRETO e está marcado ``xfail(strict=True)``:
- a suíte continua verde enquanto o bug existe;
- quando alguém corrigir o bug, o teste vira XPASS e FALHA a build, obrigando a remover
  a marcação (o bug sai do livro e vira teste de regressão comum).
"""

import csv
import re
from pathlib import Path

import pytest

from src.models.entidades import FavoritoDict
from src.models.escritores import EscritorLocal


def _favorito(titulo: str = "ok", url: str = "https://exemplo.com") -> FavoritoDict:
    """Monta um favorito mínimo válido para os testes de regressão."""
    return {"titulo": titulo, "url": url, "pasta": "Geral", "data_adicao": "01/01/2026"}


@pytest.mark.xfail(strict=True, reason="BUG-002: CSV injection (título iniciando com = + - @)")
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


@pytest.mark.xfail(strict=True, reason="BUG-003: URL com '|' ou ')' quebra a tabela/link Markdown")
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
