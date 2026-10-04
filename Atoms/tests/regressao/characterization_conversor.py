"""Testes de caracterização da conversão de favoritos Netscape."""

import json
from pathlib import Path

import pytest

from src.models.conversor import ConversorService
from src.models.entidades import StatusConversao


@pytest.mark.characterization
def test_extensao_com_ponto_e_maiuscula_grava_json_normalizado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Normaliza .JSON para .json e grava os favoritos como JSON válido."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    origem: Path = tmp_path / "favoritos.html"
    origem.write_text(
        """<!DOCTYPE NETSCAPE-Bookmark-file-1>
        <TITLE>Bookmarks</TITLE>
        <H1>Bookmarks</H1>
        <DL><p>
            <DT><A HREF="https://exemplo.com">Exemplo</A>
        </DL><p>
        """,
        encoding="utf-8",
    )
    servico: ConversorService = ConversorService()

    eventos: list[StatusConversao] = list(servico.converter_com_progresso([str(origem)], ".JSON"))

    assert eventos[-1]["sucesso"] is True
    destino: Path = Path(eventos[-1]["arquivos_convertidos"][0]["arquivo_destino"])
    assert destino.suffix == ".json"
    assert json.loads(destino.read_text(encoding="utf-8")) == [
        {
            "titulo": "Exemplo",
            "url": "https://exemplo.com",
            "pasta": "Favoritos",
            "data_adicao": "Sem data",
        }
    ]
