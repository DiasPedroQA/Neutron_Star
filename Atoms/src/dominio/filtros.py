"""Predicados de domínio para filtragem de caminhos de arquivos.

Define funções que avaliam características de nomes e caminhos, como
visibilidade, presença de palavras-chave e padrões de data, para apoio à lógica de busca.
"""

import re
from pathlib import Path

_PADRAO_DATA_US = r"(?<![^_])(0?[1-9]|1[0-2])_(0?[1-9]|[12]\d|3[01])_(\d{2})(?![^_.])"
_PADRAO_DATA_BR = r"(?<![^_])(0?[1-9]|[12]\d|3[01])_(0?[1-9]|1[0-2])_(\d{2})(?![^_.])"


def extrair_nome_do_caminho(caminho: Path) -> str:
    """Extrai apenas o nome do arquivo de seu caminho original."""
    return caminho.name.lower()


def caminho_nao_oculto(caminho: Path) -> bool:
    """True se nenhuma parte do caminho começa com '.'."""
    return not any(parte.startswith(".") for parte in caminho.parts)


def no_nome_contem_chave(caminho: Path, chaves: list[str]) -> bool:
    """True se o nome contém ao menos uma das chaves (case-insensitive)."""
    nome_arquivo: str = extrair_nome_do_caminho(caminho=caminho)
    return any(chave.lower() in nome_arquivo for chave in chaves)


def no_nome_contem_data(caminho: Path) -> bool:
    """True se o nome contém data US (mês_dia_ano) ou BR (dia_mês_ano), ano com 2 dígitos."""
    nome_arquivo: str = extrair_nome_do_caminho(caminho=caminho)
    return bool(re.search(_PADRAO_DATA_US, nome_arquivo) or re.search(_PADRAO_DATA_BR, nome_arquivo))
