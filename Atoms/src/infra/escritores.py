# Atoms/infra/escritores.py
# pylint: disable=too-few-public-methods

"""Implementações de conversão para diferentes formatos."""

from collections.abc import Sequence

from aplicacao.portas import Conversor
from dominio.entidades import TagExtraida


class ConversorMarkdown(Conversor):
    """Converte arquivos html para formatação Markdown."""

    def converter(self, arquivos_html: Sequence[TagExtraida]) -> str:
        """Gera uma lista em Markdown."""
        linhas: list[str] = ["# TagExtraidas\n"]
        for bm in arquivos_html:
            linhas.append(f"- [{bm.titulo}]({bm.url})")
        return "\n".join(linhas)
