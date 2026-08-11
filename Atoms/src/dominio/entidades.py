# Atoms/dominio/entidades.py

"""Entidades centrais do domínio de arquivos html."""

from dataclasses import dataclass


@dataclass
class ArquivoTemp:
    """Representa um arquivo temporário com nome e conteúdo."""
    nome: str
    caminho_absoluto: str
    tamanho: int
    data_criacao: str | None = None
    data_modificacao: str | None = None
    data_acesso: str | None = None
    conteudo: str | None = None


@dataclass
class TagExtraida:
    """Representa uma tag <a> extraída de um arquivo HTML."""
    titulo: str
    url: str
    data_criacao: str | None = None
    ultima_modificacao: str | None = None
    pasta: str | None = None
    tags: str | None = None


@dataclass
class ConversaoResultado:
    """Representa o resultado da conversão de arquivos HTML."""
    arquivo: ArquivoTemp
    tags_extraidas: list[TagExtraida]
