"""Adaptador HTTP e contratos OpenAPI da API de bookmarks."""

import logging
import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from adaptadores.schemas import (
    ArquivoTempResposta,
    BuscarEExtrairTagsResposta,
    ConversaoResultadoResposta,
    ExtrairTagsRequisicao,
    ExtrairTagsResposta,
    ListarArquivosResposta,
    SaudeResposta,
    TagExtraidaResposta,
)
from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from dominio.entidades import ArquivoTemp, ConversaoResultado, TagExtraida
from montagem.dependencias import (
    obter_buscar_e_extrair,
    obter_extrair_tags,
    obter_listar_arquivos,
)

logger: logging.Logger = logging.getLogger(name=__name__)

# ------------------------------------------------------------
# Configuração de diretório base
# ------------------------------------------------------------


def _get_base_dir() -> Path:
    """Retorna o diretório base configurado via variável de ambiente."""
    return Path(os.getenv("NEUTRON_STAR_BASE_DIR", str(Path.home())))


# ------------------------------------------------------------
# Validação de caminho (segurança)
# ------------------------------------------------------------


def _validar_caminho(caminho: str) -> Path:
    """
    Valida que o caminho é seguro, existe e é um arquivo.

    Regras:
    - Deve estar dentro do diretório base.
    - Deve existir no sistema de arquivos.
    - Deve ser um arquivo (não diretório).

    Levanta HTTPException com status apropriado em caso de violação.
    """
    try:
        caminho_abs: Path = Path(caminho).resolve()
    except OSError as e:
        logger.error("Erro ao resolver caminho '%s': %s", caminho, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caminho inválido.",
        ) from e

    base_dir: Path = _get_base_dir().resolve()
    if not str(caminho_abs).startswith(str(base_dir)):
        logger.warning("Tentativa de acesso fora do base_dir: %s", caminho_abs)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Caminho fora do diretório permitido: {base_dir}",
        )

    if not caminho_abs.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arquivo não encontrado: {caminho_abs}",
        )

    if not caminho_abs.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caminho não é um arquivo.",
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
    """Converte ArquivoTemp (domínio) para ArquivoTempResposta (DTO)."""
    return ArquivoTempResposta(
        nome=arquivo.nome,
        caminho_absoluto=arquivo.caminho_absoluto,
        tamanho=arquivo.tamanho,
        data_criacao=arquivo.data_criacao,
        ultima_modificacao=arquivo.ultima_modificacao,  # corrigido
        data_acesso=arquivo.data_acesso,
        conteudo=arquivo.conteudo,
    )


def _para_tag_resposta(tag: TagExtraida) -> TagExtraidaResposta:
    """Converte TagExtraida (domínio) para TagExtraidaResposta (DTO)."""
    return TagExtraidaResposta(
        titulo=tag.titulo,
        url=tag.url,
        data_criacao=tag.data_criacao,
        ultima_modificacao=tag.ultima_modificacao,
        pasta=tag.pasta,
    )


def _para_resultado_resposta(resultado: ConversaoResultado) -> ConversaoResultadoResposta:
    """Converte ConversaoResultado (domínio) para DTO."""
    return ConversaoResultadoResposta(
        arquivo=_para_arquivo_resposta(resultado.arquivo),
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
)
async def health() -> SaudeResposta:
    """Verifica se a API está disponível e respondendo."""
    logger.info("Health check realizado")
    return SaudeResposta()


@router.get(
    path="/listar_arquivos",
    summary="Listar arquivos HTML",
    description=(
        "Localiza arquivos HTML de bookmarks no diretório configurado no servidor. "
        "A resposta inclui somente metadados; o conteúdo não é retornado."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Nenhum arquivo encontrado."},
        status.HTTP_403_FORBIDDEN: {"description": "Acesso negado ao diretório base."},
        status.HTTP_400_BAD_REQUEST: {"description": "Erro na listagem."},
    },
)
async def listar_arquivos(
    dependencia: DependenciaListarArquivos,
) -> ListarArquivosResposta:
    """Lista arquivos HTML de bookmarks conhecidos pelo servidor."""
    logger.info("Requisição para listar arquivos")
    arquivos: list[ArquivoTemp] = dependencia.executar_busca()
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
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Arquivo não encontrado."},
        status.HTTP_403_FORBIDDEN: {"description": "Caminho fora do diretório permitido."},
        status.HTTP_400_BAD_REQUEST: {"description": "Caminho inválido ou não é um arquivo."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Erro interno."},
    },
)
async def extrair_tags_do_arquivo(
    pedido: ExtrairTagsRequisicao,
    dependencia: DependenciaExtrairTags,
) -> ExtrairTagsResposta:
    """Extrai bookmarks de um arquivo HTML informado pelo cliente."""
    logger.info("Requisição para extrair tags do arquivo: %s", pedido.caminho)

    caminho_validado = _validar_caminho(pedido.caminho)

    try:
        tags = dependencia.executar_extracao(caminho=caminho_validado)
    except FileNotFoundError as e:
        logger.error("Arquivo não encontrado: %s", e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PermissionError as e:
        logger.error("Permissão negada: %s", e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para ler o arquivo.",
        ) from e
    except IsADirectoryError as e:
        logger.error("É um diretório: %s", e)
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
        "Falhas de leitura retornam uma lista de tags vazia para o arquivo afetado. "
        "Se nenhum arquivo for encontrado, a lista de resultados será vazia."
    ),
)
async def buscar_e_extrair_tags(
    dependencia: DependenciaBuscarEExtrair,
) -> BuscarEExtrairTagsResposta:
    """Busca arquivos HTML e extrai os links de cada um."""
    logger.info("Requisição para buscar e extrair tags de todos os arquivos")
    resultados: list[ConversaoResultado] = dependencia.executar()
    return BuscarEExtrairTagsResposta(
        total_arquivos=len(resultados),
        resultados=[_para_resultado_resposta(r) for r in resultados],
    )
