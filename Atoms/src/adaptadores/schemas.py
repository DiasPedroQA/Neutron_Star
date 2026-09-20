# Atoms/src/adaptadores/schemas.py
# pylint: disable=too-few-public-methods, too-many-return-statements

"""Módulo de validação de dados e contratos de entrada (Schemas)."""

from typing import Any


class ValidadorRequisicao:
    """Classe responsável por validar os payloads das requisições HTTP da API."""

    @staticmethod
    def validar_processamento_lote(dados: dict[str, Any]) -> tuple[bool, str]:
        """Valida o payload enviado para a rota de processamento em lote.

        Verifica se a lista de arquivos selecionados e o formato de saída
        estão presentes, se possuem os tipos corretos e se são consistentes.
        Retorna uma tupla contendo (sucesso: bool, mensagem_erro: str).
        """
        if not isinstance(dados, dict):
            return False, "O payload da requisição deve ser um objeto JSON."

        arquivos: list[str] | Any = dados.get("arquivos_selecionados")
        extensao: str | Any = dados.get("extensao_destino")

        # 1. Validação de arquivos_selecionados
        if arquivos is None:
            return False, "O campo 'arquivos_selecionados' é obrigatório."

        if not isinstance(arquivos, list):
            return False, "O campo 'arquivos_selecionados' deve ser uma lista."

        if not arquivos:
            return False, "A lista de arquivos selecionados não pode estar vazia."

        for item in arquivos:
            if not isinstance(item, str) or not item.strip():
                return (False, "Todos os caminhos na lista de arquivos devem ser válidos.")

        # 2. Validação de extensao_destino
        if extensao is None:
            return False, "O campo 'extensao_destino' é obrigatório."

        if not isinstance(extensao, str):
            return False, "O campo 'extensao_destino' deve ser uma string."

        ext_limpa: str = extensao.strip().lower().replace(".", "")
        if ext_limpa not in ["csv", "json"]:
            return (False, "Formato de destino inválido. Escolha apenas 'csv' ou 'json'.")

        return True, ""
