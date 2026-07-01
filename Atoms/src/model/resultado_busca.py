"""Modelo para o resultado de uma busca."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .item_neutro import ItemBase


@dataclass
class ResultadoBusca:
    """Armazena os itens encontrados e metadados da execução.

    Atributos:
        consulta: Texto da consulta (ou string vazia).
        itens: Lista de itens que atenderam aos critérios.
        total_encontrado: Total de itens (pode diferir do len(itens) com paginação).
        tempo_execucao: Tempo de execução em segundos.
        raiz_busca: Diretório raiz da busca.
        criterios: Instância de CriteriosBusca utilizada (opcional, para exibição).
        metadados: Dicionário livre para informações adicionais.
    """

    consulta: str
    itens: list[ItemBase] = field(default_factory=list)
    total_encontrado: int = 0
    tempo_execucao: float = 0.0
    raiz_busca: Path | None = None
    criterios: Any | None = None
    metadados: dict[str, str | int | float] = field(default_factory=dict)

    def filtrar_por_tipo(self, tipo: type) -> ResultadoBusca:
        """Retorna um novo ResultadoBusca apenas com itens do tipo especificado.

        Args:
            tipo: Classe desejada (ItemArquivo ou ItemDiretorio).

        Returns:
            Nova instância com itens filtrados.
        """
        filtrados: list[ItemBase] = [i for i in self.itens if isinstance(i, tipo)]
        return ResultadoBusca(
            consulta=self.consulta,
            itens=filtrados,
            total_encontrado=len(filtrados),
            tempo_execucao=self.tempo_execucao,
            metadados=self.metadados,
        )

    def para_dict(
        self,
    ) -> dict[str, str | int | float | list[dict[str, str | int | float]] | dict[str, str | int | float]]:
        """Serializa o resultado e seus itens para um dicionário."""
        return {
            "consulta": self.consulta,
            "itens": [item.para_dict() for item in self.itens],
            "total_encontrado": self.total_encontrado,
            "tempo_execucao": self.tempo_execucao,
            "metadados": self.metadados,
        }
