"""Utilitários puros de conversão de tipo usados ao ler atributos HTML."""

from __future__ import annotations

from typing import Any


def to_int(valor: Any) -> int | None:
    """Converte valor para inteiro, retornando None se falhar."""
    if valor is None:
        return None
    try:
        # Trata casos como "123.0" (float em string)
        if isinstance(valor, str) and "." in valor:
            return int(float(valor))
        return int(valor)
    except (ValueError, TypeError):
        return None


def to_str(valor: Any) -> str | None:
    """Converte valor para string, retornando None se for None."""
    return None if valor is None else str(valor)
