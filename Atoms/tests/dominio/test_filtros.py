"""Testes de unidade para os filtros de caminhos e nomes de arquivos de bookmarks no domínio.

Verifica o comportamento de filtrar_por_caminhos_ocultos e filtrar_pelo_nome
em cenários de caminhos visíveis, ocultos e nomes válidos ou inválidos para bookmarks.
"""

from __future__ import annotations

from pathlib import Path

from src.dominio.filtros import (
    filtrar_pelo_nome,
    filtrar_por_caminhos_ocultos,
)


def test_filtrar_por_caminhos_ocultos_visivel() -> None:
    """Garante que caminhos de arquivos em pastas não ocultas são aceitos.

    Usa um caminho comum de usuário para validar que o filtro retorna True
    para diretórios visíveis.
    """
    assert filtrar_por_caminhos_ocultos(caminho=Path("/home/user/bookmarks.html"))


def test_filtrar_por_caminhos_ocultos_oculto() -> None:
    """Verifica que caminhos em pastas ocultas são rejeitados pelo filtro.

    Usa um diretório com nome iniciado por ponto para confirmar que o filtro
    retorna False para esse caso.
    """
    assert not filtrar_por_caminhos_ocultos(caminho=Path("/home/.git/bookmarks.html"))


def test_filtrar_pelo_nome_valido() -> None:
    """Confere que nomes típicos de bookmarks são aceitos pelo filtro de nome.

    Testa diferentes variantes de nomes relacionados a bookmarks e favoritos
    para garantir que retornam True.
    """
    assert filtrar_pelo_nome(caminho=Path("bookmarks_2025.html"))
    assert filtrar_pelo_nome(caminho=Path("favoritos.html"))
    assert filtrar_pelo_nome(caminho=Path("my_favorites.html"))


def test_filtrar_pelo_nome_invalido() -> None:
    """Valida que nomes genéricos de arquivos são rejeitados pelo filtro de nome.

    Usa exemplos como 'index.html' e 'readme.txt' para garantir que o filtro
    retorna False nesses casos.
    """
    assert not filtrar_pelo_nome(caminho=Path("index.html"))
    assert not filtrar_pelo_nome(caminho=Path("readme.txt"))
