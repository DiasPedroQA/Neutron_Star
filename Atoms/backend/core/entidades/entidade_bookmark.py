# core/entidades/entidade_bookmark.py

"""Entidade que representa um bookmark extraído de um arquivo HTML."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Bookmark:
    """Um favorito com título, URL e data de adição."""

    title: str
    url: str
    add_date: datetime = field(default_factory=lambda: datetime(year=1970, month=1, day=1, tzinfo=timezone.utc))
