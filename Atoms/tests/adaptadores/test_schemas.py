# Atoms/tests/adaptadores/test_schemas.py
# pylint: disable=protected-access

"""Testes unitários para validação dos payloads da API e métodos de schema."""

from typing import Any

import pytest

from src.adaptadores.schemas import ValidadorRequisicao


class TestValidadorRequisicao:
    """Testa as regras de validação do processamento em lote."""

    @pytest.mark.parametrize("extensao", ["json", " .CSV ", ".Json", "CSV", "JSON"])
    def test_aceita_payload_valido_e_normaliza_extensao(self, extensao: str) -> None:
        """Aceita extensões suportadas após normalização."""
        resultado: tuple[bool, str] = ValidadorRequisicao.validar_processamento_lote(
            dados={
                "arquivos_selecionados": ["/tmp/favoritos.html"],
                "extensao_destino": extensao,
            }
        )
        assert resultado == (True, "")

    def test_rejeita_payload_que_nao_e_dicionario(self) -> None:
        """Rejeita payloads que não são objetos JSON."""
        sucesso, mensagem = ValidadorRequisicao.validar_processamento_lote(dados=["arquivo.html"])
        assert sucesso is False
        assert mensagem == "O payload da requisição deve ser um objeto JSON."

    @pytest.mark.parametrize(
        ("dados", "mensagem"),
        [
            ({"extensao_destino": "json"}, "arquivos_selecionados"),
            (
                {"arquivos_selecionados": "arquivo.html", "extensao_destino": "json"},
                "deve ser uma lista",
            ),
            ({"arquivos_selecionados": [], "extensao_destino": "json"}, "não pode estar vazia"),
            ({"arquivos_selecionados": [""], "extensao_destino": "json"}, "caminhos na lista"),
            ({"arquivos_selecionados": [123], "extensao_destino": "json"}, "caminhos na lista"),
            ({"arquivos_selecionados": ["arquivo.html"]}, "extensao_destino"),
            (
                {"arquivos_selecionados": ["arquivo.html"], "extensao_destino": 123},
                "deve ser uma string",
            ),
            (
                {"arquivos_selecionados": ["arquivo.html"], "extensao_destino": "xml"},
                "Formato de destino inválido",
            ),
        ],
    )
    def test_rejeita_payload_invalido(self, dados: dict[str, Any], mensagem: str) -> None:
        """Rejeita payloads que violam cada regra do schema."""
        sucesso, erro = ValidadorRequisicao.validar_processamento_lote(dados)
        assert sucesso is False
        assert mensagem in erro

    # =========================================================================
    # Testes diretos dos novos métodos auxiliares privados
    # =========================================================================

    def test_validar_arquivos_sucesso(self) -> None:
        """Garante retorno None quando a lista de arquivos é perfeitamente válida."""
        erro = ValidadorRequisicao._validar_arquivos(["/caminho/1.html", "/caminho/2.html"])
        assert erro is None

    def test_validar_extensao_sucesso(self) -> None:
        """Garante retorno None para formatos aceitos."""
        assert ValidadorRequisicao._validar_extensao("json") is None
        assert ValidadorRequisicao._validar_extensao(".csv") is None
        assert ValidadorRequisicao._validar_extensao("CSV") is None

    def test_validar_extensao_invalida(self) -> None:
        """Garante mensagem de erro adequada para formatos não suportados."""
        erro = ValidadorRequisicao._validar_extensao("pdf")
        assert erro is not None
        assert "Escolha apenas 'csv' ou 'json'" in erro
