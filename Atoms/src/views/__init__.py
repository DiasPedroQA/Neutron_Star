"""
Pacote views do Neutron Star.

Responsável pela apresentação dos resultados no terminal.
"""

from .apresentador import Apresentador, exibir_resultado

__all__: list[str] = ["Apresentador", "exibir_resultado"]
