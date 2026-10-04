"""Testes de caracterização do parser de favoritos Netscape."""

import pytest

from src.utils.parser import ParserBeautifulSoup


@pytest.mark.characterization
def test_dl_aninhado_sem_h3_mantem_favorito_na_pasta_atual() -> None:
    """Mantém em Favoritos o link de um dl aninhado sem h3 anterior."""
    html: str = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
    <TITLE>Bookmarks</TITLE>
    <H1>Bookmarks</H1>
    <DL><p>
        <DT><DL><p>
            <DT><A HREF="https://exemplo.com">Exemplo</A>
        </DL><p>
    </DL><p>
    """
    parser: ParserBeautifulSoup = ParserBeautifulSoup()

    favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

    assert favoritos == [
        {
            "titulo": "Exemplo",
            "url": "https://exemplo.com",
            "pasta": "Favoritos",
            "data_adicao": "Sem data",
        }
    ]
