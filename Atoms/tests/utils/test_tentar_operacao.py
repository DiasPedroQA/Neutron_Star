"""
Testes para o módulo ``src.utils.system_tools``.

Organização das suítes
----------------------
    TestTentarOperacao          — wrapper de captura de OSError
    TestVerificarOcultoUnix     — detecção de oculto em Unix (ponto inicial)
    TestVerificarOcultoWindows  — detecção de oculto via atributo Win32
    TestPermissoes              — leitura de permissões de acesso
    TestDadosComuns             — metadados base (tamanho, datas, oculto)
    TestCalcularHash            — hash SHA-256 de arquivos
    TestObterTamanhoSeguro      — fallback de tamanho via stat
    TestCriarItem               — fábrica de ItemArquivo / ItemDiretorio
    TestObterInfoArquivo        — wrapper tipado para arquivos
    TestListarDiretorio         — listagem de diretório com filtros
"""

import pytest

from src.utils.system_tools import _tentar_operacao


# =============================================================================
# _tentar_operacao
# =============================================================================
class TestTentarOperacao:
    """Testes para a função _tentar_operacao."""

    def test_sucesso(self) -> None:
        """Retorna o resultado quando não há exceção."""
        resultado: int | None = _tentar_operacao(lambda x: x + 1, 41)
        assert resultado == 42

    def test_captura_oserror_com_padrao(self) -> None:
        """Retorna o valor padrão em caso de OSError."""

        def _falha() -> None:
            raise PermissionError("sem permissão")

        resultado: str | None = _tentar_operacao(_falha, valor_padrao="erro")
        assert resultado == "erro"

    @pytest.mark.parametrize(
        argnames="excecao",
        argvalues=[PermissionError, FileNotFoundError, OSError],
        ids=["permission-error", "file-not-found", "oserror-base"],
    )
    def test_captura_subclasses_oserror(self, excecao: type[OSError]) -> None:
        """Captura subclasses de OSError e retorna None."""

        def _falha() -> None:
            raise excecao("erro")

        assert _tentar_operacao(_falha) is None

    def test_nao_captura_outras_excecoes(self) -> None:
        """Não captura exceções que não são OSError."""

        def _falha() -> None:
            raise ValueError("erro inesperado")

        with pytest.raises(expected_exception=ValueError):
            _tentar_operacao(_falha)
