"""Adaptador HTTP e contratos OpenAPI da API de bookmarks."""

from pathlib import Path
from typing import Annotated, Any, Literal, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from dominio.entidades import ArquivoTemp, ConversaoResultado, TagExtraida
from montagem.dependencias import (
    obter_buscar_e_extrair,
    obter_extrair_tags,
    obter_listar_arquivos,
)

EXEMPLO_CAMINHO = "/caminho/para/bookmarks.html"


class ArquivoTempResposta(BaseModel):
    """Metadados de um arquivo HTML localizado pela API."""

    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(description="Nome do arquivo no sistema de arquivos.")
    caminho_absoluto: str = Field(description="Caminho usado para ler o arquivo.")
    tamanho: int = Field(ge=0, description="Tamanho do arquivo em bytes.")
    data_criacao: str | None = Field(default=None, description="Data de criação em UTC.")
    data_modificacao: str | None = Field(
        default=None,
        description="Data da última modificação em UTC.",
    )
    data_acesso: str | None = Field(default=None, description="Data do último acesso em UTC.")
    conteudo: str | None = Field(default=None, description="Conteúdo; não é carregado nesta rota.")


class TagExtraidaResposta(BaseModel):
    """Bookmark extraído de uma tag HTML ``<a>``."""

    model_config = ConfigDict(from_attributes=True)

    titulo: str = Field(description="Texto visível do bookmark.")
    url: str = Field(description="URL presente no atributo HREF.")
    data_criacao: str | None = Field(default=None, description="ADD_DATE convertido para UTC.")
    ultima_modificacao: str | None = Field(
        default=None,
        description="LAST_MODIFIED convertido para UTC.",
    )
    pasta: str | None = Field(default=None, description="Pasta H3 associada ao bookmark.")
    tags: str | None = Field(default=None, description="Atributo TAGS original.")


class ConversaoResultadoResposta(BaseModel):
    """Arquivo localizado e os bookmarks extraídos dele."""

    model_config = ConfigDict(from_attributes=True)

    arquivo: ArquivoTempResposta
    tags_extraidas: list[TagExtraidaResposta]


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
    total: int = Field(ge=0, description="Quantidade de bookmarks reconhecidos.")
    tags: list[TagExtraidaResposta] = Field(
        description="Bookmarks válidos encontrados; pode ser uma lista vazia."
    )


class BuscarEExtrairTagsResposta(BaseModel):
    """Resposta da busca de arquivos seguida da extração de bookmarks."""

    status: Literal["sucesso"] = "sucesso"
    total_arquivos: int = Field(ge=0, description="Quantidade de arquivos processados.")
    resultados: list[ConversaoResultadoResposta]


class SaudeResposta(BaseModel):
    """Estado básico de disponibilidade da API."""

    status: Literal["ok"] = "ok"


router = APIRouter(tags=["Bookmarks"])

DependenciaListarArquivos = Annotated[Any, Depends(obter_listar_arquivos)]
DependenciaExtrairTags = Annotated[Any, Depends(obter_extrair_tags)]
DependenciaBuscarEExtrair = Annotated[Any, Depends(obter_buscar_e_extrair)]


def criar_resposta_arquivo(arquivo: ArquivoTemp) -> ArquivoTempResposta:
    """Converte uma entidade de arquivo no contrato de resposta HTTP."""
    return ArquivoTempResposta(
        nome=arquivo.nome,
        caminho_absoluto=arquivo.caminho_absoluto,
        tamanho=arquivo.tamanho,
        data_criacao=arquivo.data_criacao,
        data_modificacao=arquivo.data_modificacao,
        data_acesso=arquivo.data_acesso,
        conteudo=arquivo.conteudo,
    )


