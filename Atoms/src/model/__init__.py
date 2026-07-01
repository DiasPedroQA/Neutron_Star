"""Modelos de dados do Neutron Star.

Define as entidades que representam itens do sistema de arquivos,
resultados de busca e configurações da aplicação.
"""

from .arquivo_info import ItemArquivo
from .configuracoes import ConfigApp
from .diretorio_info import ItemDiretorio
from .item_neutro import ItemBase
from .resultado_busca import ResultadoBusca

__all__: list[str] = [
    "ItemBase",
    "ItemArquivo",
    "ItemDiretorio",
    "ResultadoBusca",
    "ConfigApp",
]
