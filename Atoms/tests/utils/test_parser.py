# Atoms/tests/utils/test_parser.py
# pylint: disable=protected-access,redefined-outer-name

"""Testes unitários para o parser de favoritos Netscape (utils.parser)."""

from collections.abc import Callable
from typing import Any

import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag

from src.utils.parser import ParserBeautifulSoup

# ===========================================================================
# Constantes dos testes
# ===========================================================================
TIMESTAMP_2021 = "1609459200"
TIMESTAMP_EPOCH = "0"
DATA_2021_UTC = "01/01/2021 00:00:00"
DATA_EPOCH_UTC = "01/01/1970 00:00:00"
PASTA_RAIZ = "Favoritos"
MSG_SEM_DATA = "Sem data"
MSG_DATA_INVALIDA = "Data inválida"
QTD_CHAVES_FAVORITO = 4
TAMANHO_HORA_HH_MM_SS = 3
TAMANHO_ANO_AAAA = 4
TAMANHO_MES_DIA_MM = 2


# ===========================================================================
# Fixtures
# ===========================================================================
@pytest.fixture
def parser() -> ParserBeautifulSoup:
    """Instância limpa do parser (a classe é stateless, mas exige instância)."""
    return ParserBeautifulSoup()


@pytest.fixture
def tag_a() -> Callable[[str], Tag]:
    """Factory que devolve um Tag <a> parseado a partir de HTML bruto."""

    def _criar(html: str) -> Tag:
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("a")
        assert isinstance(tag, Tag), f"HTML sem <a>: {html!r}"
        return tag

    return _criar


# ===========================================================================
# _coerce_atributo
# ===========================================================================
class TestCoerceAtributo:
    """Normalização de atributos HTML: só str passa; resto vira ''."""

    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            pytest.param("texto", "texto", id="string-simples"),
            pytest.param("", "", id="string-vazia"),
            pytest.param("  com espacos  ", "  com espacos  ", id="string-espacos"),
            pytest.param("ção/ç", "ção/ç", id="string-unicode"),
            pytest.param(None, "", id="none"),
            pytest.param(123, "", id="int"),
            pytest.param(3.14, "", id="float"),
            pytest.param(True, "", id="bool"),
            pytest.param(["a", "b"], "", id="lista"),
            pytest.param(("a",), "", id="tupla"),
            pytest.param({"k": "v"}, "", id="dict"),
            pytest.param(b"bytes", "", id="bytes"),
        ],
    )
    def test_normaliza_apenas_string(self, entrada: object, esperado: str) -> None:
        """Só aceita ``str``; qualquer outro tipo é convertido em string vazia."""
        assert ParserBeautifulSoup._coerce_atributo(entrada) == esperado


# ===========================================================================
# _converter_timestamp
# ===========================================================================
class TestConverterTimestamp:
    """Conversão de timestamps Unix para data formatada pt-BR em UTC."""

    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            pytest.param(TIMESTAMP_2021, DATA_2021_UTC, id="timestamp-2021"),
            pytest.param(TIMESTAMP_EPOCH, DATA_EPOCH_UTC, id="epoch-zero"),
            pytest.param("", MSG_SEM_DATA, id="string-vazia"),
            pytest.param("abc", MSG_DATA_INVALIDA, id="nao-numerico"),
            pytest.param("12a", MSG_DATA_INVALIDA, id="alfanumerico"),
            pytest.param("10.5", MSG_DATA_INVALIDA, id="float-como-string"),
            pytest.param("12,5", MSG_DATA_INVALIDA, id="virgula-decimal"),
        ],
    )
    def test_converte_ou_retorna_mensagem(self, entrada: str, esperado: str) -> None:
        """Converte timestamps válidos e devolve mensagem amigável nos inválidos."""
        assert ParserBeautifulSoup._converter_timestamp(entrada) == esperado

    def test_formato_e_dd_mm_aaaa_hh_mm_ss(self) -> None:
        """Garante o layout exato ``DD/MM/AAAA HH:MM:SS`` na saída."""
        resultado = ParserBeautifulSoup._converter_timestamp(TIMESTAMP_2021)
        dia, hora = resultado.split(" ")
        d, m, a = dia.split("/")

        assert (len(d), len(m), len(a)) == (
            TAMANHO_MES_DIA_MM,
            TAMANHO_MES_DIA_MM,
            TAMANHO_ANO_AAAA,
        )
        assert len(hora.split(":")) == TAMANHO_HORA_HH_MM_SS


