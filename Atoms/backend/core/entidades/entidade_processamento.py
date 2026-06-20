# Atoms/backend/core/entidades/entidade_processamento.py

"""Modelos de retorno do processamento de favoritos."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from backend.core.entidades.entidade_bookmark import Favorito

logger: logging.Logger = logging.getLogger(name=__name__)

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
        # Detecta uso de parâmetros legados e loga
        if total_arquivos == 0 and total_files is not None:
            logger.info(
                "Usando parâmetro 'total_files' em vez de 'total_arquivos': %d",
                total_files,
            )
        if arquivos_processados == 0 and processed_files is not None:
            logger.info(
                "Usando parâmetro 'processed_files' em vez de 'arquivos_processados': %d",
                processed_files,
            )
        if arquivos_com_falha == 0 and failed_files is not None:
            logger.info(
                "Usando parâmetro 'failed_files' em vez de 'arquivos_com_falha': %d",
                failed_files,
            )
        if total_favoritos == 0 and total_bookmarks is not None:
            logger.info(
                "Usando parâmetro 'total_bookmarks' em vez de 'total_favoritos': %d",
                total_bookmarks,
            )

        self.total_arquivos = total_arquivos if total_files is None else total_files
        self.arquivos_processados = (
            arquivos_processados if processed_files is None else processed_files
        )
        self.arquivos_com_falha = (
            arquivos_com_falha if failed_files is None else failed_files
        )
        self.total_favoritos = (
            total_favoritos if total_bookmarks is None else total_bookmarks
        )

        logger.debug(
            "EstatisticasProcessamento criadas: total_arquivos=%d, processados=%d, "
            "falha=%d, favoritos=%d",
            self.total_arquivos,
            self.arquivos_processados,
            self.arquivos_com_falha,
            self.total_favoritos,
        )

        # Validações leves de consistência (apenas warning, sem quebrar)
        if (
            self.total_arquivos < 0
            or self.arquivos_processados < 0
            or self.arquivos_com_falha < 0
            or self.total_favoritos < 0
        ):
            logger.warning(
                "Estatísticas com valores negativos: arquivos=%d, processados=%d, "
                "falha=%d, favoritos=%d",
                self.total_arquivos,
                self.arquivos_processados,
                self.arquivos_com_falha,
                self.total_favoritos,
            )

        if self.arquivos_processados + self.arquivos_com_falha > self.total_arquivos:
            logger.warning(
                "Inconsistência: processados(%d) + falhas(%d) > total_arquivos(%d)",
                self.arquivos_processados,
                self.arquivos_com_falha,
                self.total_arquivos,
            )

    def para_dict(self) -> dict[str, int]:
        """Retorna as estatísticas como um dicionário simples."""
        logger.debug("Convertendo estatísticas para dict (para_dict)")
        return {
            "total_arquivos": self.total_arquivos,
            "arquivos_processados": self.arquivos_processados,
            "arquivos_com_falha": self.arquivos_com_falha,
            "total_favoritos": self.total_favoritos,
        }

    def to_dict(self) -> dict[str, int]:
        """Retorna estatísticas com chaves antigas de compatibilidade."""
        logger.debug("Convertendo estatísticas para dict de compatibilidade (to_dict)")
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
        logger.debug("Setando total_files = %d", valor)
        self.total_arquivos = valor

    @property
    def processed_files(self) -> int:
        """Alias de compatibilidade para `arquivos_processados`."""
        return self.arquivos_processados

    @processed_files.setter
    def processed_files(self, valor: int) -> None:
        logger.debug("Setando processed_files = %d", valor)
        self.arquivos_processados = valor

    @property
    def failed_files(self) -> int:
        """Alias de compatibilidade para `arquivos_com_falha`."""
        return self.arquivos_com_falha

    @failed_files.setter
    def failed_files(self, valor: int) -> None:
        logger.debug("Setando failed_files = %d", valor)
        self.arquivos_com_falha = valor

    @property
    def total_bookmarks(self) -> int:
        """Alias de compatibilidade para `total_favoritos`."""
        return self.total_favoritos

    @total_bookmarks.setter
    def total_bookmarks(self, valor: int) -> None:
        logger.debug("Setando total_bookmarks = %d", valor)
        self.total_favoritos = valor


@dataclass(init=False)
class ResultadoProcessamento:
    """Resultado do processamento de um diretório de favoritos."""

    favoritos_processados: list[Favorito] = field(default_factory=list)
    estatisticas_processadas: EstatisticasProcessamento = field(
        default_factory=EstatisticasProcessamento
    )
    caminho_raiz: str = ""

    def __init__(
        self,
        favoritos_processados: list[Favorito] | None = None,
        estatisticas_processadas: EstatisticasProcessamento | None = None,
        caminho_raiz: str = "",
        *,
        bookmarks: list[Favorito] | None = None,
        statistics: EstatisticasProcessamento | None = None,
        root_path: str | None = None,
    ) -> None:
        # Log de parâmetros legados
        if favoritos_processados is None and bookmarks is not None:
            logger.info(
                "Usando parâmetro 'bookmarks' em vez de 'favoritos_processados' (%d itens)",
                len(bookmarks),
            )
        if estatisticas_processadas is None and statistics is not None:
            logger.info(
                "Usando parâmetro 'statistics' em vez de 'estatisticas_processadas'"
            )
        if not caminho_raiz and root_path is not None:
            logger.info(
                "Usando parâmetro 'root_path' em vez de 'caminho_raiz': %r", root_path
            )

        self.favoritos_processados = (
            favoritos_processados
            if favoritos_processados is not None
            else (bookmarks or [])
        )
        self.estatisticas_processadas = (
            estatisticas_processadas or statistics or EstatisticasProcessamento()
        )
        self.caminho_raiz = caminho_raiz if root_path is None else root_path

        logger.debug(
            "ResultadoProcessamento criado: caminho=%r, favoritos=%d, estatisticas=%s",
            self.caminho_raiz,
            len(self.favoritos_processados),
            self.estatisticas_processadas,
        )

        self.__post_init__()

    def __post_init__(self) -> None:
        if not isinstance(self.caminho_raiz, str):
            logger.error("caminho_raiz não é str: %r", self.caminho_raiz)
            raise TypeError("caminho_raiz deve ser str")

    def para_dict(self) -> ResultadoProcessamentoDict:
        """Retorna o resultado como um dicionário para compatibilidade."""
        logger.debug("Convertendo resultado para dict (para_dict)")
        return {
            "favoritos_processados": self.favoritos_processados,
            "estatisticas_processadas": self.estatisticas_processadas.para_dict(),
            "caminho_raiz": self.caminho_raiz,
        }

    def to_dict(self) -> ResultadoProcessamentoDict:
        """Retorna resultado com chaves antigas de compatibilidade."""
        logger.debug("Convertendo resultado para dict de compatibilidade (to_dict)")
        return {
            "bookmarks": self.favoritos_processados,
            "estatisticas_processadas": self.estatisticas_processadas.to_dict(),
            "caminho_raiz": self.caminho_raiz,
        }

    @property
    def bookmarks(self) -> list[Favorito]:
        """Alias de compatibilidade para `favoritos_processados`."""
        return self.favoritos_processados

    @bookmarks.setter
    def bookmarks(self, valor: list[Favorito]) -> None:
        logger.debug("Setando bookmarks com %d itens", len(valor))
        self.favoritos_processados = valor

    @property
    def statistics(self) -> EstatisticasProcessamento:
        """Alias de compatibilidade para `estatisticas_processadas`."""
        return self.estatisticas_processadas

    @property
    def root_path(self) -> str:
        """Alias de compatibilidade para `caminho_raiz`."""
        return self.caminho_raiz
