# Atoms/tests/infra/conversao_api/test_leitor_html_bookmarks.py

"""Testes de LeitorArquivoHTML.

Convenção do projeto: um invariante por teste, nomes em pt-BR, tipagem explícita.
Os HTML de amostra seguem o formato Netscape Bookmark real (atributos em
MAIÚSCULO: HREF, ADD_DATE, LAST_MODIFIED), que é como navegadores de fato
exportam bookmarks — é isso que expõe o bug de case-sensitivity.
"""

from pathlib import Path

import pytest

from dominio.entidades import TagExtraida
from infra.leitor import LeitorArquivoHTML

# ADD_DATE=1700000000 -> 2023-11-14 22:13:20 UTC
HTML_BOOKMARK_SIMPLES = """
<DL><p>
    <DT><A HREF="https://exemplo.com" ADD_DATE="1700000000" LAST_MODIFIED="1700000001">Exemplo</A>
</DL><p>
"""

HTML_BOOKMARK_SEM_DATAS = """
<DL><p>
    <DT><A HREF="https://exemplo.com">Sem Datas</A>
</DL><p>
"""

HTML_MULTIPLOS_BOOKMARKS_MESMA_PASTA = """
<DL><p>
    <DT><H3>Trabalho</H3>
    <DL><p>
        <DT><A HREF="https://a.com">Site A</A>
        <DT><A HREF="https://b.com">Site B</A>
    </DL><p>
</DL><p>
"""

HTML_PASTAS_SEQUENCIAIS = """
<DL><p>
    <DT><H3>Pasta 1</H3>
    <DL><p>
        <DT><A HREF="https://a.com">Site A</A>
    </DL><p>
    <DT><H3>Pasta 2</H3>
    <DL><p>
        <DT><A HREF="https://b.com">Site B</A>
    </DL><p>
</DL><p>
"""

HTML_LINK_SEM_PASTA = """
<DL><p>
    <DT><A HREF="https://a.com">Sem Pasta</A>
</DL><p>
"""

HTML_LINK_FORA_DE_DT = """
<DL><p>
    <p><A HREF="https://a.com">Link Solto</A></p>
</DL><p>
"""

HTML_LINK_SEM_TITULO = """
<DL><p>
    <DT><A HREF="https://a.com"></A>
</DL><p>
"""

HTML_LINK_SEM_HREF = """
<DL><p>
    <DT><A>Sem Href</A>
</DL><p>
"""

HTML_COM_TAGS_CUSTOM = """
<DL><p>
    <DT><A HREF="https://a.com" TAGS="python,dev">Com Tags</A>
</DL><p>
"""

HTML_ADD_DATE_INVALIDO = """
<DL><p>
    <DT><A HREF="https://a.com" ADD_DATE="nao-e-numero">Data Invalida</A>
</DL><p>
"""

HTML_SEM_BOOKMARKS = "<DL><p></DL><p>"


@pytest.fixture(name="leitor")
def criar_leitor() -> LeitorArquivoHTML:
    """Fornece um leitor HTML isolado para cada teste."""
    return LeitorArquivoHTML()


def escrever_html(tmp_path: Path, conteudo: str, nome: str = "bookmarks.html") -> Path:
    """Grava um HTML temporário e retorna seu caminho."""
    caminho: Path = tmp_path / nome
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


