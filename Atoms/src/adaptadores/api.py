# src/adaptadores/api.py

"""Adaptador HTTP e contratos OpenAPI da API de bookmarks."""

import logging
import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.adaptadores.schemas import (
    ArquivoTempResposta,
    BuscarEExtrairTagsResposta,
    ConversaoResultadoResposta,
    ExtrairTagsRequisicao,
    ExtrairTagsResposta,
    ListarArquivosResposta,
    SaudeResposta,
    TagExtraidaResposta,
)
from src.aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from src.dominio.entidades import ArquivoTemp, ConversaoResultado, TagExtraida
from src.montagem.dependencias import (
    obter_buscar_e_extrair,
    obter_extrair_tags,
    obter_listar_arquivos,
)

logger: logging.Logger = logging.getLogger(name=__name__)

# ------------------------------------------------------------
# Configuração de diretório base (variável de ambiente)
# ------------------------------------------------------------


def _get_base_dir() -> Path:
    return Path(os.getenv("NEUTRON_STAR_BASE_DIR", str(Path.home())))


# ------------------------------------------------------------
# Validação de caminho (segurança)
# ------------------------------------------------------------


def _validar_caminho(caminho: str) -> Path:
    """
    Valida que o caminho existe, é um arquivo, e está dentro do _get_base_dir().
    Retorna o Path absoluto ou levanta HTTPException.
    """
    try:
        caminho_abs: Path = Path(caminho).resolve()
    except OSError as e:
        logger.error(msg=f"Erro ao resolver caminho '{caminho}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Caminho inválido."
        ) from e

    base_dir: Path = _get_base_dir().resolve()
    if not str(caminho_abs).startswith(str(base_dir)):
        logger.warning(msg=f"Tentativa de acesso fora do base_dir: {caminho_abs}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Caminho fora do diretório permitido: {base_dir}",
        )

    if not caminho_abs.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Arquivo não encontrado: {caminho_abs}"
        )

    if not caminho_abs.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Caminho não é um arquivo."
        )

    return caminho_abs


# ------------------------------------------------------------
# Router e injeção de dependências
# ------------------------------------------------------------
router = APIRouter(tags=["Bookmarks"])

DependenciaListarArquivos = Annotated[ListarArquivos, Depends(obter_listar_arquivos)]
DependenciaExtrairTags = Annotated[ExtrairTags, Depends(obter_extrair_tags)]
DependenciaBuscarEExtrair = Annotated[BuscarEExtrairTags, Depends(obter_buscar_e_extrair)]

# ------------------------------------------------------------
# Funções de conversão (entidade -> schema)
# ------------------------------------------------------------


def _para_arquivo_resposta(arquivo: ArquivoTemp) -> ArquivoTempResposta:
    return ArquivoTempResposta(
        nome=arquivo.nome,
        caminho_absoluto=arquivo.caminho_absoluto,
        tamanho=arquivo.tamanho,
        data_criacao=arquivo.data_criacao,
        ultima_modificacao=arquivo.ultima_modificacao,
        data_acesso=arquivo.data_acesso,
        conteudo=arquivo.conteudo,
    )


def _para_tag_resposta(tag: TagExtraida) -> TagExtraidaResposta:
    return TagExtraidaResposta(
        titulo=tag.titulo,
        url=tag.url,
        data_criacao=tag.data_criacao,
        ultima_modificacao=tag.ultima_modificacao,
        pasta=tag.pasta,
    )


def _para_resultado_resposta(resultado: ConversaoResultado) -> ConversaoResultadoResposta:
    return ConversaoResultadoResposta(
        arquivo=_para_arquivo_resposta(arquivo=resultado.arquivo),
        tags_extraidas=[_para_tag_resposta(t) for t in resultado.tags_extraidas],
        erro=resultado.erro,
    )


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------


