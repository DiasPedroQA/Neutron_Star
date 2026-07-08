"""Testes para a função _oculto_windows (detecção de atributo FILE_ATTRIBUTE_HIDDEN no Windows).

A função _oculto_windows utiliza a API Windows GetFileAttributesW para verificar
o atributo oculto. Esta suite testa o comportamento em diferentes cenários:
- Atributo de arquivo oculto presente/ausente.
- Retorno de erro da API (atributos inválidos).
- Exceção na chamada da API.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from src.utils.system_tools import _oculto_windows


class TestVerificarOcultoWindows:
    """Testes para _oculto_windows (atributo FILE_ATTRIBUTE_HIDDEN)."""

    _CAMINHO_WIN: Path = Path("C:\\algum\\arquivo.txt")

    @pytest.mark.parametrize(
        argnames="retorno_api, esperado",
        argvalues=[
            (0x2, True),  # FILE_ATTRIBUTE_HIDDEN setado
            (0x0, False),  # atributos normais (sem oculto)
            (-1, False),  # atributos inválidos (error)
        ],
        ids=["hidden_bit_set", "hidden_bit_not_set", "invalid_attributes"],
    )
    def test_interpreta_codigos_retorno_api(self, mock_windows: MagicMock, retorno_api: int, esperado: bool) -> None:
        """Verifica que a função interpreta corretamente os códigos de retorno da API.

        Args:
            mock_windows: Mock da função GetFileAttributesW (fixture).
            retorno_api: Valor simulado retornado pela API.
            esperado: Valor booleano esperado para a função.
        """
        mock_windows.return_value = retorno_api
        caminho_win: bool = _oculto_windows(caminho=self._CAMINHO_WIN)
        assert caminho_win is esperado

    def test_excecao_na_api_retorna_false(self, mock_windows: MagicMock) -> None:
        """Verifica que uma exceção na API resulta em False."""
        mock_windows.side_effect = OSError("erro simulado na API")
        caminho_win: bool = _oculto_windows(caminho=self._CAMINHO_WIN)
        assert not caminho_win
