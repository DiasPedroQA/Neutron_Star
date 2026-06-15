"""Modelos de retorno do processamento de favoritos."""

from __future__ import annotations

from dataclasses import dataclass, field

from Atoms.backend.core.entidades.entidade_bookmark import Favorito

ResultadoProcessamentoDict = dict[str, str | list[Favorito] | dict[str, int]]


@dataclass(init=False)
class EstatisticasProcessamento:
    """Resumo de quantos arquivos e favoritos foram processados."""

    total_arquivos: int = 0
    arquivos_processados: int = 0
    arquivos_com_falha: int = 0
    total_favoritos: int = 0

    def __init__(
        self,
        total_arquivos: int = 0,
        arquivos_processados: int = 0,
        arquivos_com_falha: int = 0,
        total_favoritos: int = 0,
        *,
        total_files: int | None = None,
        processed_files: int | None = None,
        failed_files: int | None = None,
        total_bookmarks: int | None = None,
    ) -> None:
        self.total_arquivos = total_arquivos if total_files is None else total_files
        self.arquivos_processados = arquivos_processados if processed_files is None else processed_files
        self.arquivos_com_falha = arquivos_com_falha if failed_files is None else failed_files
        self.total_favoritos = total_favoritos if total_bookmarks is None else total_bookmarks

    def para_dict(self) -> dict[str, int]:
        """Retorna as estatísticas como um dicionário simples."""
        return {
            "total_arquivos": self.total_arquivos,
            "arquivos_processados": self.arquivos_processados,
            "arquivos_com_falha": self.arquivos_com_falha,
            "total_favoritos": self.total_favoritos,
        }

    def to_dict(self) -> dict[str, int]:
        """Retorna estatísticas com chaves antigas de compatibilidade."""
        return {
            "total_arquivos": self.total_arquivos,
            "arquivos_processados": self.arquivos_processados,
            "arquivos_com_falha": self.arquivos_com_falha,
            "total_bookmarks": self.total_favoritos,
        }

    @property
    def total_files(self) -> int:
        """Alias de compatibilidade para `total_arquivos`."""
        return self.total_arquivos

    @total_files.setter
    def total_files(self, valor: int) -> None:
        self.total_arquivos = valor

    @property
    def processed_files(self) -> int:
        """Alias de compatibilidade para `arquivos_processados`."""
        return self.arquivos_processados

    @processed_files.setter
    def processed_files(self, valor: int) -> None:
        self.arquivos_processados = valor

    @property
    def failed_files(self) -> int:
        """Alias de compatibilidade para `arquivos_com_falha`."""
        return self.arquivos_com_falha

    @failed_files.setter
    def failed_files(self, valor: int) -> None:
        self.arquivos_com_falha = valor

    @property
    def total_bookmarks(self) -> int:
        """Alias de compatibilidade para `total_favoritos`."""
        return self.total_favoritos

    @total_bookmarks.setter
    def total_bookmarks(self, valor: int) -> None:
        self.total_favoritos = valor


@dataclass(init=False)
class ResultadoProcessamento:
    """Resultado do processamento de um diretório de favoritos."""

    favoritos: list[Favorito] = field(default_factory=list)
    estatisticas: EstatisticasProcessamento = field(default_factory=EstatisticasProcessamento)
    caminho_raiz: str = ""

    def __init__(
        self,
        favoritos: list[Favorito] | None = None,
        estatisticas: EstatisticasProcessamento | None = None,
        caminho_raiz: str = "",
        *,
        bookmarks: list[Favorito] | None = None,
        statistics: EstatisticasProcessamento | None = None,
        root_path: str | None = None,
    ) -> None:
        self.favoritos = favoritos if favoritos is not None else (bookmarks or [])
        self.estatisticas = estatisticas or statistics or EstatisticasProcessamento()
        self.caminho_raiz = caminho_raiz if root_path is None else root_path
        self.__post_init__()

    def __post_init__(self) -> None:
        if not isinstance(self.caminho_raiz, str):
            raise TypeError("caminho_raiz deve ser str")

    def para_dict(self) -> ResultadoProcessamentoDict:
        """Retorna o resultado como um dicionário para compatibilidade.

        O dicionário mantém o formato simples usado pela CLI e por outros
        consumidores que não precisam da instância do dataclass.
        """
        return {
            "favoritos": self.favoritos,
            "estatisticas": self.estatisticas.para_dict(),
            "caminho_raiz": self.caminho_raiz,
        }

    def to_dict(self) -> ResultadoProcessamentoDict:
        """Retorna resultado com chaves antigas de compatibilidade."""
        return {
            "bookmarks": self.favoritos,
            "estatisticas": self.estatisticas.to_dict(),
            "caminho_raiz": self.caminho_raiz,
        }

    @property
    def bookmarks(self) -> list[Favorito]:
        """Alias de compatibilidade para `favoritos`."""
        return self.favoritos

    @bookmarks.setter
    def bookmarks(self, valor: list[Favorito]) -> None:
        self.favoritos = valor

    @property
    def statistics(self) -> EstatisticasProcessamento:
        """Alias de compatibilidade para `estatisticas`."""
        return self.estatisticas

    @property
    def root_path(self) -> str:
        """Alias de compatibilidade para `caminho_raiz`."""
        return self.caminho_raiz
