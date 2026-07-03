# Atoms/src/models/arquivo_info.py

"""Módulo que define o modelo concreto para arquivos do sistema.

Fornece a classe ItemArquivo, que representa um arquivo com metadados
adicionais como tipo MIME e hash de conteúdo.
"""

from __future__ import annotations

from dataclasses import dataclass

from .item_neutro import ItemBase


@dataclass(frozen=True)
class ItemArquivo(ItemBase):
    """Representa um arquivo concreto no sistema de arquivos.

    Além dos atributos herdados de ItemBase, adiciona informações
    específicas de arquivos, como tipo MIME e checksum.

    Atributos adicionais:
        tipo_mime: Tipo MIME detectado (ex.: 'text/plain').
        hash_checksum: Hash do conteúdo (ex.: SHA-256), se calculado.
    """

    tipo_mime: str | None = None
    hash_checksum: str | None = None

    @property
    def eh_diretorio(self) -> bool:
        """Sobrescrita para indicar que este item NÃO é um diretório."""
        return False

    def metadados_coincidem(self, outro: ItemArquivo) -> bool:
        """Compara metadados essenciais com outro arquivo sem abrir o conteúdo.

        A comparação considera tamanho, data de modificação e permissões.
        Se os caminhos forem idênticos, retorna True imediatamente.

        Args:
            outro: Outra instância de ItemArquivo para comparação.

        Returns:
            True se os metadados forem iguais ou se for o mesmo caminho.
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

    def para_dict(self) -> dict[str, str | int | bool | None]:
        """Serializa o arquivo para dicionário, incluindo tipo MIME e hash.

        Returns:
            Dicionário com todos os atributos, incluindo os específicos.
        """
        d: dict[str, str | int | bool | None] = super().para_dict()
        new_data: dict[str, str | int | bool | None] = {
            "tipo_mime": self.tipo_mime,
            "hash_checksum": self.hash_checksum,
        }
        d |= new_data
        return d
