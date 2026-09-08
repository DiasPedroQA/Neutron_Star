# Atoms/infra/escritores.py
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
    """Classe abstrata de base (Contrato) para as estratégias de formato."""

    @abstractmethod
    def salvar(self, caminho: Path, dados: list[dict[str, TipoValor]]) -> None:
        """Executa a gravação dos dados estruturados no formato específico."""


class FormatadorJSON(FormatadorBase):
    """Estratégia de exportação para arquivos no formato JSON."""

    def salvar(self, caminho: Path, dados: list[dict[str, TipoValor]]) -> None:
        """Grava os dados mapeados em arquivo JSON formatado em UTF-8."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(file=caminho, mode="w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)


class FormatadorCSV(FormatadorBase):
    """Estratégia de exportação para arquivos no formato CSV."""

    def salvar(self, caminho: Path, dados: list[dict[str, TipoValor]]) -> None:
        """Grava os dados em formato CSV adaptado para o Excel em português.

        Aplica a codificação 'utf-8-sig' (BOM) e delimitador ';' para garantir
        compatibilidade instantânea na abertura de acentos no Excel Windows.
        """
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
    """Implementação física de gerenciamento de escrita e caminhos de arquivo."""

    FORMATADORES: ClassVar[dict[str, FormatadorJSON | FormatadorCSV]] = {
        "json": FormatadorJSON(),
        "csv": FormatadorCSV(),
    }

    @staticmethod
    def gerar_caminho_destino(
        caminho_original: str | Path,
        extensao: str,
        sufixo: str = "_processado",
    ) -> Path:
        """Calcula o novo caminho do arquivo de destino na mesma pasta pai."""
        caminho_orig: Path = Path(caminho_original).expanduser().resolve()
        ext_limpa: str = extensao.strip().lower().replace(".", "")
        novo_nome: str = f"{caminho_orig.stem}{sufixo}.{ext_limpa}"
        return caminho_orig.parent / novo_nome

    def salvar_lote(
        self,
        caminho_original: Path,
        dados: list[dict[str, TipoValor]],
        extensao: str,
        sufixo: str = "_processado",
    ) -> str:
        """Calcula caminhos, busca a estratégia correspondente e grava no disco."""
        if not dados:
            raise ValueError("Não há dados para exportar.")

        caminho_destino: Path = self.gerar_caminho_destino(
            caminho_original=caminho_original, extensao=extensao, sufixo=sufixo
        )
        ext_limpa: str = extensao.strip().lower().replace(".", "")

        formatador: FormatadorJSON | FormatadorCSV | None = self.FORMATADORES.get(ext_limpa)
        if not formatador:
            formatos_suportados: list[str] = list(self.FORMATADORES.keys())
            raise ValueError(
                f"Formato '.{ext_limpa}' não suportado. Escolha entre: {formatos_suportados}"
            )

        formatador.salvar(caminho=caminho_destino, dados=dados)
        return str(caminho_destino)
