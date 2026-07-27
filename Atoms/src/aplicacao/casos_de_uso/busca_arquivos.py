"""Caso de uso de busca e filtragem de arquivos HTML de bookmarks.

Percorre diretórios de forma recursiva aplicando filtros de domínio
para encontrar apenas arquivos cujo nome segue critérios configuráveis.
"""

from collections.abc import Callable
from pathlib import Path

from dominio.filtros import (
    caminho_nao_oculto,
    no_nome_contem_chave,
)

FiltroCaminho = Callable[[Path], bool]


def aplicar_filtros(arquivos: list[Path], filtros: list[FiltroCaminho]) -> list[Path]:
    """Aplica uma sequência de filtros. Retorna apenas os que passam em todos."""
    resultado: list[Path] = arquivos
    for filtro in filtros:
        resultado = [arquivo for arquivo in resultado if filtro(arquivo)]
    return resultado


def _montar_filtros() -> list[FiltroCaminho]:
    """Monta a lista de filtros a aplicar em uma busca de arquivos."""
    return [lambda arquivo: no_nome_contem_chave(caminho=arquivo)]


def buscar_arquivos(
    pasta: Path,
) -> list[Path]:
    """Coleta e filtra arquivos recursivamente."""
    extensao: str = ".html"
    arquivos: list[Path] = [
        arquivo
        for arquivo in pasta.rglob(pattern=f"*{extensao}")
        if arquivo.is_file() and caminho_nao_oculto(caminho=arquivo)
    ]
    filtros: list[FiltroCaminho] = _montar_filtros()
    return aplicar_filtros(arquivos=arquivos, filtros=filtros)
