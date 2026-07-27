"""Tipos compartilhados do domínio da aplicação."""

from pathlib import Path
from typing import TypedDict

from dominio.entidades import VirtualFolder


class ParametrosBusca(TypedDict, total=False):
    """Parâmetros iniciais e resultados parciais do pipeline."""

    diretorio: Path
    formatos_exportacao: list[str]
    diretorio_saida: str
    # Resultados produzidos pelas etapas
    arquivos_encontrados: list[Path]
    arquivo_selecionado: Path
    raiz_bookmarks: VirtualFolder


class PipelineConfig(TypedDict):
    """Configuração das etapas do pipeline de processamento de bookmarks.
    Define a sequência de nomes de etapas que serão executadas na aplicação."""

    etapas: list[str]


class AppConfig(TypedDict, total=False):
    """Configuração de alto nível da aplicação de bookmarks.
    Agrupa a definição do pipeline e os parâmetros de busca utilizados em uma execução."""

    pipeline: PipelineConfig
    parametros: ParametrosBusca
