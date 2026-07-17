# pipeline/contexto.py (ou mantenha no próprio main)
"""Tipos auxiliares para o contexto de execução do pipeline de aplicação.

Define um alias de dicionário tipado usado para compartilhar dados entre
as diferentes etapas do processamento de bookmarks.
"""

from typing import Any

Contexto = dict[str, Any]
