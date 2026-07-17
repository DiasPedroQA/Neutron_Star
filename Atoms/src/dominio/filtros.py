"""Predicados de domínio para filtragem de caminhos de arquivos.

Define funções que avaliam características de nomes e caminhos, como
visibilidade, presença de palavras-chave e padrões de data, para apoio à lógica de busca.
"""

import re
from collections.abc import Callable
from pathlib import Path

FiltroCaminho = Callable[[Path], bool]


def caminho_nao_oculto(caminho: Path) -> bool:
    """True se nenhuma parte do caminho começa com '.'."""
    return not any(parte.startswith(".") for parte in caminho.parts)


def contem_chaves_obrigatorias(caminho: Path, chaves: list[str]) -> bool:
    """True se o nome contém ao menos uma das chaves (case-insensitive)."""
    if not chaves:
        return True
    nome: str = caminho.name.lower()
    return any(chave.lower() in nome for chave in chaves)


_PADRAO_DATA_US = r"(?<![^_])(0?[1-9]|1[0-2])_(0?[1-9]|[12]\d|3[01])_(\d{2})(?![^_.])"
_PADRAO_DATA_BR = r"(?<![^_])(0?[1-9]|[12]\d|3[01])_(0?[1-9]|1[0-2])_(\d{2})(?![^_.])"


def contem_data_automatico(caminho: Path) -> bool:
    """True se o nome contém data US (mês_dia_ano) ou BR (dia_mês_ano), ano com 2 dígitos."""
    nome: str = caminho.name
    return bool(re.search(_PADRAO_DATA_US, nome) or re.search(_PADRAO_DATA_BR, nome))
