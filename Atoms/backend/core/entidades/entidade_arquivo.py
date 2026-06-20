# Atoms/backend/core/entidades/entidade_arquivo.py

"""Entidade de domínio que representa um arquivo encontrado na varredura."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass(init=False)
class ModeloArquivo:
    """Representa um arquivo do sistema de arquivos."""

    nome_arquivo: str
    caminho_arquivo: Path
    tamanho_arquivo_bytes: int = 0
    eh_html: bool = False

    def __init__(
        self,
        nome_arquivo: str,
        caminho_arquivo: Path,
        tamanho_arquivo_bytes: int = 0,
        eh_html: bool | None = None,
        *,
        file_is_html: bool | None = None,
    ) -> None:
        self.nome_arquivo = nome_arquivo
        self.caminho_arquivo = caminho_arquivo
        self.tamanho_arquivo_bytes = tamanho_arquivo_bytes
        self.eh_html = bool(eh_html if eh_html is not None else file_is_html)

        logger.debug(
            "Criando ModeloArquivo: nome=%r, caminho=%s, tamanho=%d, eh_html=%s",
            self.nome_arquivo,
            self.caminho_arquivo,
            self.tamanho_arquivo_bytes,
            self.eh_html,
        )

        self.__post_init__()

        logger.debug(
            "ModeloArquivo validado e pronto: %s (%d bytes)",
            self.caminho_arquivo,
            self.tamanho_arquivo_bytes,
        )

    def __post_init__(self) -> None:
        """Validações pós-inicialização."""
        # Validações estritas
        if not isinstance(self.nome_arquivo, str) or not self.nome_arquivo.strip():
            logger.error("nome_arquivo inválido: %r", self.nome_arquivo)
            raise ValueError("nome_arquivo deve ser uma string não vazia.")
        if not isinstance(self.caminho_arquivo, Path):
            logger.error("caminho_arquivo não é Path: %r", self.caminho_arquivo)
            raise TypeError("caminho_arquivo deve ser um Path.")
        if not isinstance(self.tamanho_arquivo_bytes, int):
            logger.error(
                "tamanho_arquivo_bytes não é int: %r", self.tamanho_arquivo_bytes
            )
            raise TypeError("tamanho_arquivo_bytes deve ser int.")
        if not isinstance(self.eh_html, bool):
            logger.error("eh_html não é bool: %r", self.eh_html)
            raise TypeError("eh_html deve ser bool.")

        if "/" in self.nome_arquivo or "\\" in self.nome_arquivo:
            logger.warning(
                "nome_arquivo contém barra: %r (caminho: %s)",
                self.nome_arquivo,
                self.caminho_arquivo,
            )
            raise ValueError(
                f"nome_arquivo não pode conter barras: {self.nome_arquivo}"
            )

        if self.nome_arquivo != self.caminho_arquivo.name:
            logger.warning(
                "nome_arquivo divergente do nome no caminho: '%s' vs '%s'",
                self.nome_arquivo,
                self.caminho_arquivo.name,
            )
            raise ValueError(
                "nome_arquivo deve ser igual ao nome final do caminho informado."
            )

        if not self.caminho_arquivo.is_absolute():
            logger.error("Caminho não absoluto: %s", self.caminho_arquivo)
            raise ValueError(f"Caminho deve ser absoluto: {self.caminho_arquivo}")

        if self.tamanho_arquivo_bytes < 0:
            logger.error(
                "Tamanho negativo: %d bytes em %s",
                self.tamanho_arquivo_bytes,
                self.caminho_arquivo,
            )
            raise ValueError("tamanho_arquivo_bytes não pode ser negativo.")

        # Correção automática: se extensão for HTML/HTM, força eh_html
        if not self.eh_html and self.caminho_arquivo.suffix.lower() in {
            ".html",
            ".htm",
        }:
            logger.info(
                "Arquivo com extensão HTML/HTM detectado, mas eh_html era False. "
                "Forçando eh_html=True: %s",
                self.caminho_arquivo,
            )
            self.eh_html = True

    @property
    def file_is_html(self) -> bool:
        """Alias de compatibilidade para `eh_html`."""
        return self.eh_html

    @file_is_html.setter
    def file_is_html(self, valor: bool) -> None:
        self.eh_html = valor
