"""Modelos de retorno do processamento de bookmarks."""

from __future__ import annotations

from dataclasses import dataclass, field

from Atoms.backend.core.entidades.entidade_bookmark import Bookmark

ResultadoProcessamentoDict = dict[str, str | list[Bookmark] | dict[str, int]]


@dataclass
class EstatisticasProcessamento:
    """Resumo de quantos arquivos e bookmarks foram processados."""

    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_bookmarks: int = 0

    def to_dict(self) -> dict[str, int]:
        """Retorna as estatísticas como um dicionário simples."""
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "total_bookmarks": self.total_bookmarks,
        }


@dataclass
class ResultadoProcessamento:
    """Resultado do processamento de um diretório de bookmarks."""

    bookmarks: list[Bookmark] = field(default_factory=list)
    statistics: EstatisticasProcessamento = field(default_factory=EstatisticasProcessamento)
    root_path: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.root_path, str):
            raise TypeError("root_path deve ser str")

    def to_dict(self) -> ResultadoProcessamentoDict:
        """Retorna o resultado como um dicionário para compatibilidade.

        O dicionário mantém o formato simples usado pela CLI e por outros
        consumidores que não precisam da instância do dataclass.
        """
        return {
            "bookmarks": self.bookmarks,
            "statistics": self.statistics.to_dict(),
            "root_path": self.root_path,
        }
