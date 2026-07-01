"""Item base abstrato para arquivos e diretórios."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ItemBase(ABC):
    """Representa uma entrada no sistema de arquivos (arquivo ou diretório).

    Atributos:
        caminho: Caminho absoluto do item.
        modificado: Data de última modificação (None se indisponível).
        tamanho: Tamanho em bytes (para arquivos) ou None.
        legivel: Se o item pode ser lido pelo processo atual.
        gravavel: Se o item pode ser escrito pelo processo atual.
        executavel: Se o item é executável (ou listável, para diretórios).
        oculto: Se o item é considerado oculto pelo SO.
    """

    caminho: Path
    modificado: datetime | None = None
    tamanho: int | None = None
    legivel: bool = False
    gravavel: bool = False
    executavel: bool = False
    oculto: bool = False

    @property
    def nome(self) -> str:
        """Nome do item (último componente do caminho)."""
        return self.caminho.name

    @property
    def sufixo(self) -> str:
        """Extensão do arquivo (ex.: '.txt')."""
        return self.caminho.suffix

    @property
    @abstractmethod
    def eh_diretorio(self) -> bool:
        """True se for diretório, False se for arquivo."""
        ...

    def para_dict(self) -> dict:
        """Serializa o item para um dicionário simples."""
        return {
            "caminho": str(self.caminho),
            "nome": self.nome,
            "modificado": self.modificado.isoformat() if self.modificado else None,
            "tamanho": self.tamanho,
            "eh_diretorio": self.eh_diretorio,
            "legivel": self.legivel,
            "gravavel": self.gravavel,
            "executavel": self.executavel,
            "oculto": self.oculto,
        }
