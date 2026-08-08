"""
Caso de uso: descobrir arquivos HTML de bookmarks em uma pasta e
gerar um relatório de metadados (quantos itens, quantos links, erros).
"""

from __future__ import annotations

import logging
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from src.aplicacao.leitura import ler_arquivo_com_fallback, parsear_html
from src.dominio.arvore import contar_links, extrair_arvore
from src.dominio.entidades import BookmarkNode
from src.dominio.filtros import filtrar_pelo_nome, filtrar_por_caminhos_ocultos

logger: logging.Logger = logging.getLogger(name=__name__)


def buscar_arquivos_html(origem: Path) -> list[Path]:
    """
    Busca recursivamente por arquivos HTML cujo nome contenha
    'bookmark', 'favorito', etc., ignorando pastas ocultas.
    """
    pasta: Path = Path(origem).expanduser()
    return [
        arq
        for arq in pasta.rglob("*.html")
        if filtrar_por_caminhos_ocultos(caminho=arq) and filtrar_pelo_nome(caminho=arq)
    ]


def processar_arquivo(arquivo: Path) -> dict[str, str | int | None]:
    """
    Analisa um arquivo HTML de bookmarks e retorna metadados:
    nome, tamanho, status, quantidade de itens e links, etc.
    """
    meta: dict[str, str | int | None] = {
        "arquivo": str(arquivo),
        "nome": arquivo.name,
        "tamanho": int(arquivo.stat().st_size),
        "status": "erro",
        "erro": None,
        "itens_raiz": 0,
        "total_links": 0,
    }

    try:
        conteudo: str = ler_arquivo_com_fallback(caminho=arquivo)
        soup: BeautifulSoup = parsear_html(conteudo)
        raiz_tag: Tag | None = soup.find("dl")
        if not isinstance(raiz_tag, Tag):
            meta["erro"] = "Tag <DL> raiz não encontrada"
        else:
            arvore: list[BookmarkNode] = extrair_arvore(tag_dl=raiz_tag)
            meta["status"] = "sucesso"
            meta["itens_raiz"] = len(arvore)
            meta["total_links"] = sum(contar_links(n) for n in arvore)
            logger.info(
                "✅ %s: %d raiz, %d links",
                arquivo.name,
                meta["itens_raiz"],
                meta["total_links"],
            )
    except (OSError, UnicodeDecodeError) as e:
        meta["erro"] = str(e)
        logger.exception("❌ %s", arquivo.name)

    return meta


def gerar_relatorio(pasta_entrada: Path) -> list[dict[str, str | int | None]]:
    """Busca arquivos em `pasta_entrada` e gera relatório de metadados."""
    arquivos: list[Path] = buscar_arquivos_html(origem=pasta_entrada)
    logger.info("🔍 Encontrados %d arquivos.", len(arquivos))

    metadados: list[dict[str, str | int | None]] = [
        processar_arquivo(arquivo=arq) for arq in arquivos
    ]

    sucessos: list[dict[str, str | int | None]] = [m for m in metadados if m["status"] == "sucesso"]
    erros: list[dict[str, str | int | None]] = [m for m in metadados if m["status"] == "erro"]

    logger.info("Total: %d, Sucesso: %d, Erros: %d", len(metadados), len(sucessos), len(erros))
    if sucessos:
        total_links: int = sum(
            m["total_links"] for m in sucessos if isinstance(m["total_links"], int)
        )
        logger.info("Total de links extraídos: %d", total_links)

    return metadados
