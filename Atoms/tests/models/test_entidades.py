# Atoms/tests/models/test_entidades.py

"""Testes unitários para a entidade Favorito e estruturas de dados de transporte."""

import dataclasses

import pytest

from src.models.entidades import (
    ArquivoConvertido,
    Favorito,
    FavoritoDict,
    StatusConversao,
)


def test_favorito_instanciacao_padrao() -> None:
    """Garante valores padrão e imutabilidade da entidade Favorito."""
    fav = Favorito(titulo="Portal", url="https://exemplo.com")

    assert fav.titulo == "Portal"
    assert fav.url == "https://exemplo.com"
    assert fav.pasta == "Favoritos"
    assert fav.data_adicao == "Sem data"

    # Garante que a dataclass é congelada (frozen)
    with pytest.raises(expected_exception=dataclasses.FrozenInstanceError):
        fav.titulo = "Novo Título"  # type: ignore[misc]


def test_favorito_com_parametros_completos() -> None:
    """Garante instanciação com todos os parâmetros preenchidos."""
    fav = Favorito(
        titulo="Documentação",
        url="https://docs.python.org",
        pasta="Dev / Python",
        data_adicao="27/09/2026 12:00:00",
    )
    assert fav.pasta == "Dev / Python"
    assert fav.data_adicao == "27/09/2026 12:00:00"


def test_contratos_typed_dicts() -> None:
    """Valida a conformidade das estruturas de dados TypedDict."""
    valor_esperado: int = 5
    fav_dict: FavoritoDict = {
        "titulo": "Site",
        "url": "https://site.com",
        "pasta": "Geral",
        "data_adicao": "01/01/2026",
    }
    assert fav_dict["titulo"] == "Site"
    assert fav_dict["data_adicao"] == "01/01/2026"
    convertido: ArquivoConvertido = {
        "arquivo_origem": "a.html",
        "arquivo_destino": "a.json",
        "total_links": 5,
    }
    assert convertido["total_links"] == valor_esperado

    status: StatusConversao = {
        "progresso": 100,
        "arquivo_atual": "a.html",
        "arquivos_convertidos": [convertido],
        "erros": [],
        "concluido": True,
        "sucesso": True,
    }
    assert status["concluido"] is True
