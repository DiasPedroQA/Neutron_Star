# Atoms/tests/dominio/test_entidades.py

"""Testes unitários para a entidade de domínio Favorito."""

import dataclasses

import pytest

from src.dominio.entidades import Favorito


def test_criacao_com_todos_os_campos_preserva_os_valores() -> None:
    """Garante que todos os campos explícitos são armazenados sem alteração."""
    favorito = Favorito(
        titulo="GitHub",
        url="https://github.com",
        pasta="Trabalho / Dev",
        data_adicao="2026-01-15",
    )

    assert favorito.titulo == "GitHub"
    assert favorito.url == "https://github.com"
    assert favorito.pasta == "Trabalho / Dev"
    assert favorito.data_adicao == "2026-01-15"


def test_criacao_sem_pasta_e_data_usa_valores_padrao() -> None:
    """Garante os defaults 'Favoritos' e 'Sem data' quando não informados."""
    favorito = Favorito(titulo="GitHub", url="https://github.com")

    assert favorito.pasta == "Favoritos"
    assert favorito.data_adicao == "Sem data"


def test_url_vazia_levanta_value_error() -> None:
    """Garante que uma URL vazia é rejeitada na criação da entidade."""
    with pytest.raises(ValueError, match="URL válida"):
        Favorito(titulo="Sem link", url="")


def test_url_somente_espacos_levanta_value_error() -> None:
    """Garante que uma URL só com espaços em branco também é rejeitada."""
    with pytest.raises(ValueError, match="URL válida"):
        Favorito(titulo="Sem link", url="   ")


def test_entidade_e_imutavel() -> None:
    """Garante que a entidade é frozen e não permite reatribuição de campos."""
    favorito = Favorito(titulo="GitHub", url="https://github.com")

    with pytest.raises(dataclasses.FrozenInstanceError):
        favorito.titulo = "Outro título"  # type: ignore[misc]


def test_to_dict_com_todos_os_campos_preenchidos() -> None:
    """Garante o mapeamento correto de campos para as chaves esperadas no dict."""
    favorito = Favorito(
        titulo="GitHub",
        url="https://github.com",
        pasta="Trabalho / Dev",
        data_adicao="2026-01-15",
    )

    assert favorito.to_dict() == {
        "Titulo": "GitHub",
        "URL": "https://github.com",
        "Pasta": "Trabalho / Dev",
        "Data_Adicao": "2026-01-15",
    }


def test_to_dict_aplica_fallback_para_titulo_vazio() -> None:
    """Garante que um título vazio vira 'Sem título' na serialização."""
    favorito = Favorito(titulo="", url="https://github.com")

    assert favorito.to_dict()["Titulo"] == "Sem título"


def test_to_dict_aplica_fallback_para_pasta_vazia() -> None:
    """Garante que uma pasta explicitamente vazia vira 'Favoritos' na serialização."""
    favorito = Favorito(titulo="GitHub", url="https://github.com", pasta="")

    assert favorito.to_dict()["Pasta"] == "Favoritos"


def test_to_dict_aplica_fallback_para_data_adicao_vazia() -> None:
    """Garante que uma data explicitamente vazia vira 'Sem data' na serialização."""
    favorito = Favorito(titulo="GitHub", url="https://github.com", data_adicao="")

    assert favorito.to_dict()["Data_Adicao"] == "Sem data"
