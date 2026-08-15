# Atoms/dependencias.py

"""Configuração de dependências (injeção simples)."""

import logging
import os

from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from infra.buscador import PastaBuscadora
from infra.leitor import LeitorArquivoHTML

logger: logging.Logger = logging.getLogger(name=__name__)

# Configurações via ambiente (com fallbacks)
INCLUIR_OCULTOS: bool = os.getenv("INCLUIR_OCULTOS", "false").lower() == "true"
EXCLUIR_PRIVADOS: bool = os.getenv("EXCLUIR_PRIVADOS", "true").lower() == "true"


def obter_listar_arquivos() -> ListarArquivos:
    """Fábrica para ListarArquivos com PastaBuscadora."""
    buscador = PastaBuscadora(
        incluir_ocultos=INCLUIR_OCULTOS, excluir_privados=EXCLUIR_PRIVADOS
    )
    logger.info(
        "Criando ListarArquivos com PastaBuscadora (ocultos=%s, privados=%s)",
        INCLUIR_OCULTOS,
        EXCLUIR_PRIVADOS,
    )
    return ListarArquivos(diretorio=buscador)


def obter_extrair_tags() -> ExtrairTags:
    """Fábrica para ExtrairTags com LeitorArquivoHTML."""
    leitor = LeitorArquivoHTML()
    logger.info(msg="Criando ExtrairTags com LeitorArquivoHTML")
    return ExtrairTags(leitor=leitor)


def obter_buscar_e_extrair() -> BuscarEExtrairTags:
    """
    Fábrica para BuscarEExtrairTags.
    Compõe ListarArquivos e ExtrairTags a partir de suas respectivas fábricas.
    """
    listar_arquivos: ListarArquivos = obter_listar_arquivos()
    extrair_tags: ExtrairTags = obter_extrair_tags()
    logger.info(msg="Criando BuscarEExtrairTags com ListarArquivos e ExtrairTags")
    return BuscarEExtrairTags(
        listar_arquivos=listar_arquivos, extrair_tags=extrair_tags
    )