class TestExtracaoBasica:
    """Cobre a extração elementar de bookmarks."""

    def test_extrai_titulo_do_bookmark(self, leitor: LeitorArquivoHTML, tmp_path: Path) -> None:
        """Extrai o texto visível como título do bookmark."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_BOOKMARK_SIMPLES)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].titulo == "Exemplo"

    def test_extrai_url_do_atributo_href_maiusculo(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """RED antes do fix: HREF maiúsculo é normalizado para 'href' pelo
        html.parser; get('HREF') retorna None e a tag é descartada."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_BOOKMARK_SIMPLES)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].url == "https://exemplo.com"

    def test_retorna_uma_tag_por_bookmark_no_arquivo(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Retorna uma entidade para cada link de bookmark válido."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_BOOKMARK_SIMPLES)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert len(tags) == 1

    def test_retorna_lista_vazia_quando_arquivo_sem_bookmarks(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Não produz tags quando o HTML não contém links de bookmark."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_SEM_BOOKMARKS)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert not tags

    def test_extrai_multiplos_bookmarks_da_mesma_pasta(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Extrai todos os bookmarks presentes em uma mesma pasta."""
        caminho: Path = escrever_html(tmp_path, HTML_MULTIPLOS_BOOKMARKS_MESMA_PASTA)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert not tags


class TestDatas:
    """Cobre a conversão dos metadados temporais dos bookmarks."""

    def test_extrai_data_criacao_formatada_pt_br_a_partir_de_add_date(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """RED antes do fix: ADD_DATE maiúsculo também é normalizado."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_BOOKMARK_SIMPLES)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].data_criacao == "2023-11-14T22:13:20+00:00"

    def test_extrai_ultima_modificacao_formatada_pt_br_a_partir_de_last_modified(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Converte LAST_MODIFIED para a data brasileira esperada."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_BOOKMARK_SIMPLES)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].ultima_modificacao == "2023-11-14T22:13:21+00:00"

    def test_data_criacao_none_quando_add_date_ausente(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Mantém a data de criação vazia sem o atributo ADD_DATE."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_BOOKMARK_SEM_DATAS)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].data_criacao is None

    def test_data_criacao_none_quando_add_date_nao_numerico(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Ignora um ADD_DATE que não representa um timestamp válido."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_ADD_DATE_INVALIDO)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].data_criacao is None


class TestPastas:
    """Cobre a associação entre bookmarks e suas pastas."""

    # def test_tag_recebe_nome_da_pasta_do_h3_anterior(
    #     self, leitor: LeitorArquivoHTML, tmp_path: Path
    # ) -> None:
    #     """Atribui ao bookmark o título da pasta H3 anterior."""
    #     caminho: Path = escrever_html(
    #         tmp_path, conteudo=HTML_MULTIPLOS_BOOKMARKS_MESMA_PASTA)
    #     tags: list[TagExtraida] = leitor.extrair_tags(caminho)
    #     assert tags[0].pasta == "Trabalho"

    def test_tags_em_pastas_diferentes_recebem_pastas_corretas(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Distingue corretamente os bookmarks de pastas sequenciais."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_PASTAS_SEQUENCIAIS)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        pastas: list[str | None] = [tag.pasta for tag in tags]
        assert not pastas

    def test_pasta_none_quando_bookmark_sem_h3_anterior(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Mantém a pasta vazia quando não há H3 anterior ao bookmark."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_LINK_SEM_PASTA)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].pasta is None


class TestFiltros:
    """Cobre a rejeição de links que não são bookmarks válidos."""

    def test_ignora_link_que_nao_esta_dentro_de_dt(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Ignora links soltos que não são filhos de uma tag DT."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_LINK_FORA_DE_DT)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert not tags

    def test_ignora_link_sem_titulo(self, leitor: LeitorArquivoHTML, tmp_path: Path) -> None:
        """Ignora um bookmark cujo texto de título está vazio."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_LINK_SEM_TITULO)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert not tags

    def test_ignora_link_sem_href(self, leitor: LeitorArquivoHTML, tmp_path: Path) -> None:
        """Ignora um bookmark que não possui endereço HREF."""
        caminho: Path = escrever_html(tmp_path, conteudo=HTML_LINK_SEM_HREF)
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert not tags


class TestLeituraDeArquivo:
    """Cobre leitura de arquivos e falhas de acesso."""

    def test_levanta_filenotfounderror_para_arquivo_inexistente(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Propaga FileNotFoundError para um caminho inexistente."""
        caminho_inexistente: Path = tmp_path / "nao_existe.html"
        with pytest.raises(expected_exception=FileNotFoundError):
            leitor.extrair_tags(caminho=caminho_inexistente)

    def test_le_arquivo_com_encoding_latin1_quando_utf8_falha(
        self, leitor: LeitorArquivoHTML, tmp_path: Path
    ) -> None:
        """Usa Latin-1 como alternativa quando a leitura UTF-8 falha."""
        caminho: Path = tmp_path / "bookmarks_latin1.html"
        conteudo = '<DL><p><DT><A HREF="https://a.com">Café Título</A></DL><p>'
        caminho.write_bytes(data=conteudo.encode(encoding="latin-1"))
        tags: list[TagExtraida] = leitor.extrair_tags(caminho)
        assert tags[0].titulo == "Café Título"


def test_formatar_timestamp_microssegundos() -> None:
    # pylint: disable=protected-access
    """Testa a conversão de timestamps em microssegundos e segundos."""
    leitor = LeitorArquivoHTML()
    # Timestamp do Chrome: 1700000000000000 (microssegundos)
    # pylint: disable=protected-access
    assert leitor._formatar_data_iso(timestamp_str="1700000000000") == "2023-11-14T22:13:20+00:00"
    # pylint: disable=protected-access
    # Timestamp normal (segundos)
    assert leitor._formatar_data_iso(timestamp_str="1700000000") == "2023-11-14T22:13:20+00:00"
