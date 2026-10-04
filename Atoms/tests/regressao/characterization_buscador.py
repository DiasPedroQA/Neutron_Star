"""Testes de caracterização dos limites de varredura do buscador local."""

from pathlib import Path

import pytest

from src.models.buscador import BuscadorLocal
from src.models.entidades import ResultadoEscaneamento


@pytest.mark.characterization
def test_escanear_limite_um_interrompe_antes_da_pasta_filha(tmp_path: Path) -> None:
    """Limita a varredura aos arquivos da raiz quando o limite é excedido."""
    arquivo_raiz: Path = tmp_path / "raiz.html"
    arquivo_raiz.write_text(data="<html></html>", encoding="utf-8")
    pasta_filha: Path = tmp_path / "filha"
    pasta_filha.mkdir()
    (pasta_filha / "filho.html").write_text(data="<html></html>", encoding="utf-8")

    resultado: ResultadoEscaneamento = BuscadorLocal(max_arquivos=1).escanear(
        caminho=tmp_path,
        profundidade=1,
    )

    assert [item["nome"] for item in resultado["arquivos"]] == [arquivo_raiz.name]
    assert resultado["total_arquivos"] == 1
