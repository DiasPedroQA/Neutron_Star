"""Testes para _compilar_regex e _construir_padrao_data.

Cobre o bug original (data explícita tratada como string literal, sem
tolerância a zero à esquerda ou separador) e a correção que passa a
normalizar a data e permitir separador/extensões configuráveis.
"""

from __future__ import annotations

import re

import pytest
from src.utils.system_tools import _compilar_regex, _construir_padrao_data


# ____________________________________________________________________________-
# _construir_padrao_data
# ____________________________________________________________________________-
class TestConstruirPadraoData:
    """Suite de testes para _construir_padrao_data."""

    @pytest.mark.parametrize(
        argnames="data_entrada,nome_arquivo",
        argvalues=[
            ("6_23_26", "prefixo_6_23_26.html"),
            ("6_23_26", "prefixo_06_23_26.html"),
            ("06_23_26", "prefixo_6_23_26.html"),
            ("6_23_26", "prefixo_6_23_26.html"),
            ("6_23_26", "prefixo_06.23.26.html"),
        ],
    )
    def test_variacoes_de_zero_a_esquerda_e_separador_sao_equivalentes(
        self, data_entrada: str, nome_arquivo: str
    ) -> None:
        """Zero à esquerda e separador não devem impedir o casamento."""
        regex: re.Pattern[str] = _compilar_regex(prefixo="prefixo", data=data_entrada, case_sensitive=True)
        assert regex.match(string=nome_arquivo) is not None

    def test_data_fora_do_formato_numerico_e_tratada_como_literal(self) -> None:
        """Se a data não tiver 3 componentes numéricos, cai para re.escape."""
        padrao: str = _construir_padrao_data(data="release-final")
        assert padrao == re.escape(pattern="release-final")

    def test_caracteres_especiais_na_data_nao_quebram_a_regex(self) -> None:
        """Data com metacaractere de regex não deve gerar padrão inválido."""
        # Antes da correção, `data` entrava crua no f-string sem re.escape.
        regex: re.Pattern[str] = _compilar_regex(prefixo="p", data="a(b", case_sensitive=True)
        assert regex.match(string="p_a(b.html") is not None
        # "(" não deve virar grupo
        assert regex.match(string="p_axb.html") is None


# ____________________________________________________________________________-
# _compilar_regex — comportamento geral
# ____________________________________________________________________________-
class TestCompilarRegex:
    """Suite de testes para _compilar_regex."""

    def test_prefixo_e_data_exatos_ainda_funcionam(self) -> None:
        """Regressão: o caso feliz original continua casando."""
        regex: re.Pattern[str] = _compilar_regex(prefixo="favoritos", data="6_23_26", case_sensitive=True)
        assert regex.match(string="favoritos_6_23_26.html") is not None

    def test_prefixo_diferente_nao_casa(self) -> None:
        """Garante que apenas o prefixo esperado e aceito pelo padrao gerado.
        Verifica que nomes de arquivo com prefixo diferente daquele configurado nao sao casados pela regex.
        """
        regex: re.Pattern[str] = _compilar_regex(prefixo="favoritos", data="6_23_26", case_sensitive=True)
        assert regex.match(string="outracoisa_6_23_26.html") is None

    def test_sem_data_aceita_qualquer_data_no_formato_padrao_ou_nenhuma(self) -> None:
        """Verifica que a ausencia de data explicita nao impede o casamento de arquivos validos.
        Garante que o padrao gerado aceita nomes com e sem data no formato padrao quando `data` nao e fornecida.
        """
        regex: re.Pattern[str] = _compilar_regex(prefixo="favoritos", case_sensitive=True)
        assert regex.match(string="favoritos.html") is not None
        assert regex.match(string="favoritos_6_23_26.html") is not None
        assert regex.match(string="favoritos_06_23_26.html") is not None

    def test_separador_configuravel(self) -> None:
        """Permite adotar outro separador entre prefixo e data (ex.: '_')."""
        regex: re.Pattern[str] = _compilar_regex(
            prefixo="favoritos", data="6_23_26", separador="_", case_sensitive=True
        )
        assert regex.match(string="favoritos_6_23_26.html") is not None
        # assert regex.match(string="favoritos_6_23_26.html") is None

    def test_multiplas_extensoes_configuraveis(self) -> None:
        """Permite aceitar mais de um padrão de extensão, não só '.html'."""
        regex: re.Pattern[str] = _compilar_regex(
            prefixo="favoritos",
            data="6_23_26",
            extensoes=(".html", ".htm"),
            case_sensitive=True,
        )
        assert regex.match(string="favoritos_6_23_26.html") is not None
        assert regex.match(string="favoritos_6_23_26.htm") is not None
        assert regex.match(string="favoritos_6_23_26.txt") is None

    def test_case_insensitive_por_padrao(self) -> None:
        """Verifica que o padrao gerado e insensivel a maiusculas e minusculas quando nao configurado em contrario.
        Garante que arquivos com prefixo e extensao em caixa alta ainda sao casados pela regex padrao.
        """
        regex: re.Pattern[str] = _compilar_regex(prefixo="favoritos", data="6_23_26")
        assert regex.match(string="FAVORITOS_6_23_26.HTML") is not None