# ===========================================================================
# _criar_favorito
# ===========================================================================
class TestCriarFavorito:
    """Construção do dict de favorito a partir de um Tag <a>."""

    def test_estrutura_completa(self, tag_a: Callable[[str], Tag]) -> None:
        """Monta o dict completo a partir de um ``<a>`` com todos os atributos."""
        tag = tag_a('<a href="https://exemplo.com" add_date="1609459200">Exemplo</a>')

        favorito = ParserBeautifulSoup._criar_favorito(tag, pilha_pastas=[])

        assert favorito == {
            "titulo": "Exemplo",
            "url": "https://exemplo.com",
            "pasta": PASTA_RAIZ,
            "data_adicao": DATA_2021_UTC,
        }

    def test_com_pilha_de_pastas(self, tag_a: Callable[[str], Tag]) -> None:
        """Junta os níveis da pilha com `` / `` no campo ``pasta``."""
        tag: Tag = tag_a('<a href="https://x.com">X</a>')

        favorito: dict[str, str] | None = ParserBeautifulSoup._criar_favorito(
            tag, pilha_pastas=["Pessoal", "Música"]
        )

        assert favorito is not None
        assert favorito["pasta"] == "Pessoal / Música"

    def test_href_ausente_vira_string_vazia(self, tag_a: Callable[[str], Tag]) -> None:
        """Sem ``href`` no ``<a>``, o campo ``url`` fica vazio."""
        favorito: dict[str, str] = self._extrair_retorno_com_apenas_quatro_chaves(
            tag_a, mock_tag='<a add_date="1609459200">X</a>'
        )
        assert favorito["url"] == ""

    def test_add_date_ausente_vira_sem_data(self, tag_a: Callable[[str], Tag]) -> None:
        """Sem ``add_date``, o campo ``data_adicao`` recebe ``Sem data``."""
        favorito: dict[str, str] = self._extrair_retorno_com_apenas_quatro_chaves(
            tag_a, mock_tag='<a href="https://x.com">X</a>'
        )
        assert favorito["data_adicao"] == MSG_SEM_DATA

    def test_add_date_invalido_vira_data_invalida(self, tag_a: Callable[[str], Tag]) -> None:
        """``add_date`` não numérico é sinalizado como ``Data inválida``."""
        favorito: dict[str, str] = self._extrair_retorno_com_apenas_quatro_chaves(
            tag_a, mock_tag='<a href="https://x.com" add_date="nao-e-data">X</a>'
        )
        assert favorito["data_adicao"] == MSG_DATA_INVALIDA

    def test_titulo_com_espacos_e_trimado(self, tag_a: Callable[[str], Tag]) -> None:
        """Remove espaços em branco das extremidades do título."""
        favorito: dict[str, str] = self._extrair_retorno_com_apenas_quatro_chaves(
            tag_a, mock_tag='<a href="https://x.com">   Título   </a>'
        )
        assert favorito["titulo"] == "Título"

    def test_link_sem_texto_gera_titulo_vazio(self, tag_a: Callable[[str], Tag]) -> None:
        """``<a>`` sem conteúdo textual produz ``titulo`` vazio."""
        favorito: dict[str, str] = self._extrair_retorno_com_apenas_quatro_chaves(
            tag_a, mock_tag='<a href="https://x.com"></a>'
        )
        assert favorito["titulo"] == ""

    def test_retorno_tem_apenas_quatro_chaves(self, tag_a: Callable[[str], Tag]) -> None:
        """Congela o contrato: exatamente as 4 chaves esperadas no dict."""
        favorito: dict[str, str] = self._extrair_retorno_com_apenas_quatro_chaves(
            tag_a, mock_tag='<a href="https://x.com">X</a>'
        )
        assert len(favorito) == QTD_CHAVES_FAVORITO
        assert set(favorito.keys()) == {
            "titulo",
            "url",
            "pasta",
            "data_adicao",
        }

    def _extrair_retorno_com_apenas_quatro_chaves(
        self, tag_a: Callable[[Any], Any], mock_tag: Any
    ) -> dict[str, str]:
        """Helper: chama ``_criar_favorito`` e afirma que o retorno não é ``None``."""
        tag = tag_a(mock_tag)
        result: dict[str, str] | None = ParserBeautifulSoup._criar_favorito(
            link=tag, pilha_pastas=[]
        )
        assert result is not None
        return result


