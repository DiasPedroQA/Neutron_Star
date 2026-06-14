# Atoms/backend/infrastructure/parser.py

"""Implementação concreta do parser de bookmarks (formato Netscape)."""

from __future__ import annotations

import contextlib
import logging
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Bookmark
from Atoms.backend.core.interfaces.bookmark_parser import BookmarkParser

logger: logging.Logger = logging.getLogger(name=__name__)


class TagsFinder(BookmarkParser):
    """Extrai todos os links de um arquivo de bookmarks (formato Netscape)."""

    def supports_file(self, arquivo: ModeloArquivo) -> bool:
        """Verifica se o parser consegue processar o arquivo."""
        return arquivo.file_is_html or arquivo.caminho_arquivo.suffix.lower() in (
            ".html",
            ".htm",
        )

    def parse_file(self, arquivo: ModeloArquivo) -> list[Bookmark]:
        """Extrai título, URL e data (convertida) de cada favorito."""
        bookmarks: list[Bookmark] = []
        caminho = Path(arquivo.caminho_arquivo)

        if not caminho.is_file():
            logger.warning("Arquivo não encontrado: %s", caminho)
            return bookmarks

        try:
            html_content: str = caminho.read_text(encoding="utf-8", errors="replace")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Erro ao ler %s", caminho)
            return bookmarks

        soup = BeautifulSoup(markup=html_content, features="lxml")

        for a_tag in soup.find_all(name="a"):
            if bookmark := self._parse_bookmark_tag(tag=a_tag):
                bookmarks.append(bookmark)

        logger.info("Extraídos %d bookmarks de %s", len(bookmarks), caminho)
        return bookmarks

    def _parse_bookmark_tag(self, tag: Tag) -> Bookmark | None:
        """Tenta extrair os dados de um único <a>."""
        href: str | list[str] | None = tag.get("href")
        if not isinstance(href, str) or not href.startswith(("http://", "https://")):
            return None

        title: str = tag.get_text(strip=True)
        add_date_str: str = str(tag.get("add_date", "")).strip()
        add_date: datetime = self._convert_timestamp(timestamp_str=add_date_str)

        return Bookmark(title=title, url=href, add_date=add_date)

    @staticmethod
    def _convert_timestamp(timestamp_str: str) -> datetime:
        """Converte string numérica para datetime UTC, ou retorna epoch."""
        if timestamp_str.isdigit():
            with contextlib.suppress(ValueError, OSError):
                return datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)
        return datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)
