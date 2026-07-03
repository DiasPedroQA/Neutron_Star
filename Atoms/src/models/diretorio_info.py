# Atoms/src/models/diretorio_info.py

"""Módulo que define o modelo concreto para diretórios do sistema.

Fornece a classe ItemDiretorio, que representa um diretório com
capacidade de armazenar seus filhos e contagem de itens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .item_neutro import ItemBase


@dataclass(frozen=True)
class ItemDiretorio(ItemBase):
    """Representa um diretório concreto no sistema de arquivos.

    Além dos atributos herdados de ItemBase, permite armazenar
    uma lista imutável de itens filhos e a quantidade total de entradas.

    Atributos adicionais:
        qtd_itens: Número de entradas imediatas (None se não pôde ser lido).
        filhos: Tupla imutável de itens contidos (opcional, vazia por padrão).
    """

    qtd_itens: int | None = None
    filhos: tuple[ItemBase, ...] = field(default_factory=tuple)

    @property
    def eh_diretorio(self) -> bool:
        """Sobrescrita para indicar que este item É um diretório."""
        return True

    @property
    def listavel(self) -> bool:
        """Indica se o diretório pode ser listado.

        Em sistemas Unix, a permissão de execução em diretórios
        equivale à permissão de listagem (entrar no diretório).

        Returns:
            True se o diretório puder ser listado.
        """
        return self.executavel

    def para_dict(self) -> dict[str, str | int | bool | None]:
        """Serializa o diretório para dicionário, incluindo contagem e filhos.

        Cada filho também é serializado recursivamente via seu próprio
        método para_dict().

        Returns:
            Dicionário com todos os atributos, incluindo os específicos.
        """
        d: dict[str, Any] = super().para_dict()
        d |= {
            "qtd_itens": self.qtd_itens,
            "filhos": [filho.para_dict() for filho in self.filhos],
        }
        return d
