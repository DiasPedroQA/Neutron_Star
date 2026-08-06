"""
Caso de uso: converter um arquivo HTML de bookmarks (Netscape) em um
DataFrame tabular e exportá-lo para um ou mais formatos de arquivo.
"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup, Tag
from pandas import DataFrame

from src.aplicacao.exportadores import WRITERS
from src.aplicacao.leitura import (
    ler_arquivo_com_fallback,
    parsear_html,
    raiz_bookmarks,
)
from src.dominio.arvore import extrair_arvore, flatten_tree
from src.dominio.entidades import BookmarkNode

logger: logging.Logger = logging.getLogger(name=__name__)


def parse_bookmarks_html(html_path: Path, extrair_icone: bool = False) -> DataFrame:
    """
    Extrai todos os links de um arquivo HTML de bookmarks (Netscape)
    e retorna um DataFrame plano.

    Args:
        html_path: Caminho para o arquivo HTML.
        extrair_icone: Se True, inclui a coluna 'icon' com o base64 original.
                       Caso contrário, a coluna é omitida.

    Returns:
        DataFrame com colunas: title, url, add_date, folder (e icon se solicitado).
    """
    conteudo: str = ler_arquivo_com_fallback(caminho=html_path)
    soup: BeautifulSoup = parsear_html(conteudo)
    root_dl: Tag | None = raiz_bookmarks(soup)

    if not root_dl:
        logger.warning("Aviso: estrutura de bookmarks não encontrada em %s", html_path)
        return pd.DataFrame()

    arvore: list[BookmarkNode] = extrair_arvore(tag_dl=root_dl)
    records: list[dict[str, str]] = flatten_tree(nodes=arvore)

    df: pd.DataFrame = pd.DataFrame(records)
    if not extrair_icone and "icon" in df.columns:
        df = df.drop(columns=["icon"])
    return df


def converter_arquivos(
    lista_paths: list[Path],
    parser: Callable[[Path], DataFrame] = parse_bookmarks_html,
    output_formats: list[str] | None = None,
    sufixo_saida: str | None = None,
) -> list[Path]:
    """
    Converte uma lista de arquivos HTML de bookmarks para outros formatos.

    Args:
        lista_paths: lista de caminhos (Path) já validados.
        parser: Função que recebe um Path e retorna um DataFrame.
        output_formats: lista de extensões desejadas (ex: ['.csv', '.json']).
                        Se None, usa todas as definidas em WRITERS.
        sufixo_saida: String opcional adicionada ao nome base antes da extensão.

    Returns:
        lista com os Paths dos arquivos gerados.
    """
    if output_formats is None:
        output_formats = list(WRITERS.keys())

    arquivos_gerados: list[Path] = []

    for caminho_entrada in lista_paths:
        entrada = Path(caminho_entrada)
        logger.info("Processando: %s", entrada)

        try:
            df: DataFrame = parser(entrada)
        except (OSError, ValueError, AttributeError):
            logger.exception("  Erro ao parsear %s", entrada)
            continue

        if df.empty:
            logger.warning("  Aviso: DataFrame vazio, nenhum arquivo gerado para %s", entrada)
            continue

        diretorio: Path = entrada.parent
        stem: str = entrada.stem

        for ext in output_formats:
            if ext not in WRITERS:
                logger.warning("  Aviso: formato '%s' não possui escritor. Ignorado.", ext)
                continue

            nome_saida: str = f"{stem}{sufixo_saida}{ext}" if sufixo_saida else f"{stem}{ext}"
            caminho_saida: Path = diretorio / nome_saida
            writer: Callable[[DataFrame, Path], None] = WRITERS[ext]
            writer(df, caminho_saida)
            arquivos_gerados.append(caminho_saida)
            logger.info("  -> %s", caminho_saida)

    return arquivos_gerados


def adicionar_favicon_url(df: DataFrame, size: int = 32) -> DataFrame:
    """
    Adiciona uma coluna 'favicon_url' com links para favicons via Google S2.

    Args:
        df: DataFrame contendo a coluna 'url'.
        size: Tamanho desejado para o favicon (padrão 32).

    Returns:
        Novo DataFrame com a coluna 'favicon_url' adicionada.
    """

    def get_favicon(url: str) -> str:
        """Constrói a URL do favicon a partir do domínio do site."""
        with contextlib.suppress(Exception):
            domain = urlparse(url).netloc
            if domain:
                return f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"
        return "Icone nao encontrado"

    df = df.copy()
    df["favicon_url"] = df["url"].apply(get_favicon)
    return df
