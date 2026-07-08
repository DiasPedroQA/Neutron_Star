"""Módulo que define o modelo concreto para arquivos do sistema."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Permissoes:
    """Agrupa permissões de acesso a um arquivo."""

    legivel: bool
    gravavel: bool
    executavel: bool


@dataclass(frozen=True)
class Arquivo:
    """Representa um arquivo concreto no sistema de arquivos."""

    caminho: Path
    tamanho: int | None
    modificado: datetime | None
    permissoes: Permissoes
    oculto: bool
    tipo_mime: str | None = None
    hash_checksum: str | None = None

    @property
    def nome(self) -> str:
        """Nome do arquivo (último componente do caminho)."""
        return self.caminho.name

    @property
    def legivel(self) -> bool:
        """Alias para permissão de leitura."""
        return self.permissoes.legivel

    @property
    def gravavel(self) -> bool:
        """Alias para permissão de escrita."""
        return self.permissoes.gravavel

    @property
    def executavel(self) -> bool:
        """Alias para permissão de execução."""
        return self.permissoes.executavel
