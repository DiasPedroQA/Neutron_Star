"""Conversões de tempo usadas no domínio de bookmarks.

O formato Netscape Bookmark File grava datas como timestamp Unix (segundos
desde a época). Esta função converte esse valor bruto em um datetime utilizável
pelos adaptadores de exportação, sem forçar o restante do domínio a manipular
`datetime` (TagA mantém a data como string crua, fiel ao arquivo original).
"""

from __future__ import annotations

from datetime import datetime, timezone


def converter_timestamp_unix(valor: str | None) -> datetime | None:
    """Converte um timestamp Unix em segundos (como string) para datetime.

    Args:
        valor: Timestamp Unix como string (ex.: "1700000000"), string vazia ou None.

    Returns:
        datetime | None: O datetime correspondente, ou None se `valor` for
        None, vazio, ou não representar um timestamp válido.
    """
    if not valor:
        return None
    try:
        # Use timezone-aware UTC datetime to avoid local timezone offsets
        # and to satisfy the deprecation guidance for utcfromtimestamp.
        return datetime.fromtimestamp(timestamp=int(valor), tz=timezone.utc)
    except (ValueError, TypeError, OSError):
        return None
