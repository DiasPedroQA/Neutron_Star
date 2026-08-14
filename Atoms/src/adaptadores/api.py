"""Adaptador HTTP e contratos OpenAPI da API de bookmarks."""

import logging
import os
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

# Configuração de logging
logger: logging.Logger = logging.getLogger(name=__name__)

# Diretório-base permitido para leitura de arquivos
# Em produção, isso viria de uma variável de ambiente

# para testes, mas não é bom para produção


def _get_base_dir() -> Path:
    return Path(os.getenv("NEUTRON_STAR__get_base_dir()", str(Path.home())))


EXEMPLO_CAMINHO = "/home/diaspedro/Downloads/bookmarks.html"


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
    )


def criar_resposta_resultado(
    resultado: ConversaoResultado,
) -> ConversaoResultadoResposta:
    """Converte o resultado do caso de uso no contrato de resposta HTTP."""
    return ConversaoResultadoResposta(
        arquivo=criar_resposta_arquivo(arquivo=resultado.arquivo),
        tags_extraidas=[criar_resposta_tag(tag)
                        for tag in resultado.tags_extraidas],
        erro=resultado.erro,  # ✅ inclui campo erro
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
    logger.info(msg="Health check realizado")
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
    logger.info(msg="Requisição para listar arquivos")
    use_case: ListarArquivos = cast(ListarArquivos, dependencia)
    arquivos: list[ArquivoTemp] = use_case.executar_busca()
    return ListarArquivosResposta(
        total=len(arquivos),
        arquivos=[criar_resposta_arquivo(arquivo) for arquivo in arquivos],
    )


def _validar_caminho(caminho: str) -> Path:
    """
    Valida que o caminho existe, é um arquivo, e está dentro do _get_base_dir().
    Retorna o Path absoluto ou levanta HTTPException.
    """
    try:
        caminho_abs: Path = Path(caminho).resolve()
    except Exception as e:
        logger.error(msg=f"Erro ao resolver caminho '{caminho}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Caminho inválido."
        ) from e

    # Verifica se está dentro do diretório-base permitido
    if not str(caminho_abs).startswith(str(_get_base_dir().resolve())):
        logger.warning(
            msg=f"Tentativa de acesso fora do base_dir: {caminho_abs}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Caminho fora do diretório permitido: {_get_base_dir()}",
        )

    if not caminho_abs.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arquivo não encontrado: {caminho_abs}",
        )

    if not caminho_abs.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Caminho não é um arquivo."
        )

    return caminho_abs


@router.post(
    path="/extrair_tags_do_arquivo",
    summary="Extrair bookmarks de um arquivo",
    description=(
        "Lê um arquivo HTML acessível ao servidor e extrai links de bookmark. "
        "Uma lista `tags` vazia é válida: nenhum link reconhecível foi encontrado."
    ),
    response_model=ExtrairTagsResposta,
    response_description="Bookmarks extraídos com sucesso.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Arquivo não encontrado."},
        status.HTTP_403_FORBIDDEN: {
            "description": "Caminho fora do diretório permitido."
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Caminho inválido ou não é um arquivo."
        },
    },
)
async def extrair_tags_do_arquivo(
    pedido: ExtrairTagsRequisicao,
    dependencia: DependenciaExtrairTags,
) -> ExtrairTagsResposta:
    """Extrai bookmarks de um arquivo cujo caminho foi informado pelo cliente."""
    logger.info(
        msg=f"Requisição para extrair tags do arquivo: {pedido.caminho}")

    # 🔒 Validação de segurança
    caminho_validado: Path = _validar_caminho(caminho=pedido.caminho)

    use_case: ExtrairTags = cast(ExtrairTags, dependencia)
    try:
        tags: list[TagExtraida] = use_case.executar_extracao(
            caminho=caminho_validado)
    except FileNotFoundError as error:
        logger.error(msg=f"Arquivo não encontrado: {error}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except PermissionError as error:
        logger.error(msg=f"Permissão negada: {error}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para ler o arquivo.",
        ) from error
    except IsADirectoryError as error:
        logger.error(msg=f"É um diretório: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O caminho aponta para um diretório, não um arquivo.",
        ) from error
    except Exception as error:
        logger.exception(msg=f"Erro inesperado ao extrair tags: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar o arquivo.",
        ) from error

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
    logger.info(msg="Requisição para buscar e extrair tags de todos os arquivos")
    use_case: BuscarEExtrairTags = cast(BuscarEExtrairTags, dependencia)
    resultados: list[ConversaoResultado] = use_case.executar()
    return BuscarEExtrairTagsResposta(
        total_arquivos=len(resultados),
        resultados=[criar_resposta_resultado(
            resultado) for resultado in resultados],
    )
