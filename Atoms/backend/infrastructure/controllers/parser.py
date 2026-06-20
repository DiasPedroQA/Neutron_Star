# Atoms/backend/infrastructure/controllers/parser.py

"""Implementação concreta do analisador de favoritos no formato Netscape."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup, Tag

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.interfaces.bookmark_parser import FavoritoParser

logger: logging.Logger = logging.getLogger(name=__name__)


class AnalisadorTags(FavoritoParser):
    """Extrai todos os links de um arquivo de favoritos (formato Netscape)."""

    def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
        """Verifica se o analisador consegue processar o arquivo."""
        suportado: bool = arquivo.eh_html or arquivo.caminho_arquivo.suffix.lower() in (
            ".html",
            ".htm",
        )
        logger.debug(
            "Verificando suporte para %s: %s",
            arquivo.caminho_arquivo,
            suportado,
        )
        return suportado

    def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Favorito]:
        """Extrai título, URL e data (convertida) de cada favorito."""
        favoritos: list[Favorito] = []
        caminho = Path(arquivo.caminho_arquivo)

        logger.info("Iniciando análise do arquivo: %s", caminho)

        if not caminho.is_file():
            logger.warning("Arquivo não encontrado ou não é um arquivo: %s", caminho)
            return favoritos

        try:
            conteudo_html: str = caminho.read_text(encoding="utf-8", errors="replace")
            logger.debug(
                "Arquivo lido: %s (%d caracteres)", caminho, len(conteudo_html)
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Erro ao ler o arquivo: %s", caminho)
            return favoritos

        sopa = BeautifulSoup(markup=conteudo_html, features="lxml")
        tags_encontradas = sopa.find_all(name="a")
        logger.debug("Encontradas %d tags <a> em %s", len(tags_encontradas), caminho)

        for tag_link in tags_encontradas:
            if favorito := self._analisar_tag_favorito(html_tag=tag_link):
                favoritos.append(favorito)
                logger.debug("Favorito adicionado: %s", favorito.url)
            else:
                logger.debug("Tag ignorada (não gerou favorito válido)")

        logger.info("Extraídos %d favoritos de %s", len(favoritos), caminho)
        return favoritos

    def _analisar_tag_favorito(self, html_tag: Tag) -> Favorito | None:
        """Tenta extrair os dados de um único <a>."""
        href_tag: str | list[str] | None = html_tag.get("href")
        if not isinstance(href_tag, str):
            logger.debug("Tag sem href string: %s", html_tag)
            return None
        if not self._is_favorito_url(tag_url=href_tag):
            logger.debug("URL inválida para favorito: %s", href_tag)
            return None

        titulo_tag: str = html_tag.get_text(strip=True)
        texto_data_adicao: str = str(html_tag.get("add_date", "")).strip()
        data_adicao_tag: datetime = self._converter_timestamp(
            texto_timestamp=texto_data_adicao
        )

        logger.debug(
            "Favorito extraído: título=%r, url=%s, data=%s",
            titulo_tag,
            href_tag,
            data_adicao_tag.isoformat(),
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
            valido: bool = hostname in {"localhost", "127.0.0.1", "::1"}
            if not valido:
                logger.debug("URL HTTP não é localhost: %s", tag_url)
            return valido
        logger.debug("Esquema não suportado: %s em %s", scheme, tag_url)
        return False

    @staticmethod
    def _converter_timestamp(texto_timestamp: str) -> datetime:
        """Converte string numérica para datetime UTC, ou retorna epoch."""
        if texto_timestamp.isdigit():
            try:
                dt: datetime = datetime.fromtimestamp(
                    timestamp=int(texto_timestamp), tz=timezone.utc
                )
                logger.debug(
                    "Timestamp convertido: %s -> %s", texto_timestamp, dt.isoformat()
                )
                return dt
            except (ValueError, OSError):
                logger.debug("Falha ao converter timestamp: %s", texto_timestamp)
        else:
            logger.debug("Timestamp não numérico: %s", texto_timestamp)
        return datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)

    def _parse_bookmark_tag(self, tag: Tag) -> Favorito | None:
        """Alias de compatibilidade para `_analisar_tag_favorito`."""
        logger.debug("Usando alias '_parse_bookmark_tag'")
        return self._analisar_tag_favorito(html_tag=tag)

    @staticmethod
    def _convert_timestamp(timestamp_str: str) -> datetime:
        """Alias de compatibilidade para `_converter_timestamp`."""
        logger.debug("Usando alias '_convert_timestamp'")
        return AnalisadorTags._converter_timestamp(texto_timestamp=timestamp_str)
