"""Implementação concreta do analisador de favoritos no formato Netscape."""

from __future__ import annotations

import contextlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup, Tag

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.interfaces.bookmark_parser import FavoritoParser

logger: logging.Logger = logging.getLogger(name=__name__)


class TagsFinder(FavoritoParser):
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
            logger.warning(msg=f"Arquivo não encontrado: {caminho}")
            return favoritos

        try:
            conteudo_html: str = caminho.read_text(encoding="utf-8", errors="replace")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception(msg=f"Erro ao ler o caminho: {caminho}")
            return favoritos

        sopa = BeautifulSoup(markup=conteudo_html, features="lxml")

        for tag_link in sopa.find_all(name="a"):
            if favorito := self._analisar_tag_favorito(html_tag=tag_link):
                favoritos.append(favorito)

        logger.info(msg=f"Extraídos {len(favoritos)} favoritos de {caminho}")
        return favoritos

    def _analisar_tag_favorito(self, html_tag: Tag) -> Favorito | None:
        """Tenta extrair os dados de um único <a>."""
        href_tag: str | list[str] | None = html_tag.get("href")
        if not isinstance(href_tag, str) or not self._is_favorito_url(tag_url=href_tag):
            return None

        titulo_tag: str = html_tag.get_text(strip=True)
        texto_data_adicao: str = str(html_tag.get("add_date", "")).strip()
        data_adicao_tag: datetime = self._converter_timestamp(
            texto_timestamp=texto_data_adicao
        )

        return Favorito(titulo=titulo_tag, url=href_tag, data_adicao=data_adicao_tag)

    @staticmethod
    def _is_favorito_url(tag_url: str) -> bool:
        """Valida se a URL do favorito é segura ou estável localmente."""
        parsed: ParseResult = urlparse(url=tag_url)
        scheme: str = parsed.scheme.lower()
        if scheme == "https":
            return True
        if scheme == "http":
            hostname: str = parsed.hostname or ""
            return hostname in {"localhost", "127.0.0.1", "::1"}
        return False

    @staticmethod
    def _converter_timestamp(texto_timestamp: str) -> datetime:
        """Converte string numérica para datetime UTC, ou retorna epoch."""
        if texto_timestamp.isdigit():
            with contextlib.suppress(ValueError, OSError):
                return datetime.fromtimestamp(
                    timestamp=int(texto_timestamp), tz=timezone.utc
                )
        return datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)

    def _parse_bookmark_tag(self, tag: Tag) -> Favorito | None:
        """Alias de compatibilidade para `_analisar_tag_favorito`."""
        return self._analisar_tag_favorito(html_tag=tag)

    @staticmethod
    def _convert_timestamp(timestamp_str: str) -> datetime:
        """Alias de compatibilidade para `_converter_timestamp`."""
        return TagsFinder._converter_timestamp(texto_timestamp=timestamp_str)


AnalisadorTags = TagsFinder
