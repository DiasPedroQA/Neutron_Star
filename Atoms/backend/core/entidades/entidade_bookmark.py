"""Entidade que representa um favorito extraído de um arquivo HTML."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

DATA_PADRAO = datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)


@dataclass(frozen=True, init=False)
class Favorito:
    """Representa um favorito com título, URL e data de adição.

    Os parâmetros em inglês são aceitos apenas por compatibilidade com a API
    anterior. No código novo, prefira `titulo` e `data_adicao`.
    """

    titulo: str
    url: str
    data_adicao: datetime

    def __init__(
        self,
        titulo: str | None = None,
        url: str = "",
        data_adicao: datetime | None = None,
        *,
        title: str | None = None,
        add_date: datetime | None = None,
    ) -> None:
        titulo_final: str | None = titulo if titulo is not None else title
        data_final: datetime | None = (
            data_adicao if data_adicao is not None else add_date
        )

        object.__setattr__(self, "titulo", titulo_final or "")
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "data_adicao", data_final or DATA_PADRAO)

    @property
    def title(self) -> str:
        """Alias de compatibilidade para `titulo`."""
        return self.titulo

    @property
    def add_date(self) -> datetime:
        """Alias de compatibilidade para `data_adicao`."""
        return self.data_adicao


Bookmark = Favorito