def criar_resposta_tag(tag: TagExtraida) -> TagExtraidaResposta:
    """Converte uma entidade de bookmark no contrato de resposta HTTP."""
    return TagExtraidaResposta(
        titulo=tag.titulo,
        url=tag.url,
        data_criacao=tag.data_criacao,
        ultima_modificacao=tag.ultima_modificacao,
        pasta=tag.pasta,
        tags=tag.tags,
    )


def criar_resposta_resultado(
    resultado: ConversaoResultado,
) -> ConversaoResultadoResposta:
    """Converte o resultado do caso de uso no contrato de resposta HTTP."""
    return ConversaoResultadoResposta(
        arquivo=criar_resposta_arquivo(resultado.arquivo),
        tags_extraidas=[criar_resposta_tag(tag) for tag in resultado.tags_extraidas],
    )


@router.get(
    path="/health",
    summary="Verificar disponibilidade",
    description="Retorna o estado da API sem acessar o sistema de arquivos.",
    response_model=SaudeResposta,
    response_description="API disponível.",
)
async def health() -> SaudeResposta:
    """Informa que o processo FastAPI está disponível."""
    return SaudeResposta()


@router.get(
    path="/listar_arquivos",
    summary="Listar arquivos HTML",
    description=(
        "Localiza arquivos HTML de bookmarks no diretório configurado no servidor. "
        "A resposta inclui somente metadados; o conteúdo não é retornado."
    ),
    response_model=ListarArquivosResposta,
    response_description="Arquivos HTML localizados com sucesso.",
)
async def listar_arquivos(
    dependencia: DependenciaListarArquivos,
) -> ListarArquivosResposta:
    """Localiza os arquivos HTML e retorna seus metadados."""
    use_case: ListarArquivos = cast(ListarArquivos, dependencia)
    arquivos: list[ArquivoTemp] = use_case.executar_busca()
    return ListarArquivosResposta(
        total=len(arquivos),
        arquivos=[criar_resposta_arquivo(arquivo) for arquivo in arquivos],
    )


@router.post(
    path="/extrair_tags_do_arquivo",
    summary="Extrair bookmarks de um arquivo",
    description=(
        "Lê um arquivo HTML acessível ao servidor e extrai links de bookmark. "
        "Uma lista `tags` vazia é válida: nenhum link reconhecível foi encontrado."
    ),
    response_model=ExtrairTagsResposta,
    response_description="Bookmarks extraídos com sucesso.",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Arquivo não encontrado."}},
)
async def extrair_tags_do_arquivo(
    pedido: ExtrairTagsRequisicao,
    dependencia: DependenciaExtrairTags,
) -> ExtrairTagsResposta:
    """Extrai bookmarks de um arquivo cujo caminho foi informado pelo cliente."""
    use_case = cast(ExtrairTags, dependencia)
    try:
        tags: list[TagExtraida] = use_case.executar_extracao(caminho=Path(pedido.caminho))
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return ExtrairTagsResposta(
        caminho=pedido.caminho,
        total=len(tags),
        tags=[criar_resposta_tag(tag) for tag in tags],
    )


@router.get(
    path="/buscar_e_extrair_tags",
    summary="Localizar arquivos e extrair bookmarks",
    description=(
        "Executa a busca de arquivos HTML e a extração de bookmarks em cada arquivo localizado. "
        "Falhas de leitura retornam uma lista de tags vazia para o arquivo afetado."
    ),
    response_model=BuscarEExtrairTagsResposta,
    response_description="Arquivos processados com suas respectivas tags.",
)
async def buscar_e_extrair_tags(
    dependencia: DependenciaBuscarEExtrair,
) -> BuscarEExtrairTagsResposta:
    """Localiza todos os arquivos e associa a cada um os bookmarks encontrados."""
    use_case = cast(BuscarEExtrairTags, dependencia)
    resultados: list[ConversaoResultado] = use_case.executar()
    return BuscarEExtrairTagsResposta(
        total_arquivos=len(resultados),
        resultados=[criar_resposta_resultado(resultado) for resultado in resultados],
    )
