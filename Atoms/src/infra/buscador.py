# Atoms/infra/repositorio.py
# pylint: disable=too-few-public-methods

"""Pastas concretas para arquivos html."""

from pathlib import Path

from src.aplicacao.portas import Diretorio
from src.dominio.entidades import TagExtraida


class PastaBuscadora(Diretorio):
    """Pasta que armazena arquivos html."""

    def buscar_arquivos_html(self) -> list[TagExtraida]:
        """Retorna uma lista de arquivos html encontrados no sistema de arquivos.

        Para manter compatibilidade com a porta, retornamos instâncias de
        `TagExtraida` em vez de Path.
        """

        pasta_raiz = "~/"
        caminho_tratado: Path = Path(pasta_raiz).expanduser()
        arquivos: list[Path] = [
            arquivo for arquivo in caminho_tratado.glob("**/*.html")
            if arquivo.is_file()
        ]

        resultados: list[TagExtraida] = []

        for arquivo in arquivos:
            titulo: str = arquivo.stem
            url = str(arquivo.resolve())
            resultados.append(TagExtraida(titulo=titulo, url=url))

        return resultados
