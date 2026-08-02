"""Predicados puros para decidir se um caminho é um candidato a bookmark."""

from __future__ import annotations

import re
from pathlib import Path

PADROES_NOME: re.Pattern[str] = re.compile(
    pattern=r"bookmark?|favorito?|favorite?",
    flags=re.IGNORECASE,
)


def filtrar_por_caminhos_ocultos(caminho: Path) -> bool:
    """Exclui caminhos que contenham partes iniciadas por '.' (ocultos)."""
    return not any(part.startswith(".") for part in caminho.parts)


def filtrar_pelo_nome(caminho: Path) -> bool:
    """Verifica se o nome do arquivo contém palavras-chave de bookmarks."""
    return bool(PADROES_NOME.search(caminho.name))
