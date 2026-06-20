# Atoms/backend/core/entidades/entidade_bookmark.py


"""Entidade que representa um favorito extraído de um arquivo HTML."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger: logging.Logger = logging.getLogger(name=__name__)

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
        # Resolução dos parâmetros alternativos
        titulo_final: str | None = titulo if titulo is not None else title
        data_final: datetime | None = (
            data_adicao if data_adicao is not None else add_date
        )

        # Logs sobre uso de aliases (nível INFO, pois indica chamada com API antiga)
        if titulo is None and title is not None:
            logger.info("Usando parâmetro 'title' em vez de 'titulo': %r", title)
        if data_adicao is None and add_date is not None:
            logger.info(
                "Usando parâmetro 'add_date' em vez de 'data_adicao': %s",
                add_date.isoformat(),
            )

        # Aplica valores finais (com fallback)
        object.__setattr__(self, "titulo", titulo_final or "")
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "data_adicao", data_final or DATA_PADRAO)

        # Log após definição dos atributos (DEBUG)
        logger.debug(
            "Favorito criado: título=%r, url=%r, data=%s",
            self.titulo,
            self.url,
            self.data_adicao.isoformat(),
        )

        # Avisos sobre valores ausentes ou substituídos
        if not self.titulo.strip():
            logger.warning("Favorito com título vazio. URL: %r", self.url)

        if data_final is None:
            logger.info(
                "Data de adição não fornecida, usando data padrão (1970-01-01). URL: %r",
                self.url,
            )
        elif data_final.tzinfo is None:
            logger.debug("Data sem informação de fuso horário: %s", data_final)

    @property
    def title(self) -> str:
        """Alias de compatibilidade para `titulo`."""
        return self.titulo

    @property
    def add_date(self) -> datetime:
        """Alias de compatibilidade para `data_adicao`."""
        return self.data_adicao
