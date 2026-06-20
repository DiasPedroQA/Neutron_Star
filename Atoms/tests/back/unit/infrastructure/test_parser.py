# Atoms/tests/back/unit/infrastructure/test_parser.py

"""Testes para o analisador de favoritos (TagsFinder / AnalisadorTags)."""

from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
import pytest

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.infrastructure.controllers.parser import AnalisadorTags


HTML_EXEMPLO = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><A HREF="https://www.google.com" ADD_DATE="1672531200">Google</A>
    <DT><A HREF="https://www.example.com" ADD_DATE="invalid">Example</A>
    <DT><A HREF="http://localhost:8080">Localhost</A>
    <DT><A HREF="ftp://bad.com">Bad scheme</A>
</DL><p>
"""


@pytest.fixture
def parser() -> AnalisadorTags:
    """Cria uma instância do analisador de tags para uso nos testes.
    Fornece um objeto AnalisadorTags compartilhado entre os casos de teste que o utilizam."""
    return AnalisadorTags()


@pytest.fixture
def arquivo_html(tmp_path: Path) -> ModeloArquivo:
    """Cria um arquivo HTML temporário de bookmarks para os testes.
    Fornece um ModeloArquivo apontando para o conteúdo HTML de exemplo gravado em disco."""
    p: Path = tmp_path / "bookmarks.html"
    p.write_text(data=HTML_EXEMPLO, encoding="utf-8")
    return ModeloArquivo(
        nome_arquivo="bookmarks.html",
        caminho_arquivo=p,
        eh_html=True,
    )


class TestAnalisadorTags:
    """Testes para o comportamento do AnalisadorTags ao processar arquivos de favoritos.
    Verifica o suporte a diferentes extensões, a extração correta de favoritos e o tratamento de erros e aliases na API."""

    def test_suporta_arquivo_html(
        self, parser: AnalisadorTags, arquivo_html: ModeloArquivo
    ) -> None:
        """Testa o suporte do analisador para arquivos HTML de favoritos.
        Garante que um ModeloArquivo representando um HTML válido é reconhecido como suportado."""
        assert parser.suporta_arquivo(arquivo=arquivo_html) is True

    def test_suporta_arquivo_htm(self, parser: AnalisadorTags, tmp_path: Path) -> None:
        """Testa o suporte do analisador para arquivos com extensão .htm.
        Garante que arquivos HTM sejam reconhecidos como suportados mesmo sem a flag explícita de HTML."""
        arq = ModeloArquivo(
            nome_arquivo="f.htm",
            caminho_arquivo=tmp_path / "f.htm",
            eh_html=False,
        )
        assert parser.suporta_arquivo(arquivo=arq) is True

    def test_analisar_arquivo_extrai_favoritos(
        self, parser: AnalisadorTags, arquivo_html: ModeloArquivo
    ) -> None:
        """Testa a extração de favoritos a partir de um arquivo HTML suportado.
        Verifica se apenas links válidos são convertidos em Favorito e se os campos essenciais são populados corretamente."""
        favoritos: list[Favorito] = parser.analisar_arquivo(arquivo=arquivo_html)
        assert len(favoritos) == 3  # ftp é ignorado
        assert favoritos[0].titulo == "Google"
        assert favoritos[0].url == "https://www.google.com"
        # data 1672531200 = 2023-01-01 00:00:00 UTC
        assert favoritos[0].data_adicao == datetime(
            year=2023, month=1, day=1, tzinfo=timezone.utc
        )

    def test_arquivo_inexistente_retorna_vazio(
        self, parser: AnalisadorTags, tmp_path: Path
    ) -> None:
        """Testa o comportamento do analisador quando o arquivo de entrada não existe.
        Verifica se, nessa situação, a lista de favoritos retornada é vazia."""
        arq = ModeloArquivo(
            nome_arquivo="inexistente.html",
            caminho_arquivo=tmp_path / "inexistente.html",
            eh_html=True,
        )
        assert parser.analisar_arquivo(arquivo=arq) == []

    def test_alias_parse_file(
        self, parser: AnalisadorTags, arquivo_html: ModeloArquivo
    ) -> None:
        """Testa o alias parse_file como atalho para analisar arquivos de favoritos.
        Verifica se o método alternativo retorna a mesma quantidade esperada de favoritos extraídos."""
        favoritos: list[Favorito] = parser.parse_file(arquivo_atual=arquivo_html)
        assert len(favoritos) == 3

    def test_alias_parse_bookmark_tag(
        self, parser: AnalisadorTags, arquivo_html: ModeloArquivo
    ) -> None:
        """Testa o alias interno que converte uma tag de bookmark em um objeto Favorito.
        Verifica se a primeira âncora válida do HTML de exemplo é parseada corretamente com o título esperado."""
        print(f"Teste independente do arquivo {arquivo_html}")
        sopa = BeautifulSoup(markup=HTML_EXEMPLO, features="lxml")
        tag: Tag | NavigableString | None = sopa.find(name="a")
        if isinstance(tag, Tag):
            fav: Favorito | None = parser._parse_bookmark_tag(tag=tag)
            assert fav is not None
            assert fav.titulo == "Google"
