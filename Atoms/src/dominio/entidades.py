# Atoms/dominio/entidades.py

"""Entidades centrais do domínio de arquivos html."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EXEMPLO_CAMINHO = "/home/diaspedro/Downloads/bookmarks.html"


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


@dataclass
class ConversaoResultado:
    """Representa o resultado da conversão de arquivos HTML."""

    arquivo: ArquivoTemp
    tags_extraidas: list[TagExtraida]
    erro: str | None = None


class ArquivoTempResposta(BaseModel):
    """Metadados de um arquivo HTML localizado pela API."""

    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(description="Nome do arquivo no sistema de arquivos.")
    caminho_absoluto: str = Field(
        description="Caminho usado para ler o arquivo.")
    tamanho: int = Field(ge=0, description="Tamanho do arquivo em bytes.")
    data_criacao: str | None = Field(
        default=None, description="Data de criação em UTC."
    )
    data_modificacao: str | None = Field(
        default=None,
        description="Data da última modificação em UTC.",
    )
    data_acesso: str | None = Field(
        default=None, description="Data do último acesso em UTC."
    )
    conteudo: str | None = Field(
        default=None, description="Conteúdo; não é carregado nesta rota."
    )


class TagExtraidaResposta(BaseModel):
    """Bookmark extraído de uma tag HTML ``<a>``."""

    model_config = ConfigDict(from_attributes=True)

    titulo: str = Field(description="Texto visível do bookmark.")
    url: str = Field(description="URL presente no atributo HREF.")
    data_criacao: str | None = Field(
        default=None, description="ADD_DATE convertido para UTC."
    )
    ultima_modificacao: str | None = Field(
        default=None,
        description="LAST_MODIFIED convertido para UTC.",
    )
    pasta: str | None = Field(
        default=None, description="Pasta H3 associada ao bookmark."
    )


class ConversaoResultadoResposta(BaseModel):
    """Arquivo localizado e os bookmarks extraídos dele."""

    model_config = ConfigDict(from_attributes=True)

    arquivo: ArquivoTempResposta
    tags_extraidas: list[TagExtraidaResposta]
    # ✅ Adicionado campo erro
    erro: str | None = Field(
        default=None, description="Mensagem de erro se a extração falhou."
    )


class ListarArquivosResposta(BaseModel):
    """Resposta da busca por arquivos HTML."""

    status: Literal["sucesso"] = "sucesso"
    total: int = Field(ge=0, description="Quantidade de arquivos localizados.")
    arquivos: list[ArquivoTempResposta]


class ExtrairTagsRequisicao(BaseModel):
    """Corpo necessário para extrair bookmarks de um arquivo local."""

    caminho: str = Field(
        min_length=1,
        description="Caminho de um arquivo HTML acessível ao servidor.",
        examples=[EXEMPLO_CAMINHO],
    )


class ExtrairTagsResposta(BaseModel):
    """Resposta da extração de bookmarks de um arquivo."""

    status: Literal["sucesso"] = "sucesso"
    caminho: str = Field(description="Caminho recebido na requisição.")
    total: int = Field(
        ge=0, description="Quantidade de bookmarks reconhecidos.")
    tags: list[TagExtraidaResposta] = Field(
        description="Bookmarks válidos encontrados; pode ser uma lista vazia."
    )


class BuscarEExtrairTagsResposta(BaseModel):
    """Resposta da busca de arquivos seguida da extração de bookmarks."""

    status: Literal["sucesso"] = "sucesso"
    total_arquivos: int = Field(
        ge=0, description="Quantidade de arquivos processados.")
    resultados: list[ConversaoResultadoResposta]


class SaudeResposta(BaseModel):
    """Estado básico de disponibilidade da API."""

    status: Literal["ok"] = "ok"
