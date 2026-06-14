# Atoms/backend/core/entidades/entidade_arquivo.py

"""Modelos de dados principais do domínio: ModeloArquivo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModeloArquivo:
    """Representa um arquivo (ex: bookmark HTML, qualquer arquivo)."""

    nome_arquivo: str
    caminho_arquivo: Path  # caminho absoluto
    tamanho_arquivo_bytes: int = 0
    file_is_html: bool = False  # atalho para saber se é HTML

    def __post_init__(self) -> None:
        # Validações de tipo
        if not isinstance(self.nome_arquivo, str) or not self.nome_arquivo.strip():
            raise ValueError("nome_arquivo deve ser uma string não vazia.")
        if not isinstance(self.caminho_arquivo, Path):
            raise TypeError("caminho_arquivo deve ser um Path.")
        if not isinstance(self.tamanho_arquivo_bytes, int):
            raise TypeError("tamanho_arquivo_bytes deve ser int.")
        if not isinstance(self.file_is_html, bool):
            raise TypeError("file_is_html deve ser bool.")

        # nome_arquivo não deve conter separadores de diretório
        if "/" in self.nome_arquivo or "\\" in self.nome_arquivo:
            raise ValueError(f"nome_arquivo não pode conter barras: {self.nome_arquivo}")

        # O nome do arquivo deve ser consistente com o caminho fornecido
        if self.nome_arquivo != self.caminho_arquivo.name:
            raise ValueError("nome_arquivo deve ser igual ao nome final do caminho informado.")

        # Caminho absoluto obrigatório
        if not self.caminho_arquivo.is_absolute():
            raise ValueError(f"Caminho deve ser absoluto: {self.caminho_arquivo}")

        # O caminho deve apontar para um arquivo (não uma pasta existente)
        # (essa checagem só faz sentido se o arquivo existir; ajuste conforme necessidade)
        # if self.caminho_arquivo.exists() and not self.caminho_arquivo.is_file():
        #     raise ValueError(
        #         f"caminho_arquivo deve ser um arquivo, não um diretório: {self.caminho_arquivo}"
        #     )

        # Tamanho nunca negativo
        if self.tamanho_arquivo_bytes < 0:
            raise ValueError("tamanho_arquivo_bytes não pode ser negativo.")

        # Inferência do flag HTML (mantida como estava)
        if not self.file_is_html and self.caminho_arquivo.suffix.lower() == ".html":
            # Em dataclass normal podemos reatribuir (não é frozen)
            self.file_is_html = True

        # Consistência opcional: se foi explicitamente marcado como HTML, forçar sufixo .html/.htm?
        # (descomente se quiser essa rigidez)
        # if self.file_is_html and self.caminho_arquivo.suffix.lower() not in (".html", ".htm"):
        #     raise ValueError(
        #         f"Arquivo marcado como HTML mas sufixo é {self.caminho_arquivo.suffix}"
        #     )
