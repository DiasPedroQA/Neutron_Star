# Atoms/src/models/item_neutro.py

"""Módulo que define a base abstrata para itens do sistema de arquivos.

Esta base é utilizada por modelos concretos de arquivos e diretórios,
fornecendo atributos e métodos comuns a ambos.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ItemBase(ABC):
    """Representa uma entrada no sistema de arquivos (arquivo ou diretório).

    Esta classe é abstrata e não deve ser instanciada diretamente.
    Utilize as subclasses ItemArquivo ou ItemDiretorio.

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
        """Retorna o nome do item (último componente do caminho)."""
        return self.caminho.name

    @property
    def sufixo(self) -> str:
        """Retorna a extensão do arquivo (ex.: '.txt').

        Para diretórios, retorna uma string vazia.
        """
        return self.caminho.suffix

    @property
    @abstractmethod
    def eh_diretorio(self) -> bool:
        """Indica se o item é um diretório.

        Returns:
            True se for diretório, False se for arquivo.
        """
        ...

    def para_dict(self) -> dict[str, str | int | bool | None]:
        """Serializa os atributos comuns do item para um dicionário.

        As subclasses devem sobrescrever este método para incluir
        seus atributos específicos, chamando super().para_dict().

        Returns:
            Dicionário com os campos básicos do item.
        """
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
