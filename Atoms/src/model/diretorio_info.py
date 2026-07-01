"""Modelo para diretórios."""

from __future__ import annotations

from dataclasses import dataclass, field

from .item_neutro import ItemBase


@dataclass(frozen=True)
class ItemDiretorio(ItemBase):
    """Representa um diretório.

    Atributos adicionais:
        qtd_itens: Número de entradas imediatas (None se não pôde ser lido).
        filhos: Tupla imutável de itens contidos (opcional, vazia por padrão).
    """

    qtd_itens: int | None = None
    filhos: tuple[ItemBase, ...] = field(default_factory=tuple)

    @property
    def eh_diretorio(self) -> bool:
        return True

    @property
    def listavel(self) -> bool:
        """Alias para permissão de listagem (executável em diretórios)."""
        return self.executavel