@router.get(
    path="/health",
    summary="Verificar disponibilidade",
    description="Retorna o estado da API sem acessar o sistema de arquivos.",
    response_description="API disponível.",
)
async def health() -> SaudeResposta:
    """Verifica se a API está disponível e respondendo."""
    logger.info(msg="Health check realizado")
    return SaudeResposta()


@router.get(
    path="/listar_arquivos",
    summary="Listar arquivos HTML",
    description=(
        "Localiza arquivos HTML de bookmarks no diretório configurado no servidor. "
        "A resposta inclui somente metadados; o conteúdo não é retornado."
    ),
    response_description="Arquivos HTML localizados com sucesso.",
)
async def listar_arquivos(
    dependencia: DependenciaListarArquivos,
) -> ListarArquivosResposta:
    """
    Lista arquivos HTML de bookmarks conhecidos pelo servidor.
    Retorna apenas metadados dos arquivos sem incluir o conteúdo.
    """
    logger.info(msg="Requisição para listar arquivos")
    use_case: ListarArquivos = dependencia
    arquivos: list[ArquivoTemp] = use_case.executar_busca()
    return ListarArquivosResposta(
        total=len(arquivos),
        arquivos=[_para_arquivo_resposta(a) for a in arquivos],
    )


@router.post(
    path="/extrair_tags_do_arquivo",
    summary="Extrair bookmarks de um arquivo",
    description=(
        "Lê um arquivo HTML acessível ao servidor e extrai links de bookmark. "
        "Uma lista `tags` vazia é válida: nenhum link reconhecível foi encontrado."
    ),
    response_description="Bookmarks extraídos com sucesso.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Arquivo não encontrado."},
        status.HTTP_403_FORBIDDEN: {"description": "Caminho fora do diretório permitido."},
        status.HTTP_400_BAD_REQUEST: {"description": "Caminho inválido ou não é um arquivo."},
    },
)
async def extrair_tags_do_arquivo(
    pedido: ExtrairTagsRequisicao,
    dependencia: DependenciaExtrairTags,
) -> ExtrairTagsResposta:
    """Extrai bookmarks de um arquivo HTML informado pelo cliente."""
    logger.info(msg=f"Requisição para extrair tags do arquivo: {pedido.caminho}")

    caminho_validado: Path = _validar_caminho(caminho=pedido.caminho)

    use_case: ExtrairTags = dependencia
    try:
        tags: list[TagExtraida] = use_case.executar_extracao(caminho=caminho_validado)
    except FileNotFoundError as e:
        logger.error(msg=f"Arquivo não encontrado: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PermissionError as e:
        logger.error(msg=f"Permissão negada: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para ler o arquivo."
        ) from e
    except IsADirectoryError as e:
        logger.error(msg=f"É um diretório: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O caminho aponta para um diretório, não um arquivo.",
        ) from e
    except Exception as e:
        logger.exception(msg=f"Erro inesperado ao extrair tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar o arquivo.",
        ) from e

    return ExtrairTagsResposta(
        caminho=pedido.caminho,
        total=len(tags),
        tags=[_para_tag_resposta(t) for t in tags],
    )


@router.get(
    path="/buscar_e_extrair_tags",
    summary="Localizar arquivos e extrair bookmarks",
    description=(
        "Executa a busca de arquivos HTML e a extração de bookmarks em cada arquivo localizado. "
        "Falhas de leitura retornam uma lista de tags vazia para o arquivo afetado."
    ),
    response_description="Arquivos processados com suas respectivas tags.",
)
async def buscar_e_extrair_tags(
    dependencia: DependenciaBuscarEExtrair,
) -> BuscarEExtrairTagsResposta:
    """Busca arquivos HTML de bookmarks e extrai os links de cada um."""
    logger.info(msg="Requisição para buscar e extrair tags de todos os arquivos")

    use_case: BuscarEExtrairTags = dependencia
    resultados: list[ConversaoResultado] = use_case.executar()
    return BuscarEExtrairTagsResposta(
        total_arquivos=len(resultados),
        resultados=[_para_resultado_resposta(resultado=r) for r in resultados],
    )