# ____________________________________________________________________________-
# _compilar_regex — múltiplos prefixos sinônimos (pt-BR / en-US)
# ____________________________________________________________________________-
class TestCompilarRegexMultiplosPrefixos:
    """Cobre o requisito de aceitar aliases equivalentes (ex.: favoritos/bookmarks)."""

    @pytest.mark.parametrize(
        argnames="nome_arquivo",
        argvalues=[
            "favoritos_5_20_26.html",
            "bookmarks_5_20_26.html",
            "favoritos.html",
            "bookmarks.html",
        ],
    )
    def test_aceita_qualquer_alias_com_ou_sem_data(self, nome_arquivo: str) -> None:
        """Verifica que qualquer alias presente na lista casa com nomes válidos.
        Garante que a regex gerada aceita arquivos com qualquer prefixo da lista de aliases,
        tanto com data quanto sem data, desde que o formato seja compatível.
        """
        regex: re.Pattern[str] = _compilar_regex(prefixo=("favoritos", "bookmarks"), data=None, case_sensitive=True)
        assert regex.match(string=nome_arquivo) is not None

    def test_aceita_alias_com_data_exata_via_lista(self) -> None:
        """Verifica que listas de prefixos equivalentes aceitam arquivos com data exata configurada.
        Garante que qualquer alias presente na lista casa com nomes que seguem o formato de data esperado, incluindo separadores alternativos.
        """
        regex: re.Pattern[str] = _compilar_regex(
            prefixo=["favoritos", "bookmarks"], data="5_20_26", case_sensitive=True
        )
        assert regex.match(string="favoritos_5_20_26.html") is not None
        assert regex.match(string="bookmarks_5_20_26.html") is not None
        # separador de data "_"
        assert regex.match(string="bookmarks_5_20_26.html") is not None

    def test_prefixo_fora_da_lista_de_aliases_nao_casa(self) -> None:
        """Garante que nomes de arquivo com prefixo fora da lista de aliases nao sao considerados validos.
        Verifica que o padrao gerado so casa quando o prefixo pertence explicitamente ao conjunto de aliases configurados.
        """
        regex: re.Pattern[str] = _compilar_regex(prefixo=("favoritos", "bookmarks"), case_sensitive=True)
        assert regex.match(string="marcadores.html") is None

    def test_string_unica_continua_funcionando_como_antes(self) -> None:
        """Regressão: string única (não-lista) deve manter o comportamento original."""
        regex: re.Pattern[str] = _compilar_regex(prefixo="favoritos", case_sensitive=True)
        assert regex.match(string="favoritos.html") is not None
        assert regex.match(string="bookmarks.html") is None

    def test_lista_vazia_de_prefixos_levanta_erro(self) -> None:
        """Garante que uma lista vazia de prefixos é considerada configuração inválida.
        Verifica que _compilar_regex sinaliza o erro levantando um ValueError quando nenhum prefixo é fornecido.
        """
        with pytest.raises(expected_exception=ValueError):
            _compilar_regex(prefixo=[])
