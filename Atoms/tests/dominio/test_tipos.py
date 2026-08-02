"""Testes de unidade para as funções utilitárias de conversão de tipos no domínio.

Verifica o comportamento de to_int e to_str em cenários válidos e inválidos, garantindo conversões previsíveis e tratamento adequado de valores ausentes.
"""

from __future__ import annotations

from src.dominio.tipos import to_int, to_str


def test_to_int_valido() -> None:
    """Valida que to_int converte corretamente valores numéricos representados como string ou inteiro.

    Garante que números positivos, zero e negativos são convertidos para int preservando o valor esperado.
    """
    assert to_int(valor="123") == 123
    assert to_int(valor=456) == 456
    assert to_int(valor="0") == 0
    assert to_int(valor="-10") == -10


def test_to_int_invalido() -> None:
    """Verifica que to_int retorna None para entradas não numéricas ou ausentes.

    Também garante que strings representando números com ponto decimal são convertidas truncando a parte fracionária para int.
    """
    assert to_int(valor="abc") is None
    assert to_int(valor=None) is None
    assert to_int(valor="12.34") == 12  # converte float para int


def test_to_str_valido() -> None:
    """Garante que to_str converte corretamente valores já textuais ou numéricos para string.

    Confirma que strings são preservadas e inteiros são transformados em sua representação textual equivalente.
    """
    assert to_str(valor="hello") == "hello"
    assert to_str(valor=123) == "123"


def test_to_str_none() -> None:
    """Valida que to_str preserva valores ausentes retornando None em vez de uma string.

    Garante que chamadas com None não geram texto inesperado e mantêm a semântica de ausência de valor.
    """
    assert to_str(valor=None) is None
