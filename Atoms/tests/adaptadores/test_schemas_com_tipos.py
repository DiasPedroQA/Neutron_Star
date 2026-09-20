"""Testes de validação de schemas com type hints específicos.

.. module:: tests.adaptadores.test_schemas_com_tipos
   :platform: Unix, Windows
   :synopsis: Validação de payloads com tipos TypedDict.
"""

import pytest

from src.adaptadores.schemas import ValidadorRequisicao


class TestValidadorRequisicaoComTipos:
    """Testes do validador com contexto de tipos."""

    def test_validacao_payload_valido(self) -> None:
        """Valida payload correto para processamento em lote."""
        payload = {
            "arquivos_selecionados": [
                "/home/user/bookmarks.html",
                "/home/user/favoritos.html",
            ],
            "extensao_destino": "json",
        }
        sucesso, msg = ValidadorRequisicao.validar_processamento_lote(payload)
        assert sucesso is True
        assert msg == ""

    def test_validacao_payload_vazio(self) -> None:
        """Valida rejeição de payload vazio."""
        sucesso, msg = ValidadorRequisicao.validar_processamento_lote({})
        assert sucesso is False
        assert "obrigatório" in msg.lower()

    def test_validacao_lista_arquivos_vazia(self) -> None:
        """Valida rejeição de lista vazia de arquivos."""
        payload = {"arquivos_selecionados": [], "extensao_destino": "json"}
        sucesso, msg = ValidadorRequisicao.validar_processamento_lote(payload)
        assert sucesso is False
        assert "vazia" in msg.lower()

    def test_validacao_extensao_invalida(self) -> None:
        """Valida rejeição de formato inválido."""
        payload = {
            "arquivos_selecionados": ["/file.html"],
            "extensao_destino": "xml",
        }
        sucesso, msg = ValidadorRequisicao.validar_processamento_lote(payload)
        assert sucesso is False
        assert "inválido" in msg.lower()

    def test_validacao_extensao_com_ponto_removido(self) -> None:
        """Valida normalização de extensão com ponto prefixado."""
        payload = {
            "arquivos_selecionados": ["/file.html"],
            "extensao_destino": ".csv",
        }
        sucesso, msg = ValidadorRequisicao.validar_processamento_lote(payload)
        assert sucesso is True

    @pytest.mark.parametrize("ext", ["JSON", "Json", "jSoN", "csv", "CSV"])
    def test_validacao_extensoes_case_insensitive(self, ext: str) -> None:
        """Valida aceitação de extensões em qualquer case."""
        payload = {
            "arquivos_selecionados": ["/file.html"],
            "extensao_destino": ext,
        }
        sucesso, _ = ValidadorRequisicao.validar_processamento_lote(payload)
        assert sucesso is True
