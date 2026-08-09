# Atoms/infra/repositorio.py

"""Repositórios concretos para bookmarks."""

from pathlib import Path

from dominio.entidades import Bookmark
from aplicacao.portas import BookmarkRepositorio


class RepositorioEmMemoria(BookmarkRepositorio):
    """Repositório que armazena bookmarks em memória (mock)."""

    def buscar_arquivos_html(self) -> list[Bookmark]:
        """Retorna uma lista de bookmarks encontrados no sistema de arquivos.

        Para manter compatibilidade com a porta, retornamos instâncias de
        `Bookmark` em vez de Path.
        """
        pasta_raiz = "~/"
        caminho_tratado: Path = Path(pasta_raiz).expanduser()
        arquivos: list[Path] = [arquivo for arquivo in caminho_tratado.glob(
            "**/*.html") if arquivo.is_file()]
        resultados: list[Bookmark] = []
        for arquivo in arquivos:
            titulo: str = arquivo.stem
            url = str(arquivo.resolve())
            resultados.append(Bookmark(titulo=titulo, url=url))
        return resultados