# ===========================================================================
# extrair_favoritos — API pública
# ===========================================================================
class TestExtrairFavoritosVazio:
    """Casos sem nenhum favorito extraível."""

    def test_html_vazio(self, parser: ParserBeautifulSoup) -> None:
        """HTML vazio devolve lista vazia."""
        assert parser.extrair_favoritos(html_conteudo="") == []

    def test_html_sem_links(self, parser: ParserBeautifulSoup) -> None:
        """HTML sem ``<a>`` devolve lista vazia."""
        html = "<html><body><p>Nada aqui</p></body></html>"
        assert parser.extrair_favoritos(html_conteudo=html) == []

    def test_html_com_apenas_h3(self, parser: ParserBeautifulSoup) -> None:
        """Pasta sem links dentro não gera entradas."""
        html = "<dl><h3>Pasta sem links</h3></dl>"
        assert parser.extrair_favoritos(html_conteudo=html) == []


class TestExtrairFavoritosEstrutura:
    """Estrutura do retorno: pasta raiz, uma pasta, pastas aninhadas.

    Observação: o parser espera que <h3> e <dl> sejam irmãos dentro do mesmo
    nó pai. Esse é o formato usado nos testes abaixo.
    """

    def test_link_sem_pasta_usa_favoritos(self, parser: ParserBeautifulSoup) -> None:
        """Link fora de qualquer ``<h3>`` cai na pasta raiz ``Favoritos``."""
        html = """
        <dl>
            <dt><a href="https://exemplo.com" add_date="1609459200">Exemplo</a></dt>
        </dl>
        """

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert favoritos == [
            {
                "titulo": "Exemplo",
                "url": "https://exemplo.com",
                "pasta": PASTA_RAIZ,
                "data_adicao": DATA_2021_UTC,
            }
        ]

    def test_link_dentro_de_uma_pasta(self, parser: ParserBeautifulSoup) -> None:
        """Link sob um único ``<h3>`` recebe o nome dessa pasta."""
        html = """
        <dl>
            <h3>Trabalho</h3>
            <dl>
                <dt><a href="https://trabalho.com">T</a></dt>
            </dl>
        </dl>
        """

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert len(favoritos) == 1
        assert favoritos[0]["pasta"] == "Trabalho"

    def test_pastas_aninhadas_formam_caminho(self, parser: ParserBeautifulSoup) -> None:
        """Pastas aninhadas são concatenadas com `` / ``."""
        html = """
        <dl>
            <h3>Pessoal</h3>
            <dl>
                <h3>Música</h3>
                <dl>
                    <dt><a href="https://b.com">B</a></dt>
                </dl>
            </dl>
        </dl>
        """

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert len(favoritos) == 1
        assert favoritos[0]["pasta"] == "Pessoal / Música"

    def test_multiplas_pastas_irmas(self, parser: ParserBeautifulSoup) -> None:
        """Pastas irmãs são tratadas independentemente."""
        html = """
        <dl>
            <h3>A</h3>
            <dl>
                <dt><a href="https://a1.com">A1</a></dt>
                <dt><a href="https://a2.com">A2</a></dt>
            </dl>
            <h3>B</h3>
            <dl>
                <dt><a href="https://b1.com">B1</a></dt>
            </dl>
        </dl>
        """

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        pastas: list[tuple[str, str]] = [(f["url"], f["pasta"]) for f in favoritos]
        assert pastas == [
            ("https://a1.com", "A"),
            ("https://a2.com", "A"),
            ("https://b1.com", "B"),
        ]


