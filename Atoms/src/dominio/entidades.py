# Atoms/src/dominio/entidades.py

"""Entidades centrais do domínio de arquivos html.

Este módulo não pode depender de frameworks (pydantic, fastapi, etc.) —
os contratos HTTP (DTOs de request/response) ficam em adaptadores/schemas.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Favorito:
    """
    Entidade de Domínio Pura.
    Representa o contrato essencial de um link de favorito no ecossistema Neutron Star.
    Como é definida como frozen=True, ela é imutável e thread-safe.
    """

    titulo: str
    url: str
    pasta: str = "Favoritos"
    data_adicao: str = "Sem data"

    def __post_init__(self) -> None:
        """Validações básicas de consistência de domínio."""
        if not self.url or not self.url.strip():
            raise ValueError("Um favorito precisa obrigatoriamente conter uma URL válida.")

    def to_dict(self) -> dict[str, str]:
        """Converte a entidade de domínio em um dicionário serializável padrão."""
        return {
            "Titulo": self.titulo or "Sem título",
            "URL": self.url,
            "Pasta": self.pasta or "Favoritos",
            "Data_Adicao": self.data_adicao or "Sem data",
        }
