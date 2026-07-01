"""Pacote de controladores da aplicação.

Contém o buscador de sistema de arquivos e o identificador de sistema operacional,
que atuam como orquestradores entre os modelos e as ferramentas de baixo nível.
"""

from .buscador import BuscadorSistemaArquivos, CriteriosBusca, FiltroTexto
from .identificador import IdentificadorSistema, InfoSistema

__all__: list[str] = [
    "BuscadorSistemaArquivos",
    "CriteriosBusca",
    "FiltroTexto",
    "IdentificadorSistema",
    "InfoSistema",
]
