"""Entidades de domínio compartilhadas entre os serviços do Neutron Star."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Bookmark:
    """Representa um favorito extraído de um arquivo Netscape Bookmark (.html).

    `para_dict`/`de_dict` formam o contrato de serialização usado entre os
    microsserviços (busca_api → orquestrador_api → conversao_api), já que
    o dataclass deixa de poder ser compartilhado por import direto quando
    cada serviço roda em processo/deploy separado.
    """

    titulo: str
    url: str
    data_adicao: datetime | None = None
    pasta: str = ""
    icone: str | None = None

    def para_dict(self) -> dict[str, str | None]:
        """Serializa o bookmark para um dicionário JSON-compatível."""
        return {
            "titulo": self.titulo,
            "url": self.url,
            "data_adicao": self.data_adicao.isoformat() if self.data_adicao else None,
            "pasta": self.pasta,
            "icone": self.icone,
        }

    @classmethod
    def de_dict(cls, dados: dict[str, str | None]) -> Bookmark:
        """Reconstrói um `Bookmark` a partir de um dicionário recebido via HTTP."""
        data_adicao_str = dados.get("data_adicao")
        return cls(
            titulo=str(dados["titulo"]),
            url=str(dados["url"]),
            data_adicao=datetime.fromisoformat(data_adicao_str) if data_adicao_str else None,
            pasta=str(dados.get("pasta") or ""),
            icone=dados.get("icone"),
        )
