"""Entidade de domínio que representa o sistema operacional local."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, init=False)
class ModeloSistemaOperacional:
    """Representa o sistema operacional onde a execução ocorre."""

    nome_sistema: str
    versao_sistema: str
    pasta_usuario: Path

    def __init__(
        self,
        nome_sistema: str,
        versao_sistema: str,
        pasta_usuario: Path | None = None,
        *,
        user_home: Path | None = None,
    ) -> None:
        object.__setattr__(self, "nome_sistema", nome_sistema)
        object.__setattr__(self, "versao_sistema", versao_sistema)
        object.__setattr__(self, "pasta_usuario", pasta_usuario or user_home)
        self.__post_init__()

    def __post_init__(self) -> None:
        self._validar_texto_do_sistema()
        self._validar_pasta_usuario()

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

    def _validar_pasta_usuario(self) -> None:
        if not isinstance(self.pasta_usuario, Path):
            raise TypeError("pasta_usuario deve ser Path.")
        if not self.pasta_usuario.is_absolute():
            raise ValueError(f"Home deve ser caminho absoluto: {self.pasta_usuario}")
        if not self.pasta_usuario.is_dir():
            raise ValueError(
                f"Home deve ser um diretório existente: {self.pasta_usuario}"
            )

    @property
    def user_home(self) -> Path:
        """Alias de compatibilidade para `pasta_usuario`."""
        return self.pasta_usuario
