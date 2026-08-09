# Atoms/infra/escritores.py
# pylint: disable=too-few-public-methods

"""Implementações de conversão para diferentes formatos."""

from typing import Sequence

from src.aplicacao.portas import Conversor
from dominio.entidades import Bookmark


class ConversorMarkdown(Conversor):
    """Converte bookmarks para formatação Markdown."""

    def converter(self, bookmarks: Sequence[Bookmark]) -> str:
        """Gera uma lista em Markdown."""
        linhas: list[str] = ["# Bookmarks\n"]
        for bm in bookmarks:
            linhas.append(f"- [{bm.titulo}]({bm.url})")
        return "\n".join(linhas)
