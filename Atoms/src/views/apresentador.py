"""
Módulo de apresentação de resultados do Neutron Star.

Exibe um ``ResultadoBusca`` no terminal de forma clara e estruturada,
usando ``rich`` se disponível, com fallback para texto puro.
"""

from __future__ import annotations

from typing import Final

# __________________________________________________________________________-
# Constantes de apresentação
# __________________________________________________________________________-
_MAX_ITENS_PADRAO: Final[int] = 100
_LARGURA_SEPARADOR: Final[int] = 70
_SIMBOLO_ARQUIVO: Final[str] = "📄"
_SIMBOLO_PASTA: Final[str] = "📁"
_AVISO_TRUNCADO: Final[str] = "… (lista truncada — use filtros para refinar)"
_TITULO_BUSCA: Final[str] = "🔭 Neutron Star — Resultado da Busca"
