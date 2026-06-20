# Atoms/backend/core/entidades/entidade_sistema_operacional.py

"""Entidade de domínio que representa o sistema operacional local."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger: logging.Logger = logging.getLogger(name=__name__)


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
        # Log de uso do parâmetro legado
        if pasta_usuario is None and user_home is not None:
            logger.info(
                "Usando parâmetro 'user_home' em vez de 'pasta_usuario': %s",
                user_home,
            )

        object.__setattr__(self, "nome_sistema", nome_sistema)
        object.__setattr__(self, "versao_sistema", versao_sistema)
        object.__setattr__(self, "pasta_usuario", pasta_usuario or user_home)

        logger.debug(
            "ModeloSistemaOperacional criado: nome=%r, versao=%r, home=%s",
            self.nome_sistema,
            self.versao_sistema,
            self.pasta_usuario,
        )

        self.__post_init__()

    def __post_init__(self) -> None:
        self._validar_texto_do_sistema()
        self._validar_pasta_usuario()

    def _validar_texto_do_sistema(self) -> None:
        if not isinstance(self.nome_sistema, str) or not self.nome_sistema.strip():
            logger.error("nome_sistema inválido: %r", self.nome_sistema)
            raise ValueError("nome_sistema deve ser uma string não vazia.")
        if not isinstance(self.versao_sistema, str) or not self.versao_sistema.strip():
            logger.error("versao_sistema inválido: %r", self.versao_sistema)
            raise ValueError("versao_sistema deve ser uma string não vazia.")

        for attr, valor in [
            ("nome_sistema", self.nome_sistema),
            ("versao_sistema", self.versao_sistema),
        ]:
            if "\n" in valor or "\r" in valor:
                logger.warning("%s contém quebra de linha: %r", attr, valor)
                raise ValueError(f"{attr} não pode conter quebras de linha.")
            if "/" in valor or "\\" in valor:
                logger.warning("%s contém barra de caminho: %r", attr, valor)
                raise ValueError(f"{attr} não pode conter barras (path).")

    def _validar_pasta_usuario(self) -> None:
        if not isinstance(self.pasta_usuario, Path):
            logger.error("pasta_usuario não é Path: %r", self.pasta_usuario)
            raise TypeError("pasta_usuario deve ser Path.")
        if not self.pasta_usuario.is_absolute():
            logger.error("Home não é absoluto: %s", self.pasta_usuario)
            raise ValueError(f"Home deve ser caminho absoluto: {self.pasta_usuario}")
        if not self.pasta_usuario.is_dir():
            logger.warning("Home não é um diretório existente: %s", self.pasta_usuario)
            raise ValueError(
                f"Home deve ser um diretório existente: {self.pasta_usuario}"
            )

    @property
    def user_home(self) -> Path:
        """Alias de compatibilidade para `pasta_usuario`."""
        logger.debug("Acessando alias 'user_home'")
        return self.pasta_usuario
