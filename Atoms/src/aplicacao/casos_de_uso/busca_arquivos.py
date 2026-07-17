"""Caso de uso de busca e filtragem de arquivos HTML de bookmarks.

Percorre diretórios de forma recursiva aplicando filtros de domínio
para encontrar apenas arquivos cujo nome segue critérios configuráveis.
"""

from pathlib import Path

from dominio.filtros import (
    FiltroCaminho,
    caminho_nao_oculto,
    contem_chaves_obrigatorias,
    contem_data_automatico,
)


def aplicar_pipeline(arquivos: list[Path], filtros: list[FiltroCaminho]) -> list[Path]:
    """Aplica uma sequência de filtros. Retorna apenas os que passam em todos."""
    resultado: list[Path] = arquivos
    for filtro in filtros:
        resultado = [p for p in resultado if filtro(p)]
    return resultado


def normalizar_extensao(extensao: str) -> str:
    """Garante que a extensão comece com '.'."""
    return extensao if extensao.startswith(".") else f".{extensao}"


def _montar_filtros(chaves: list[str], exigir_data: bool) -> list[FiltroCaminho]:
    """Monta a lista de filtros a aplicar em uma busca de arquivos."""
    filtros: list[FiltroCaminho] = [lambda p: contem_chaves_obrigatorias(caminho=p, chaves=chaves)]
    if exigir_data:
        filtros.append(contem_data_automatico)
    return filtros


def buscar_arquivos(
    pasta: Path,
    extensao: str,
    chaves: list[str],
    exigir_data: bool = False,
) -> list[Path]:
    """Coleta e filtra arquivos recursivamente."""
    ext: str = normalizar_extensao(extensao=extensao)
    arquivos: list[Path] = [p for p in pasta.rglob(f"*{ext}") if p.is_file() and caminho_nao_oculto(caminho=p)]
    filtros: list[FiltroCaminho] = _montar_filtros(chaves=chaves, exigir_data=exigir_data)
    return aplicar_pipeline(arquivos=arquivos, filtros=filtros)