class TestExtrairFavoritosPreservacao:
    """Ordem, integridade e tolerância a dados faltantes/inválidos."""

    def test_preserva_ordem_de_aparicao(self, parser: ParserBeautifulSoup) -> None:
        """Favoritos saem na mesma ordem em que aparecem no HTML."""
        html = """
        <dl>
            <dt><a href="https://primeiro.com">1</a></dt>
            <dt><a href="https://segundo.com">2</a></dt>
            <dt><a href="https://terceiro.com">3</a></dt>
        </dl>
        """

        urls: list[str] = [f["url"] for f in parser.extrair_favoritos(html_conteudo=html)]

        assert urls == [
            "https://primeiro.com",
            "https://segundo.com",
            "https://terceiro.com",
        ]

    def test_ignora_nos_de_texto_soltos(self, parser: ParserBeautifulSoup) -> None:
        """Texto solto entre tags não vira favorito nem quebra o parsing."""
        html = """
        <dl>
            texto solto entre tags
            <dt><a href="https://x.com">X</a></dt>
            mais texto solto
        </dl>
        """

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert len(favoritos) == 1
        assert favoritos[0]["titulo"] == "X"

    def test_atributos_ausentes_sao_tolerados(self, parser: ParserBeautifulSoup) -> None:
        """``<a>`` sem ``href``/``add_date`` produz entradas com defaults."""
        html = "<dl><dt><a>Sem nada</a></dt></dl>"

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert favoritos == [
            {
                "titulo": "Sem nada",
                "url": "",
                "pasta": PASTA_RAIZ,
                "data_adicao": MSG_SEM_DATA,
            }
        ]

    def test_atributos_invalidos_nao_quebram(self, parser: ParserBeautifulSoup) -> None:
        """``add_date`` inválido não interrompe a extração."""
        html = '<dl><dt><a href="https://x.com" add_date="abc">X</a></dt></dl>'

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert favoritos[0]["data_adicao"] == MSG_DATA_INVALIDA


class TestExtrairFavoritosNetscape:
    """Snippets com <p> intercalado, como em exports de navegadores."""

    def test_estrutura_com_p_intercalado(self, parser: ParserBeautifulSoup) -> None:
        """O ``<p>`` herdado do formato Netscape não afeta a extração."""
        html = """
        <DL><p>
            <DT><A HREF="https://x.com" ADD_DATE="1609459200">X</A>
        </DL><p>
        """

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert len(favoritos) == 1
        assert favoritos[0]["url"] == "https://x.com"
        assert favoritos[0]["pasta"] == PASTA_RAIZ

    def test_cabecalho_netscape_e_ignorado(self, parser: ParserBeautifulSoup) -> None:
        """Cabeçalho ``NETSCAPE-Bookmark-file-1`` é ignorado silenciosamente."""
        html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
        <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
        <TITLE>Bookmarks</TITLE>
        <H1>Bookmarks</H1>
        <DL><p>
            <DT><A HREF="https://x.com">X</A>
        </DL><p>
        """

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert len(favoritos) == 1
        assert favoritos[0]["titulo"] == "X"

    def test_case_insensitive_em_tag_e_atributo(self, parser: ParserBeautifulSoup) -> None:
        """Tags/atributos em maiúsculas são normalizados pelo BeautifulSoup."""
        html = '<DL><DT><A HREF="https://x.com" ADD_DATE="1609459200">X</A></DL>'

        favoritos: list[dict[str, str]] = parser.extrair_favoritos(html_conteudo=html)

        assert favoritos[0]["url"] == "https://x.com"
        assert favoritos[0]["data_adicao"] == DATA_2021_UTC


# ===========================================================================
# Contrato do módulo
# ===========================================================================
class TestContratoDoModulo:
    """Congela a superfície pública do parser."""

    def test_metodo_publico_existe(self) -> None:
        """``extrair_favoritos`` existe e é chamável."""
        assert callable(ParserBeautifulSoup.extrair_favoritos)

    def test_helpers_sao_estaticos_ou_classmethod(self) -> None:
        """Os helpers privados mantêm o tipo de método esperado."""
        assert isinstance(ParserBeautifulSoup.__dict__["_coerce_atributo"], staticmethod)
        assert isinstance(ParserBeautifulSoup.__dict__["_converter_timestamp"], staticmethod)
        assert isinstance(ParserBeautifulSoup.__dict__["_criar_favorito"], classmethod)

    def test_pode_ser_instanciado(self) -> None:
        """A classe é instanciável sem argumentos."""
        assert ParserBeautifulSoup() is not None
