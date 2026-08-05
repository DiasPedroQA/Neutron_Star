"""Leitura de arquivos de bookmarks em disco (I/O)."""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup, Tag

# 'html5lib' é obrigatório aqui: arquivos reais de bookmarks (Netscape
# Bookmark File) não fecham as tags <p>/<DT>, e apenas um parser que
# segue as regras de auto-fechamento do HTML5 reconstrói a árvore
# corretamente (ver src.dominio.arvore.extrair_arvore).
PARSER_HTML: str = "html5lib"


def ler_arquivo_com_fallback(caminho: Path) -> str:
    """Lê um arquivo tentando vários encodings comuns."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(file=caminho, encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Não foi possível decodificar o arquivo: {caminho}")


def parsear_html(conteudo: str) -> BeautifulSoup:
    """Ponto único de escolha do parser HTML para todo o pacote."""
    return BeautifulSoup(conteudo, PARSER_HTML)


def raiz_bookmarks(soup: BeautifulSoup) -> Tag | None:
    """Localiza a tag <DL> raiz, preferindo a que vem depois de um <H1>."""
    h1: Tag | None = soup.find(name="h1")
    if h1 is not None:
        return h1.find_next(name="dl") or soup.find(name="dl")
    return soup.find(name="dl")
