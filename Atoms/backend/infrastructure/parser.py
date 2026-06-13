# backend/parser.py

"""Implementação concreta do parser de bookmarks."""
from __future__ import annotations

from typing import Any, TypedDict

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList

from Atoms.backend.core.entities import ModeloArquivo
from Atoms.backend.core.interfaces import BookmarkParser


class BookmarkDict(TypedDict):
    """Estrutura tipada para um bookmark extraído de HTML."""

    title: str
    url: str
    add_date: str
    source_file: str


class NetscapeBookmarkParser(BookmarkParser):
    """REPOSITORY: extrai bookmarks de HTML no formato Netscape."""

    def parse_file(self, arquivo: ModeloArquivo) -> list[dict[str, Any]]:
        """Extrai título, URL e data de adição do arquivo HTML."""
        bookmarks: list[dict[str, Any]] = []

        try:
            with open(
                file=arquivo.caminho_arquivo,
                mode="r",
                encoding="utf-8",
                errors="ignore",
            ) as f:
                soup = BeautifulSoup(f, features="lxml")

            for a in soup.find_all("a"):
                href: str | AttributeValueList | None = a.get("href")
                if href and isinstance(href, str) and href.startswith("http"):
                    add_date_raw: str | AttributeValueList | None = a.get(
                        key="add_date",
                        default="",
                    )
                    add_date: str = str(add_date_raw) if add_date_raw is not None else ""

                    bookmark: BookmarkDict = {
                        "title": a.get_text(strip=True),
                        "url": href,
                        "add_date": add_date,
                        # info extra
                        "source_file": str(arquivo.caminho_arquivo),
                    }
                    bookmarks.append(dict(bookmark))
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {arquivo.caminho_arquivo}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Erro ao processar {arquivo.caminho_arquivo}: {e}")

        return bookmarks
