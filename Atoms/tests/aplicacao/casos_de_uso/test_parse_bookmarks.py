"""Testes do caso de uso de interpretação de bookmarks HTML (parse_bookmarks.py)."""

import pytest
from aplicacao.casos_de_uso.parse_bookmarks import parse_bookmarks_html
from dominio.entidades import TagA, VirtualFolder
from dominio.excecoes import ErroParseBookmarks

_HTML_SIMPLES = """
<DL><p>
    <DT><A HREF="https://a.com" ADD_DATE="100">Site A</A>
    <DT><A HREF="https://b.com" ADD_DATE="200">Site B</A>
</DL><p>
"""

_HTML_COM_PASTA_ANINHADA = """
<DL><p>
    <DT><A HREF="https://raiz.com">Raiz</A>
    <DT><H3 ADD_DATE="10">Trabalho</H3>
    <DL><p>
        <DT><A HREF="https://trabalho.com">No trabalho</A>
        <DT><H3>Subpasta</H3>
        <DL><p>
            <DT><A HREF="https://sub.com">Fundo do poço</A>
        </DL><p>
    </DL><p>
</DL><p>
"""


class TestParseBookmarksHtml:
    """Interpretação de um documento Netscape Bookmark File."""

    def test_extrai_favoritos_no_primeiro_nivel(self) -> None:
        """Favoritos diretamente na raiz devem virar TagA na ordem do HTML."""
        raiz: VirtualFolder = parse_bookmarks_html(conteudo_html=_HTML_SIMPLES)

        assert isinstance(raiz, VirtualFolder)
        assert raiz.nome == "Bookmarks"
        assert len(raiz.filhos_da_pasta) == 2
        assert all(isinstance(item, TagA) for item in raiz.filhos_da_pasta)

        titulos = []
        for item in raiz.filhos_da_pasta:
            assert isinstance(item, TagA)
            titulos.append(item.titulo)

        assert titulos == ["Site A", "Site B"]

    def test_preserva_atributos_do_favorito(self) -> None:
        """URL e data de adição devem ser extraídas corretamente da tag <A>."""
        raiz: VirtualFolder = parse_bookmarks_html(conteudo_html=_HTML_SIMPLES)

        primeiro = raiz.filhos_da_pasta[0]
        assert isinstance(primeiro, TagA)
        assert primeiro.url == "https://a.com"
        assert primeiro.data_adicao == "100"

    def test_reconhece_pastas_aninhadas_em_multiplos_niveis(self) -> None:
        """Uma <H3> com <DL> associado deve virar VirtualFolder com seus próprios filhos."""
        raiz: VirtualFolder = parse_bookmarks_html(conteudo_html=_HTML_COM_PASTA_ANINHADA)

        pasta_trabalho: VirtualFolder = next(item for item in raiz.filhos_da_pasta if isinstance(item, VirtualFolder))
        assert pasta_trabalho.nome == "Trabalho"

        subpasta: VirtualFolder = next(
            item for item in pasta_trabalho.filhos_da_pasta if isinstance(item, VirtualFolder)
        )
        assert subpasta.nome == "Subpasta"

        primeiro_filho = subpasta.filhos_da_pasta[0]
        assert isinstance(primeiro_filho, TagA)
        assert primeiro_filho.titulo == "Fundo do poço"

    def test_html_sem_dl_raiz_levanta_erro_parse(self) -> None:
        """Documento sem nenhuma <DL> deve levantar ErroParseBookmarks, não quebrar em silêncio."""
        with pytest.raises(expected_exception=ErroParseBookmarks, match="DL"):
            parse_bookmarks_html(conteudo_html="<html><body>sem bookmarks aqui</body></html>")

    def test_dl_vazia_retorna_pasta_raiz_sem_filhos(self) -> None:
        """Uma <DL> presente mas vazia deve gerar a pasta raiz sem levantar erro."""
        raiz: VirtualFolder = parse_bookmarks_html(conteudo_html="<DL><p></DL><p>")

        assert raiz.nome == "Bookmarks"
        assert not raiz.filhos_da_pasta
