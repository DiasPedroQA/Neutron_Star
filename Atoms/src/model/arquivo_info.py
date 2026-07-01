"""Modelo para arquivos."""

from __future__ import annotations

from dataclasses import dataclass

from .item_neutro import ItemBase


@dataclass(frozen=True)
class ItemArquivo(ItemBase):
    """Representa um arquivo concreto.

    Atributos adicionais:
        tipo_mime: Tipo MIME detectado (ex.: 'text/plain').
        hash_checksum: Hash do conteúdo (ex.: SHA-256), se calculado.
    """

    tipo_mime: str | None = None
    hash_checksum: str | None = None

    @property
    def eh_diretorio(self) -> bool:
        return False

    def metadados_coincidem(self, outro: ItemArquivo) -> bool:
        """Compara metadados com outro arquivo sem abrir o conteúdo.

        Considera tamanho, data de modificação e permissões.
        Retorna True se forem idênticos ou se forem o mesmo caminho.
        """
        if self.caminho == outro.caminho:
            return True
        return (
            self.tamanho == outro.tamanho
            and self.modificado == outro.modificado
            and self.legivel == outro.legivel
            and self.gravavel == outro.gravavel
            and self.executavel == outro.executavel
        )
