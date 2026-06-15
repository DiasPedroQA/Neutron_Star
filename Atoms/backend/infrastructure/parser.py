"""Implementação concreta do analisador de favoritos no formato Netscape."""

from __future__ import annotations

import contextlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Favorito
from Atoms.backend.core.interfaces.bookmark_parser import BookmarkParser

logger: logging.Logger = logging.getLogger(name=__name__)


class TagsFinder(BookmarkParser):
    """Extrai todos os links de um arquivo de favoritos (formato Netscape)."""

    def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
        """Verifica se o analisador consegue processar o arquivo."""
        return arquivo.eh_html or arquivo.caminho_arquivo.suffix.lower() in (
            ".html",
            ".htm",
        )

    def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Favorito]:
        """Extrai título, URL e data (convertida) de cada favorito."""
        favoritos: list[Favorito] = []
        caminho = Path(arquivo.caminho_arquivo)

        if not caminho.is_file():
            logger.warning("Arquivo não encontrado: %s", caminho)
            return favoritos

        try:
            conteudo_html: str = caminho.read_text(encoding="utf-8", errors="replace")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Erro ao ler %s", caminho)
            return favoritos

        sopa = BeautifulSoup(markup=conteudo_html, features="lxml")

        for tag_link in sopa.find_all(name="a"):
            if favorito := self._analisar_tag_favorito(tag=tag_link):
                favoritos.append(favorito)

        logger.info("Extraídos %d favoritos de %s", len(favoritos), caminho)
        return favoritos

    def _analisar_tag_favorito(self, tag: Tag) -> Favorito | None:
        """Tenta extrair os dados de um único <a>."""
        href: str | list[str] | None = tag.get("href")
        if not isinstance(href, str) or not self._is_favorito_url(href):
            return None

        titulo: str = tag.get_text(strip=True)
        texto_data_adicao: str = str(tag.get("add_date", "")).strip()
        data_adicao: datetime = self._converter_timestamp(
            texto_timestamp=texto_data_adicao
        )

        return Favorito(titulo=titulo, url=href, data_adicao=data_adicao)

    @staticmethod
    def _is_favorito_url(url: str) -> bool:
        """Valida se a URL do favorito é segura ou estável localmente."""
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        if scheme == "https":
            return True
        if scheme == "http":
            hostname = parsed.hostname or ""
            return hostname in ("localhost", "127.0.0.1", "::1")
        return False

    @staticmethod
    def _converter_timestamp(texto_timestamp: str) -> datetime:
        """Converte string numérica para datetime UTC, ou retorna epoch."""
        if texto_timestamp.isdigit():
            with contextlib.suppress(ValueError, OSError):
                return datetime.fromtimestamp(int(texto_timestamp), tz=timezone.utc)
        return datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)

    def _parse_bookmark_tag(self, tag: Tag) -> Favorito | None:
        """Alias de compatibilidade para `_analisar_tag_favorito`."""
        return self._analisar_tag_favorito(tag=tag)

    @staticmethod
    def _convert_timestamp(timestamp_str: str) -> datetime:
        """Alias de compatibilidade para `_converter_timestamp`."""
        return TagsFinder._converter_timestamp(texto_timestamp=timestamp_str)


AnalisadorTags = TagsFinder
