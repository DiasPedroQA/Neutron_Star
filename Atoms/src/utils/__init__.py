"""Pacote de ferramentas de baixo nível para interação com o sistema de arquivos.

Fornece funções para listar diretórios, obter metadados de itens e calcular
hashes, encapsulando tratamento de erros e diferenças entre sistemas operacionais.
"""

from .system_tools import (
    _calcular_hash,
    criar_item,
    listar_diretorio,
    obter_info_arquivo,
)

__all__: list[str] = [
    "_calcular_hash",
    "criar_item",
    "listar_diretorio",
    "obter_info_arquivo",
]
