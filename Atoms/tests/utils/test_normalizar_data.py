"""Testes para normalizar_data: aceita uma data em (quase) qualquer formato
digitado pelo usuário e converte para o formato canônico M_D_AA aceito por
`_compilar_regex`/`_construir_padrao_data` (ex.: "5_20_26").

Escrito antes da implementação (TDD): estes testes descrevem o contrato
esperado da função.
"""

from __future__ import annotations

from re import Pattern

import pytest
from src.utils.system_tools import _compilar_regex, normalizar_data


class TestNormalizarData:
    """Suite de testes para normalizar_data."""

    @pytest.mark.parametrize(
        argnames="data_entrada,esperado",
        argvalues=[
            ("2026_05_20", "5_20_26"),
            ("20/05/2026", "5_20_26"),
            ("5_20_2026", "5_20_26"),
            ("05_20_26", "5_20_26"),
            ("05.20.26", "5_20_26"),
            ("5_20_26", "5_20_26"),
            ("2026_05_20", "5_20_26"),
            ("20_05_2026", "5_20_26"),
        ],
    )
    def test_aceita_varios_formatos_e_converte_para_canonico(self, data_entrada: str, esperado: str) -> None:
        """Verifica que datas digitadas em diversos formatos sao normalizadas para um formato canonico unico.
        Garante que normalizar_data converte entradas equivalentes em um mesmo valor padrao aceito pelas demais funcoes de regex.
        """
        assert normalizar_data(data=data_entrada) == esperado

    def test_data_vazia_levanta_value_error(self) -> None:
        """String vazia não é uma data válida."""
        with pytest.raises(expected_exception=ValueError):
            normalizar_data(data="")

    def test_data_nao_reconhecivel_levanta_value_error(self) -> None:
        """Texto que não corresponde a nenhuma data reconhecível levanta erro claro."""
        with pytest.raises(expected_exception=ValueError):
            normalizar_data(data="isso_nao_e_uma_data")

    def test_resultado_e_compativel_com_compilar_regex(self) -> None:
        """Verifica que o valor retornado por normalizar_data e diretamente utilizavel por _compilar_regex.
        Garante que a regex gerada a partir da data normalizada casa variacoes de separador e zero a esquerda, mas rejeita datas diferentes.
        """
        data_normalizada: str = normalizar_data("20/05/2026")  # "5_20_26"
        regex: Pattern[str] = _compilar_regex(
            prefixo="bookmarks",
            data=data_normalizada,
            case_sensitive=True,
        )
        # A regex aceita vários separadores
        assert regex.match("bookmarks_5_20_26.html") is not None
        assert regex.match("bookmarks_5_20_26.html") is not None
        assert regex.match("bookmarks_05.20.26.html") is not None
        # Também aceita com zero à esquerda
        assert regex.match("bookmarks_05_20_26.html") is not None
        # Data errada não casa
        assert regex.match("bookmarks_5_21_26.html") is None
