# Atoms/src/adaptadores/schemas.py
# pylint: disable=too-few-public-methods, too-many-return-statements

"""Módulo de validação de dados e contratos de entrada (Schemas)."""

from typing import Any

FORMATOS_VALIDOS: set[str] = {"csv", "json"}


class ValidadorRequisicao:
    """Classe responsável por validar os payloads das requisições HTTP da API."""

    @staticmethod
    def _validar_arquivos(arquivos: Any) -> str | None:
        """Valida a lista de arquivos selecionados. Retorna mensagem de erro ou None se válido."""
        if arquivos is None:
            return "O campo 'arquivos_selecionados' é obrigatório."

        if not isinstance(arquivos, list):
            return "O campo 'arquivos_selecionados' deve ser uma lista."

        if not arquivos:
            return "A lista de arquivos selecionados não pode estar vazia."

        if any(not isinstance(item, str) or not item.strip() for item in arquivos):
            return "Todos os caminhos na lista de arquivos devem ser válidos."

        return None

    @staticmethod
    def _validar_extensao(extensao: Any) -> str | None:
        """Valida o formato de destino. Retorna mensagem de erro ou None se válido."""
        if extensao is None:
            return "O campo 'extensao_destino' é obrigatório."

        if not isinstance(extensao, str):
            return "O campo 'extensao_destino' deve ser uma string."

        ext_limpa: str = extensao.strip().lower().replace(".", "")
        if ext_limpa not in FORMATOS_VALIDOS:
            return "Formato de destino inválido. Escolha apenas 'csv' ou 'json'."

        return None

    @classmethod
    def validar_processamento_lote(cls, dados: Any) -> tuple[bool, str]:
        """Valida o payload enviado para a rota de processamento em lote.

        Verifica se a lista de arquivos selecionados e o formato de saída
        estão presentes, se possuem os tipos corretos e se são consistentes.
        Retorna uma tupla contendo (sucesso: bool, mensagem_erro: str).
        """
        if not isinstance(dados, dict):
            return False, "O payload da requisição deve ser um objeto JSON."

        if erro_arquivos := cls._validar_arquivos(dados.get("arquivos_selecionados")):
            return False, erro_arquivos

        if erro_extensao := cls._validar_extensao(dados.get("extensao_destino")):
            return False, erro_extensao

        return True, ""
