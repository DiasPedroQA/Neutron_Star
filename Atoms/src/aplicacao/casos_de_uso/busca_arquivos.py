"""Caso de uso de busca e filtragem de arquivos HTML de bookmarks.

Percorre diretórios de forma recursiva aplicando filtros de domínio
para encontrar apenas arquivos cujo nome segue critérios configuráveis.
"""

from collections.abc import Callable
from pathlib import Path

from dominio.filtros import (
    caminho_nao_oculto,
    no_nome_contem_chave,
    no_nome_contem_data,
)

FiltroCaminho = Callable[[Path], bool]


def aplicar_filtros(arquivos: list[Path], filtros: list[FiltroCaminho]) -> list[Path]:
    """Aplica uma sequência de filtros. Retorna apenas os que passam em todos."""
    resultado: list[Path] = arquivos
    for filtro in filtros:
        resultado = [arquivo for arquivo in resultado if filtro(arquivo)]
    return resultado


def _montar_filtros(chaves: list[str], exigir_data: bool) -> list[FiltroCaminho]:
    """Monta a lista de filtros a aplicar em uma busca de arquivos.

    Quando chaves está vazia, nenhum filtro de palavra-chave é adicionado:
    lista vazia significa "sem restrição por chave", nunca "não corresponde a nada".
    """
    filtros: list[FiltroCaminho] = []
    if chaves:
        filtros.append(lambda arquivo: no_nome_contem_chave(caminho=arquivo, chaves=chaves))
    if exigir_data:
        filtros.append(no_nome_contem_data)
    return filtros


def buscar_arquivos(
    pasta: Path,
    extensao: str,
    chaves: list[str],
    exigir_data: bool = False,
) -> list[Path]:
    """Coleta e filtra arquivos recursivamente."""
    arquivos: list[Path] = [
        arquivo for arquivo in pasta.rglob(f"*{extensao}") if arquivo.is_file() and caminho_nao_oculto(caminho=arquivo)
    ]
    filtros: list[FiltroCaminho] = _montar_filtros(chaves=chaves, exigir_data=exigir_data)
    return aplicar_filtros(arquivos=arquivos, filtros=filtros)
