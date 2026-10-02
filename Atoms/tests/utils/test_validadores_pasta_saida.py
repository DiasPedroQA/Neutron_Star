# Atoms/tests/utils/test_validadores_pasta_saida.py

"""Contrato do campo opcional ``pasta_saida`` (string ou null) no payload de /api/processar."""

from typing import Any

import pytest

from src.utils.validadores import ValidadorRequisicao


def _payload(**extras: Any) -> dict[str, Any]:
    """Monta um payload base para os testes, mesclando campos extras."""
    base: dict[str, Any] = {"arquivos_selecionados": ["/home/u/a.html"], "extensao_destino": "json"}
    return base | extras


def test_pasta_saida_ausente_e_valida() -> None:
    """Aceita payload sem o campo ``pasta_saida``."""
    assert ValidadorRequisicao.validar_processamento_lote(dados=_payload()) == (True, "")


def test_pasta_saida_nula_e_valida() -> None:
    """Aceita ``pasta_saida=None``."""
    dados: dict[str, Any] = _payload(pasta_saida=None)

    assert ValidadorRequisicao.validar_processamento_lote(dados=dados) == (True, "")


def test_pasta_saida_texto_valido_e_aceita() -> None:
    """Aceita ``pasta_saida`` como string não vazia."""
    dados: dict[str, Any] = _payload(pasta_saida="/home/u/saida")

    assert ValidadorRequisicao.validar_processamento_lote(dados=dados) == (True, "")


@pytest.mark.parametrize("valor", [123, ["/home/u"], {"a": 1}, True])
def test_pasta_saida_com_tipo_errado_e_rejeitada(valor: Any) -> None:
    """Rejeita ``pasta_saida`` quando não é string."""
    valido, mensagem = ValidadorRequisicao.validar_processamento_lote(
        dados=_payload(pasta_saida=valor)
    )

    assert valido is False
    assert mensagem == "O campo 'pasta_saida' deve ser uma string."


@pytest.mark.parametrize("valor", ["", "   ", "\t\n"])
def test_pasta_saida_em_branco_e_rejeitada(valor: str) -> None:
    """Rejeita ``pasta_saida`` quando é string vazia ou só espaços."""
    valido, mensagem = ValidadorRequisicao.validar_processamento_lote(
        dados=_payload(pasta_saida=valor)
    )

    assert valido is False
    assert mensagem == "O campo 'pasta_saida' não pode ser vazio."
