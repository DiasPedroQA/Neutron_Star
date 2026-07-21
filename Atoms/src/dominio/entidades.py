"""Entidades do domínio de bookmarks."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TagA:
    """Favorito individual (tag <A>)."""

    url: str
    titulo: str
    data_adicao: str = ""
    ultima_modificacao: str = ""
    icon_uri: str = ""

    def to_dict(self) -> dict[str, str]:
        """Converte o favorito em um dicionário serializável.

        Returns:
            dict[str, str]: URL, título, datas e ícone do favorito.
        """
        return {
            "url": self.url,
            "titulo": self.titulo,
            "data_adicao": self.data_adicao,
            "ultima_modificacao": self.ultima_modificacao,
            "icon_uri": self.icon_uri,
        }


@dataclass(frozen=True)
class VirtualFolder:
    """Pasta que contém favoritos ou outras pastas."""

    nome: str
    data_adicao: str = ""
    ultima_modificacao: str = ""
    filhos_da_pasta: list[ItemPasta] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Converte a pasta de bookmarks em um dicionário serializável.

        Returns:
            dict[str, object]: Nome, datas e itens filhos da pasta.
        """
        return {
            "nome": self.nome,
            "data_adicao": self.data_adicao,
            "ultima_modificacao": self.ultima_modificacao,
            "filhos_da_pasta": [item.to_dict() for item in self.filhos_da_pasta],
        }


ItemPasta = TagA | VirtualFolder
