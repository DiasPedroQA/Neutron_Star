"""Domínio compartilhado do projeto Neutron Star."""

from dominio.entidades import Bookmark
from dominio.excecoes import ArquivoInvalidoError, ErroDominioNeutron, PastaInvalidaError

__all__ = [
    "Bookmark",
    "ArquivoInvalidoError",
    "ErroDominioNeutron",
    "PastaInvalidaError",
]
