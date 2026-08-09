# Atoms/aplicacao/casos_uso.py
# pylint: disable=too-few-public-methods

"""Casos de uso da aplicação."""

from collections.abc import Sequence

from src.aplicacao.portas import Conversor, Diretorio, OrquestradorClient
from src.dominio.entidades import TagExtraida


class ListarTagExtraidas:
    """Caso de uso: listar todos os arquivos html."""

    def __init__(self, repo: Diretorio) -> None:
        self.repo: Diretorio = repo

    def buscar_arquivos_html(self) -> Sequence[TagExtraida]:
        """Executa a busca por arquivos."""
        return self.repo.buscar_arquivos_html()


class ConverterTagExtraidas:
    """Caso de uso: converter arquivos html para outro formato."""

    def __init__(self, conversor: Conversor) -> None:
        self.conversor: Conversor = conversor

    def executar(self, arquivos_html: list) -> str:
        """Executa a conversão dos arquivos html."""
        return self.conversor.converter(arquivos_html)


class OrquestrarBuscaEConversao:
    """Caso de uso: buscar arquivos html de uma API externa e converter."""

    def __init__(self, cliente: OrquestradorClient, conversor: Conversor) -> None:
        self.cliente: OrquestradorClient = cliente
        self.conversor: Conversor = conversor

    def executar(self) -> str:
        """Busca arquivos html e converte para o formato desejado."""
        arquivos_html: Sequence[TagExtraida] = self.cliente.buscar()
        return self.conversor.converter(arquivos_html)
