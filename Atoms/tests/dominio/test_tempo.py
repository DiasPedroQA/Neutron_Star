"""Testes da conversão de timestamp Unix (dominio/tempo.py)."""

from datetime import datetime, timezone

import pytest
from dominio.tempo import converter_timestamp_unix


class TestConverterTimestampUnix:
    """Conversão de timestamp Unix (segundos, como string) para datetime."""

    def test_converte_timestamp_valido(self) -> None:
        """Um timestamp Unix válido deve virar o datetime correspondente, em UTC."""
        resultado: datetime | None = converter_timestamp_unix(valor="0")

        assert resultado == datetime.fromtimestamp(0, timezone.utc)

    @pytest.mark.parametrize(
        argnames="valor",
        argvalues=[
            pytest.param("", id="string_vazia"),
            pytest.param("nao-e-um-numero", id="nao_numerico"),
            pytest.param(None, id="none"),
        ],
    )
    def test_valores_invalidos_retornam_none(self, valor: str | None) -> None:
        """Entrada vazia, não numérica ou None deve retornar None, nunca lançar exceção."""
        assert converter_timestamp_unix(valor=valor) is None
