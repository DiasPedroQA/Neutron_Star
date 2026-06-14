# Atoms/backend/core/entidades/entidade_sistema_operacional.py

"""Modelos de dados principais do domínio: Sistema Operacional."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModeloSistemaOperacional:
    """Representa o sistema operacional onde a execução ocorre."""

    nome_sistema: str  # "Windows", "Linux", "Darwin"
    versao_sistema: str  # ex: "10", "22.04"
    user_home: Path  # caminho absoluto para o diretório do usuário

    def __post_init__(self) -> None:
        self._validar_texto_do_sistema()
        self._validar_user_home()

    def _validar_texto_do_sistema(self) -> None:
        if not isinstance(self.nome_sistema, str) or not self.nome_sistema.strip():
            raise ValueError("nome_sistema deve ser uma string não vazia.")
        if not isinstance(self.versao_sistema, str) or not self.versao_sistema.strip():
            raise ValueError("versao_sistema deve ser uma string não vazia.")

        for attr, valor in [
            ("nome_sistema", self.nome_sistema),
            ("versao_sistema", self.versao_sistema),
        ]:
            if "\n" in valor or "\r" in valor:
                raise ValueError(f"{attr} não pode conter quebras de linha.")
            if "/" in valor or "\\" in valor:
                raise ValueError(f"{attr} não pode conter barras (path).")

    def _validar_user_home(self) -> None:
        if not isinstance(self.user_home, Path):
            raise TypeError("user_home deve ser Path.")
        if not self.user_home.is_absolute():
            raise ValueError(f"Home deve ser caminho absoluto: {self.user_home}")
        if not self.user_home.is_dir():
            raise ValueError(f"Home deve ser um diretório existente: {self.user_home}")
