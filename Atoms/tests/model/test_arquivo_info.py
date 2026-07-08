"""Testes para o modelo concreto Arquivo (e Permissoes).

Verifica a criação, as properties de conveniência e a imutabilidade
do dataclass usado pelo Buscador para representar resultados.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from src.models.arquivo import Arquivo, Permissoes


class TestArquivo:
    """Suite de testes para a classe Arquivo."""

    def test_criacao_completa(self) -> None:
        """Verifica a instanciação com todos os atributos preenchidos."""
        modificado = datetime(year=2025, month=1, day=1, hour=12, minute=0, second=0)
        permissoes = Permissoes(legivel=True, gravavel=False, executavel=True)

        arquivo = Arquivo(
            caminho=Path("/tmp/bar.txt"),
            tamanho=1024,
            modificado=modificado,
            permissoes=permissoes,
            oculto=True,
            tipo_mime="text/plain",
            hash_checksum="abc123",
        )

        assert arquivo.caminho == Path("/tmp/bar.txt")
        assert arquivo.modificado == modificado
        assert arquivo.tamanho == 1024
        assert arquivo.oculto is True
        assert arquivo.tipo_mime == "text/plain"
        assert arquivo.hash_checksum == "abc123"

    def test_properties_de_conveniencia_espelham_permissoes(self) -> None:
        """As properties legivel/gravavel/executavel são atalhos para `permissoes`."""
        permissoes = Permissoes(legivel=True, gravavel=False, executavel=True)
        arquivo = Arquivo(
            caminho=Path("/tmp/a.txt"),
            tamanho=100,
            modificado=None,
            permissoes=permissoes,
            oculto=False,
        )

        assert arquivo.legivel is True
        assert arquivo.gravavel is False
        assert arquivo.executavel is True

    def test_nome_retorna_apenas_o_ultimo_componente_do_caminho(self) -> None:
        """`nome` deve ser equivalente a `caminho.name`."""
        arquivo = Arquivo(
            caminho=Path("/tmp/pasta/bookmarks_5_20_26.html"),
            tamanho=10,
            modificado=None,
            permissoes=Permissoes(legivel=True, gravavel=True, executavel=False),
            oculto=False,
        )
        assert arquivo.nome == "bookmarks_5_20_26.html"

    def test_tipo_mime_e_hash_sao_opcionais(self) -> None:
        """Campos opcionais têm None como padrão quando não informados."""
        arquivo = Arquivo(
            caminho=Path("/tmp/data.json"),
            tamanho=2048,
            modificado=None,
            permissoes=Permissoes(legivel=True, gravavel=True, executavel=False),
            oculto=False,
        )
        assert arquivo.tipo_mime is None
        assert arquivo.hash_checksum is None

    def test_imutabilidade(self) -> None:
        """Garante que a classe frozen não permite alteração de atributos."""
        arquivo = Arquivo(
            caminho=Path("/tmp/x.txt"),
            tamanho=0,
            modificado=None,
            permissoes=Permissoes(legivel=True, gravavel=True, executavel=False),
            oculto=False,
        )
        with pytest.raises(expected_exception=AttributeError):
            arquivo.tamanho = 999  # type: ignore[misc]


class TestPermissoes:
    """Suite de testes para a classe Permissoes."""

    def test_criacao_e_imutabilidade(self) -> None:
        """Permissoes também é um dataclass frozen."""
        permissoes = Permissoes(legivel=True, gravavel=True, executavel=False)
        assert permissoes.legivel is True
        assert permissoes.gravavel is True
        assert permissoes.executavel is False
        with pytest.raises(expected_exception=AttributeError):
            permissoes.legivel = False  # type: ignore[misc]
