# Atoms/aplicacao/casos_uso.py

"""Casos de uso da aplicação."""

from dominio.entidades import Bookmark

from .portas import BookmarkRepositorio, Conversor, OrquestradorClient


class ListarBookmarks:
    """Caso de uso: listar todos os bookmarks."""

    def __init__(self, repo: BookmarkRepositorio) -> None:
        self.repo: BookmarkRepositorio = repo

    def buscar_arquivos_html(self) -> list[Bookmark]:
        """Executa a busca por arquivos."""
        return self.repo.buscar_arquivos_html()


class ConverterBookmarks:
    """Caso de uso: converter bookmarks para outro formato."""

    def __init__(self, conversor: Conversor) -> None:
        self.conversor: Conversor = conversor

    def executar(self, bookmarks: list) -> str:
        """Executa a conversão dos bookmarks."""
        return self.conversor.converter(bookmarks)


class OrquestrarBuscaEConversao:
    """Caso de uso: buscar bookmarks de uma API externa e converter."""

    def __init__(self, cliente: OrquestradorClient, conversor: Conversor) -> None:
        self.cliente: OrquestradorClient = cliente
        self.conversor: Conversor = conversor

    def executar(self) -> str:
        """Busca bookmarks e converte para o formato desejado."""
        bookmarks: list[Bookmark] = self.cliente.buscar()
        return self.conversor.converter(bookmarks)
