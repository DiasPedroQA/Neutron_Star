"""Entidade de domínio que representa um arquivo encontrado na varredura."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
        self.__post_init__()

    def __post_init__(self) -> None:
        if not isinstance(self.nome_arquivo, str) or not self.nome_arquivo.strip():
            raise ValueError("nome_arquivo deve ser uma string não vazia.")
        if not isinstance(self.caminho_arquivo, Path):
            raise TypeError("caminho_arquivo deve ser um Path.")
        if not isinstance(self.tamanho_arquivo_bytes, int):
            raise TypeError("tamanho_arquivo_bytes deve ser int.")
        if not isinstance(self.eh_html, bool):
            raise TypeError("eh_html deve ser bool.")

        if "/" in self.nome_arquivo or "\\" in self.nome_arquivo:
            raise ValueError(f"nome_arquivo não pode conter barras: {self.nome_arquivo}")

        if self.nome_arquivo != self.caminho_arquivo.name:
            raise ValueError("nome_arquivo deve ser igual ao nome final do caminho informado.")

        if not self.caminho_arquivo.is_absolute():
            raise ValueError(f"Caminho deve ser absoluto: {self.caminho_arquivo}")

        if self.tamanho_arquivo_bytes < 0:
            raise ValueError("tamanho_arquivo_bytes não pode ser negativo.")

        if not self.eh_html and self.caminho_arquivo.suffix.lower() in (".html", ".htm"):
            self.eh_html = True

    @property
    def file_is_html(self) -> bool:
        """Alias de compatibilidade para `eh_html`."""
        return self.eh_html

    @file_is_html.setter
    def file_is_html(self, valor: bool) -> None:
        self.eh_html = valor
