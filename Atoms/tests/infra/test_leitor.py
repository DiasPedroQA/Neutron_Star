# pylint: disable=protected-access
"""Testes para o LeitorArquivoHTML."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup, Tag

from dominio.entidades import TagExtraida
from infra.leitor import LeitorArquivoHTML


# ------------------------ Fixtures ------------------------
@pytest.fixture
def leitor_fixture() -> LeitorArquivoHTML:
    """Retorna uma instância do leitor."""
    return LeitorArquivoHTML()


@pytest.fixture
def arquivo_exemplo(tmp_path: Path) -> Path:
    """
    Cria um arquivo HTML de bookmarks (formato Netscape) em um diretório temporário.
    Retorna o caminho do arquivo.
    """
    conteudo = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
        <HTML>
        <HEAD>
        <TITLE>Bookmarks</TITLE>
        </HEAD>
        <BODY>
        <H1>Bookmarks</H1>
        <DL><p>
            <DT><H3 ADD_DATE="1609459200" LAST_MODIFIED="1609545600" PERSONAL_TOOLBAR_FOLDER="true">Barra de Ferramentas</H3>
            <DL><p>
                <DT><A HREF="https://www.google.com/" ADD_DATE="1609459200" LAST_MODIFIED="1609545600" TAGS="pesquisa,google">Google</A>
                <DT><A HREF="https://github.com/" ADD_DATE="1609459200" LAST_MODIFIED="1609545600">GitHub</A>
            </DL><p>
            <DT><H3 ADD_DATE="1609459200">Projetos</H3>
            <DL><p>
                <DT><A HREF="https://fastapi.tiangolo.com/" ADD_DATE="1609459200" LAST_MODIFIED="1609545600" TAGS="python,api">FastAPI Docs</A>
            </DL><p>
            <DT><A HREF="https://example.com/" ADD_DATE="1609459200">Exemplo sem pasta</A>
        </DL><p>
        </BODY>
        </HTML>
    """
    arquivo: Path = tmp_path / "bookmarks.html"
    arquivo.write_text(data=conteudo, encoding="utf-8")
    return arquivo


@pytest.fixture
def arquivo_microssegundos(tmp_path: Path) -> Path:
    """Arquivo com timestamps em microssegundos (13 dígitos)."""
    conteudo = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
        <HTML>
        <BODY>
        <DL><p>
            <DT><A HREF="https://example.com/" ADD_DATE="1700000000000" LAST_MODIFIED="1700000001000">Link com micro</A>
        </DL><p>
        </BODY>
        </HTML>
    """
    arquivo: Path = tmp_path / "micro_bookmarks.html"
    arquivo.write_text(data=conteudo, encoding="utf-8")
    return arquivo


@pytest.fixture
def arquivo_latin1(tmp_path: Path) -> Path:
    """Arquivo com encoding Latin-1 (não UTF-8)."""
    conteudo_latin1 = b"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
        <HTML>
        <BODY>
        <DL><p>
            <DT><A HREF="https://example.com/" ADD_DATE="1609459200">P\xe1gina de exemplo</A>
        </DL><p>
        </BODY>
        </HTML>
    """
    arquivo: Path = tmp_path / "latin1_bookmarks.html"
    arquivo.write_bytes(data=conteudo_latin1)
    return arquivo


# ------------------------ Testes ------------------------
def test_extrair_tags_com_estrutura_valida(
    leitor_fixture: LeitorArquivoHTML, arquivo_exemplo: Path
) -> None:
    """Deve extrair corretamente as tags de um arquivo HTML válido."""
    tags: list[TagExtraida] = leitor_fixture.extrair_tags(
        caminho=arquivo_exemplo)

    assert len(tags) == 4

    # Google
    assert tags[0].titulo == "Google"
    assert tags[0].url == "https://www.google.com/"
    assert tags[0].pasta == "Barra de Ferramentas"
    assert tags[0].data_criacao == "2021-01-01T00:00:00+00:00"
    assert tags[0].ultima_modificacao == "2021-01-02T00:00:00+00:00"

    # Exemplo sem pasta
    assert tags[3].titulo == "Exemplo sem pasta"
    assert tags[3].url == "https://example.com/"
    assert tags[3].pasta == "Projetos"


def test_extrair_tags_arquivo_inexistente(leitor_fixture: LeitorArquivoHTML) -> None:
    """Deve levantar FileNotFoundError quando o arquivo não existe."""
    caminho_inexistente = Path("/tmp/nao_existe.html")
    with pytest.raises(
        expected_exception=FileNotFoundError, match="Arquivo não encontrado"
    ):
        leitor_fixture.extrair_tags(caminho=caminho_inexistente)


def test_formatar_timestamp_microssegundos(
    leitor_fixture: LeitorArquivoHTML, arquivo_microssegundos: Path
) -> None:
    """Deve converter timestamps em microssegundos corretamente."""
    tags: list[TagExtraida] = leitor_fixture.extrair_tags(
        caminho=arquivo_microssegundos
    )
    assert len(tags) == 1
    # 1700000000000 microssegundos = 1700000000 segundos → 1970-01-20T16:13:20+00:00
    esperado_criacao = "2023-11-14T22:13:20+00:00"
    esperado_modificacao = "2023-11-14T22:13:21+00:00"
    assert tags[0].data_criacao == esperado_criacao
    assert tags[0].ultima_modificacao == esperado_modificacao


def test_fallback_encoding_latin1(
    leitor_fixture: LeitorArquivoHTML, arquivo_latin1: Path
) -> None:
    """Deve conseguir ler arquivo com encoding Latin-1 (fallback)."""
    tags: list[TagExtraida] = leitor_fixture.extrair_tags(
        caminho=arquivo_latin1)
    assert len(tags) == 1
    # 'á' interpretado corretamente
    assert tags[0].titulo == "Página de exemplo"


def test_extrair_atributo_quando_ausente(leitor_fixture: LeitorArquivoHTML) -> None:
    """O método _extrair_atributo deve retornar None para atributo inexistente."""
    soup = BeautifulSoup('<a href="x">Link</a>', "html.parser")
    elemento: Tag | None = soup.find("a")
    if elemento is not None:
        assert leitor_fixture._extrair_atributo(elemento, "add_date") is None
        assert leitor_fixture._extrair_atributo(elemento, "href") == "x"


def test_is_bookmark_link(leitor_fixture: LeitorArquivoHTML) -> None:
    """Deve identificar corretamente se o <a> está dentro de <dt>."""
    soup1 = BeautifulSoup(
        markup='<dl><dt><a href="x">Link</a></dt></dl>', features="html.parser"
    )
    link1: Tag | None = soup1.find("a")
    if link1 is not None:
        assert leitor_fixture._is_bookmark_link(elemento=link1) is True

    soup2 = BeautifulSoup('<a href="x">Link solto</a>', "html.parser")
    link2: Tag | None = soup2.find("a")
    if link2 is not None:
        assert leitor_fixture._is_bookmark_link(elemento=link2) is False
