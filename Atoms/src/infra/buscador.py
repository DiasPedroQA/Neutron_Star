# Atoms/src/infra/buscador.py

"""Pastas concretas para arquivos html."""

from datetime import datetime, timezone
from os import stat_result
from pathlib import Path

from aplicacao.portas import Diretorio
from dominio.entidades import ArquivoTemp


class PastaBuscadora(Diretorio):
    """
    Busca recursivamente arquivos .html a partir do diretório home (~/),
    com opções para incluir/excluir ocultos e diretórios privados.
    """

    def __init__(
        self,
        incluir_ocultos: bool = False,
        excluir_privados: bool = True,
    ) -> None:
        """Configura os filtros aplicados durante a busca recursiva."""
        self.incluir_ocultos: bool = incluir_ocultos
        self.excluir_privados: bool = excluir_privados
        self._diretorios_privados: set[str] = {
            ".ssh",
            ".gnupg",
            ".aws",
            ".azure",
            ".cache",
            ".local",
            "docs",
        }

    def converter_data_float_para_str(self, data_float: float) -> str:
        """Converte timestamp float para string legível usando UTC."""
        return datetime.fromtimestamp(timestamp=data_float, tz=timezone.utc).strftime(
            format="%Y-%m-%d %H:%M:%S"
        )

    def extrair_stats_do_arquivo(self, caminho_arquivo: Path) -> ArquivoTemp:
        """Extrai informações básicas de um arquivo Path e retorna um objeto ArquivoTemp."""
        stats: stat_result = caminho_arquivo.stat()
        return ArquivoTemp(
            nome=caminho_arquivo.name,
            caminho_absoluto=str(caminho_arquivo.resolve()),
            tamanho=stats.st_size,
            data_criacao=self.converter_data_float_para_str(data_float=stats.st_ctime),
            data_modificacao=self.converter_data_float_para_str(
                data_float=stats.st_mtime
            ),
            data_acesso=self.converter_data_float_para_str(data_float=stats.st_atime),
            conteudo=None,  # Conteúdo não é carregado nesta etapa
        )

    def buscar_arquivos_html(self) -> list[ArquivoTemp]:
        """Percorre a árvore a partir de ~/ e retorna uma lista de ArquivoTemp."""
        pasta_raiz: Path = Path("~/").expanduser()
        resultados: list[ArquivoTemp] = []

        for arquivo in pasta_raiz.rglob("*.html"):
            if arquivo.is_dir():
                continue

            # Filtro de ocultos
            if not self.incluir_ocultos and any(
                parte.startswith(".") for parte in arquivo.parts
            ):
                continue

            # Filtro de diretórios privados
            if self.excluir_privados and any(
                parte in self._diretorios_privados for parte in arquivo.parts
            ):
                continue

            # Filtro de prefixos aceitáveis para o nome do arquivo
            prefixos_aceitaveis: set[str] = {
                "book",
                "fav",
            }

            if not any(
                arquivo.name.startswith(prefixo) for prefixo in prefixos_aceitaveis
            ):
                continue

            resultados.append(self.extrair_stats_do_arquivo(caminho_arquivo=arquivo))

        return resultados
