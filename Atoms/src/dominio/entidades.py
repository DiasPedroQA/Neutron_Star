# Atoms/dominio/entidades.py

"""Entidades centrais do domínio de arquivos html.

Este módulo não pode depender de frameworks (pydantic, fastapi, etc.) —
os contratos HTTP (DTOs de request/response) ficam em adaptadores/schemas.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArquivoTemp:
    """Representa um arquivo temporário com nome e conteúdo."""

    nome: str
    caminho_absoluto: str
    tamanho: int
    data_criacao: str | None = None
    ultima_modificacao: str | None = None
    data_acesso: str | None = None
    conteudo: str | None = None


@dataclass(frozen=True)
class TagExtraida:
    """Representa uma tag <a> extraída de um arquivo HTML."""

    titulo: str
    url: str
    data_criacao: str | None = None
    ultima_modificacao: str | None = None
    pasta: str | None = None


@dataclass(frozen=True)
class ConversaoResultado:
    """Representa o resultado da conversão de arquivos HTML."""

    arquivo: ArquivoTemp
    tags_extraidas: list[TagExtraida]
    erro: str | None = None
