"""Testes unitários para validação dos payloads da API."""

from typing import Any

import pytest

from src.adaptadores.schemas import ValidadorRequisicao


class TestValidadorRequisicao:
    """Testa as regras de validação do processamento em lote."""

    @pytest.mark.parametrize(argnames="extensao", argvalues=["json", " .CSV ", ".Json"])
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
        sucesso, mensagem = ValidadorRequisicao.validar_processamento_lote(["arquivo.html"])

        assert sucesso is False
        assert mensagem == "O payload da requisição deve ser um objeto JSON."

    @pytest.mark.parametrize(
        argnames=("dados", "mensagem"),
        argvalues=[
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
