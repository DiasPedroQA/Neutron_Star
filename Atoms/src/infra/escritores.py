# Atoms/src/infra/escritores.py
# pylint: disable=too-few-public-methods

"""Implementação concreta das estratégias de exportação física de arquivos."""

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from ..aplicacao.portas import EscritorPort

TipoValor = str | float | bool


class FormatadorBase(ABC):
    @abstractmethod
    def salvar(self, caminho: Path, dados: list[dict[str, TipoValor]]) -> None:
        """Executa a gravação dos dados estruturados no formato específico."""


class FormatadorJSON(FormatadorBase):
    def salvar(self, caminho: Path, dados: list[dict[str, TipoValor]]) -> None:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(file=caminho, mode="w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)


class FormatadorCSV(FormatadorBase):
    def salvar(self, caminho: Path, dados: list[dict[str, TipoValor]]) -> None:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if not dados:
            return

        cabecalhos: list[str] = list(dados[0].keys())
        with open(file=caminho, mode="w", encoding="utf-8-sig", newline="") as arquivo:
            escritor: csv.DictWriter[str] = csv.DictWriter(
                arquivo, fieldnames=cabecalhos, delimiter=";"
            )
            escritor.writeheader()
            escritor.writerows(dados)


class EscritorLocal(EscritorPort):
    FORMATADORES: ClassVar[dict[str, FormatadorJSON | FormatadorCSV]] = {
        "json": FormatadorJSON(),
        "csv": FormatadorCSV(),
    }
    sufixo_processamento: str = "_processado"

    @staticmethod
    def gerar_caminho_destino(
        caminho_original: str | Path,
        extensao: str,
        sufixo: str = sufixo_processamento,
        pasta_saida: Path | None = None,
    ) -> Path:
        """Calcula o novo caminho do arquivo de destino.

        Se ``pasta_saida`` for informada, grava lá; caso contrário, grava ao lado
        do original (comportamento legado).
        """
        caminho_orig: Path = Path(caminho_original).expanduser().resolve()
        ext_limpa: str = extensao.strip().lower().replace(".", "")
        novo_nome: str = f"{caminho_orig.stem}{sufixo}.{ext_limpa}"

        if pasta_saida is not None:
            pasta: Path = Path(pasta_saida).expanduser().resolve()
            return pasta / novo_nome

        return caminho_orig.parent / novo_nome

    def salvar_lote(
        self,
        caminho_original: Path,
        dados: list[dict[str, TipoValor]],
        extensao: str,
        sufixo: str = sufixo_processamento,
        pasta_saida: Path | None = None,
    ) -> str:
        if not dados:
            raise ValueError("Não há dados para exportar.")

        caminho_destino: Path = self.gerar_caminho_destino(
            caminho_original=caminho_original,
            extensao=extensao,
            sufixo=sufixo,
            pasta_saida=pasta_saida,
        )
        ext_limpa: str = extensao.strip().lower().replace(".", "")

        formatador = self.FORMATADORES.get(ext_limpa)
        if not formatador:
            formatos_suportados: list[str] = list(self.FORMATADORES.keys())
            raise ValueError(
                f"Formato '.{ext_limpa}' não suportado. Escolha entre: {formatos_suportados}"
            )

        formatador.salvar(caminho=caminho_destino, dados=dados)
        return str(caminho_destino)