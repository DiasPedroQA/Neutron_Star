# Atoms/src/models/escritores.py
# pylint: disable=too-few-public-methods, too-many-arguments, too-many-positional-arguments

"""Implementação das estratégias de exportação de arquivos de favoritos."""

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from .entidades import FORMATOS_SAIDA, FavoritoDict

type TipoDados = list[FavoritoDict] | list[dict[str, str]]


class FormatadorBase(ABC):
    """Classe base abstrata para formatadores de exportação."""

    @abstractmethod
    def salvar(self, caminho: Path, dados: TipoDados) -> None:
        """Executa a gravação dos dados estruturados no formato específico."""


class FormatadorJSON(FormatadorBase):
    """Formatador responsável por persistir os favoritos no formato JSON formatado."""

    def salvar(self, caminho: Path, dados: TipoDados) -> None:
        """Salva a lista de favoritos em formato JSON legível."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(file=caminho, mode="w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)


class FormatadorCSV(FormatadorBase):
    """Formatador responsável por persistir os favoritos no formato CSV."""

    def salvar(self, caminho: Path, dados: TipoDados) -> None:
        """Salva a lista de favoritos em formato CSV com suporte ao Excel."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if not dados:
            return

        cabecalhos: list[str] = list(dados[0].keys())
        with open(
            file=caminho,
            mode="w",
            encoding="utf-8-sig",
            newline="",
        ) as arquivo:
            escritor: csv.DictWriter[str] = csv.DictWriter(
                f=arquivo,
                fieldnames=cabecalhos,
                delimiter=";",
            )
            escritor.writeheader()
            escritor.writerows(
                {chave: self._neutralizar_formula(str(valor)) for chave, valor in linha.items()}
                for linha in dados
            )

    @staticmethod
    def _neutralizar_formula(valor: str) -> str:
        """Evita que planilhas interpretem valores externos como fórmulas."""
        return f"'{valor}" if valor.lstrip().startswith(("=", "+", "-", "@")) else valor


class FormatadorMarkdown(FormatadorBase):
    """Formatador responsável por exportar os favoritos em formato Markdown estruturado."""

    def salvar(self, caminho: Path, dados: TipoDados) -> None:
        """Salva a lista de favoritos em formato Markdown (.md)."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        linhas: list[str] = [
            "# 📑 Favoritos Exportados\n",
            f"*Total de links processados: {len(dados)}*\n",
            "| Título | URL | Pasta | Data de Adição |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for fav in dados:
            titulo: str = str(fav.get("titulo", "Sem título")).replace("|", "-")
            url: str = str(fav.get("url", ""))
            pasta: str = str(fav.get("pasta", "Geral")).replace("|", "/")
            data: str = str(fav.get("data_adicao", "Sem data"))
            url_escapada: str = url.replace("\\", "\\\\").replace("|", "\\|").replace(")", "\\)")
            linhas.append(f"| [{titulo}]({url_escapada}) | `{url_escapada}` | {pasta} | {data} |")

        caminho.write_text("\n".join(linhas), encoding="utf-8")


class EscritorLocal:
    """Gerencia a resolução de caminhos e persistência através dos formatadores."""

    _FORMATADOR_MARKDOWN: ClassVar[FormatadorMarkdown] = FormatadorMarkdown()
    FORMATADORES: ClassVar[dict[str, FormatadorBase]] = {
        "json": FormatadorJSON(),
        "csv": FormatadorCSV(),
        "md": _FORMATADOR_MARKDOWN,
        "markdown": _FORMATADOR_MARKDOWN,
    }
    SUFIXO_PROCESSAMENTO: ClassVar[str] = "_processado"

    @classmethod
    def gerar_caminho_destino(
        cls,
        caminho_original: str | Path,
        extensao: str,
        sufixo: str = "_processado",
        pasta_saida: Path | None = None,
    ) -> Path:
        """Calcula o novo caminho do arquivo de destino."""
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
        dados: TipoDados,
        extensao: str,
        sufixo: str = "_processado",
        pasta_saida: Path | None = None,
    ) -> str:
        """Valida formato e grava o lote no arquivo de destino."""
        if not dados:
            raise ValueError("Não há dados para exportar.")

        caminho_destino: Path = self.gerar_caminho_destino(
            caminho_original=caminho_original,
            extensao=extensao,
            sufixo=sufixo,
            pasta_saida=pasta_saida,
        )
        ext_limpa: str = extensao.strip().lower().replace(".", "")

        formatador: FormatadorBase | None = self.FORMATADORES.get(ext_limpa)
        if not formatador or ext_limpa not in FORMATOS_SAIDA:
            formatos_suportados: list[str] = list(self.FORMATADORES.keys())
            formato: str = f"Formato '.{ext_limpa}' não suportado."
            escolha: str = f" Escolha entre: {formatos_suportados}."
            raise ValueError(formato + escolha)

        formatador.salvar(caminho=caminho_destino, dados=dados)
        return str(caminho_destino)
