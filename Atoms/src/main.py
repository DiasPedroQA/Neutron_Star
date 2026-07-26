#!/usr/bin/env python3

"""Orquestrador de busca e extração de bookmarks.

Modos de operação (subcomandos):
- buscar: apenas localiza arquivos e lista.
- extrair: busca + extrai a árvore de bookmarks (mostra estatísticas).
- exportar: pipeline completo (buscar -> selecionar -> extrair -> exportar).
- lote: processa todos os arquivos encontrados, exportando cada um individualmente.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Iterable
from pathlib import Path

from aplicacao.casos_de_uso.processar_lote import processar_arquivos_em_lote
from aplicacao.etapas import (
    etapa_buscar,
    etapa_exportar,
    etapa_extrair,
    etapa_selecionar_arquivo,
)
from aplicacao.tipos import ParametrosBusca
from dominio.excecoes import ErroBookmarks

# --------------------------------------------
# Constantes
# --------------------------------------------
DEFAULT_FORMATOS: list[str] = [".json", ".csv"]
COMANDO_PADRAO = "exportar"

# --------------------------------------------
# Tipos e constantes
# --------------------------------------------
EtapaPipeline = Callable[[ParametrosBusca], ParametrosBusca]

ETAPAS_DISPONIVEIS: dict[str, EtapaPipeline] = {
    "buscar": etapa_buscar,
    "selecionar_arquivo": etapa_selecionar_arquivo,
    "extrair": etapa_extrair,
    "exportar": etapa_exportar,
}

# Pipeline padrão (ordem)
PIPELINE_PADRAO: list[str] = ["buscar", "selecionar_arquivo", "extrair", "exportar"]


# --------------------------------------------
# Construção do parser com subcomandos
# --------------------------------------------
def _adicionar_opcoes_comuns(parser: argparse.ArgumentParser) -> None:
    """Adiciona as opções comuns (diretorio, extensao, chaves) a um subparser."""
    parser.add_argument(
        "--diretorio",
        type=Path,
        default=Path.home(),
        help="Diretório onde buscar (padrão: home).",
    )
    parser.add_argument(
        "--extensao",
        default=".html",
        help="Extensão dos arquivos de bookmarks a buscar (ex: .html)",
    )
    parser.add_argument(
        "--lote",
        action="store_true",
        help="Processar arquivos em lote",
    )
    parser.add_argument(
        "--chaves",
        nargs="*",
        default=["favoritos", "bookmarks"],
        help="Palavras-chave no nome do arquivo.",
    )


def construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos com subcomandos."""
    parser = argparse.ArgumentParser(
        prog="neutron",
        description="Ferramenta para extrair e exportar bookmarks.",
        add_help=True,
    )
    subparsers: argparse._SubParsersAction = parser.add_subparsers(
        dest="comando",
        required=False,  # agora não obrigatório; definimos padrão depois
        help="Subcomando a executar",
    )

    # ---- Comando: buscar ----
    buscar_parser = subparsers.add_parser(
        name="buscar",
        help="Busca arquivos de bookmarks e exibe a lista.",
    )
    _adicionar_opcoes_comuns(parser=buscar_parser)
    buscar_parser.add_argument(
        "--exigir-data",
        action="store_true",
        help="Exige data no nome do arquivo.",
    )

    # ---- Comando: extrair ----
    extrair_parser: argparse.ArgumentParser = subparsers.add_parser(
        name="extrair",
        help="Busca, seleciona o primeiro arquivo e extrai a árvore (mostra estatísticas).",
    )
    _adicionar_opcoes_comuns(parser=extrair_parser)
    extrair_parser.add_argument(
        "--indice",
        type=int,
        default=0,
        help="Índice do arquivo a processar (padrão: 0).",
    )

    # ---- Comando: exportar ----
    exportar_parser = subparsers.add_parser(
        name="exportar",
        help="Pipeline completo: buscar -> selecionar -> extrair -> exportar.",
    )
    _adicionar_opcoes_comuns(parser=exportar_parser)
    exportar_parser.add_argument(
        "--indice",
        type=int,
        default=0,
        help="Índice do arquivo a processar (padrão: 0).",
    )
    exportar_parser.add_argument(
        "--formatos",
        nargs="*",
        default=DEFAULT_FORMATOS,
        help="Formatos de exportação (padrão: .json .csv).",
    )
    exportar_parser.add_argument(
        "--saida",
        default="resultados",
        help="Diretório de saída (padrão: resultados).",
    )

    # ---- Comando: lote ----
    lote_parser = subparsers.add_parser(
        name="lote",
        help="Processa todos os arquivos encontrados, exportando cada um individualmente.",
    )
    _adicionar_opcoes_comuns(lote_parser)
    lote_parser.add_argument(
        "--formatos",
        nargs="*",
        default=DEFAULT_FORMATOS,
        help="Formatos de exportação (padrão: .json .csv).",
    )
    lote_parser.add_argument(
        "--saida",
        default="resultados_lote",
        help="Diretório de saída para os arquivos do lote (padrão: resultados_lote).",
    )

    return parser


# --------------------------------------------
# Funções auxiliares para montar contexto
# --------------------------------------------
def montar_contexto_base(args: argparse.Namespace) -> ParametrosBusca:
    """Monta um contexto básico a partir dos argumentos comuns."""
    contexto: ParametrosBusca = {
        "diretorio": args.diretorio,
        "extensao": args.extensao,
        "chaves": args.chaves,
        "exigir_data": getattr(args, "exigir_data", False),
        "indice_arquivo": getattr(args, "indice", 0),
        "formatos_exportacao": getattr(args, "formatos", DEFAULT_FORMATOS),
        "diretorio_saida": getattr(args, "saida", "."),
    }
    return contexto


# --------------------------------------------
# Executores dos subcomandos
# --------------------------------------------
def executar_buscar(contexto: ParametrosBusca) -> None:
    """Executa apenas a etapa de busca e exibe os resultados."""
    try:
        resultado: ParametrosBusca = etapa_buscar(contexto_busca=contexto)
        arquivos: list[Path] = resultado.get("arquivos_encontrados", [])
        print(f"Encontrados {len(arquivos)} arquivos:")
        for i, arq in enumerate(arquivos):
            print(f"  [{i}] {arq}")
    except ErroBookmarks as e:
        print(f"Erro na busca: {e}")


def executar_extrair(contexto: ParametrosBusca) -> None:
    """Executa busca, seleção e extração, exibindo estatísticas da árvore."""
    try:
        # Busca
        resultado: ParametrosBusca = etapa_buscar(contexto_busca=contexto)
        arquivos: list[Path] = resultado.get("arquivos_encontrados", [])
        if not arquivos:
            print("Nenhum arquivo encontrado.")
            return
        # Seleciona
        resultado = etapa_selecionar_arquivo(contexto_busca=resultado)
        # Extrai
        resultado = etapa_extrair(contexto_busca=resultado)
        if raiz := resultado.get("raiz_bookmarks"):
            total: int = len(raiz.filhos_da_pasta)  # ajuste conforme sua estrutura
            print(f"Árvore extraída com {total} bookmarks (raiz: {raiz.nome})")
        else:
            print("Nenhuma raiz extraída.")
    except (ErroBookmarks, ValueError) as e:
        print(f"Erro: {e}")


def executar_exportar(contexto: ParametrosBusca) -> None:
    """Executa o pipeline completo."""
    executar_pipeline(contexto, etapas=PIPELINE_PADRAO)


def executar_lote(contexto: ParametrosBusca) -> None:
    """Executa o modo lote: processa todos os arquivos."""
    try:
        resultado: ParametrosBusca = etapa_buscar(contexto_busca=contexto)
        arquivos: list[Path] = resultado.get("arquivos_encontrados", [])
        if not arquivos:
            print("Nenhum arquivo encontrado.")
            return

        falhas: dict[Path, ErroBookmarks] = processar_arquivos_em_lote(
            arquivos=arquivos,
            formatos=contexto.get("formatos_exportacao", DEFAULT_FORMATOS),
            diretorio_saida=Path(contexto.get("diretorio_saida", ".")),
        )
        sucesso: int = len(arquivos) - len(falhas)
        print(f"Lote concluído: {sucesso}/{len(arquivos)} processados com sucesso.")
        for arq, erro in falhas.items():
            print(f"  [FALHA] {arq}: {erro}")
    except ErroBookmarks as e:
        print(f"Erro no lote: {e}")


def executar_pipeline(contexto: ParametrosBusca, etapas: list[str]) -> None:
    """Executa uma sequência de etapas, propagando o contexto."""
    for nome in etapas:
        etapa: EtapaPipeline | None = ETAPAS_DISPONIVEIS.get(nome)
        if etapa is None:
            print(f"Etapa '{nome}' desconhecida -> será ignorada.")
            continue
        try:
            contexto = etapa(contexto)
        except (ErroBookmarks, ValueError) as e:
            print(f"Erro na etapa '{nome}': {e}")
            break


# --------------------------------------------
# Main
# --------------------------------------------
def main(argv: Iterable[str] | None = None) -> None:
    """Ponto de entrada principal."""
    parser: argparse.ArgumentParser = construir_parser()
    args: argparse.Namespace = parser.parse_args(args=argv)

    # Se nenhum comando foi fornecido, usa o padrão
    if not args.comando:
        args.comando = COMANDO_PADRAO
        # Como o parser não tem default para comando, precisamos simular
        # chamando o subparser correspondente. Para simplificar, reparseamos
        # com o comando padrão? Melhor: ajustar manualmente.
        # Vamos criar um Namespace com o comando padrão e mesclar os args.
        # Mas é mais fácil executar diretamente a função exportar com contexto vazio.
        contexto: ParametrosBusca = {
            "diretorio": Path.home(),
            "extensao": ".html",
            "chaves": ["favoritos", "bookmarks"],
            "exigir_data": False,
            "indice_arquivo": 0,
            "formatos_exportacao": DEFAULT_FORMATOS,
            "diretorio_saida": "resultados",
        }
        executar_exportar(contexto)
        return

    # Monta o contexto base a partir dos argumentos
    contexto = montar_contexto_base(args)

    # Mapeia subcomando para função executora
    executores: dict[str, Callable[..., None]] = {
        "buscar": executar_buscar,
        "extrair": executar_extrair,
        "exportar": executar_exportar,
        "lote": executar_lote,
    }

    if executor := executores.get(args.comando):
        executor(contexto)
    else:
        print(f"Comando '{args.comando}' não reconhecido.")


# --------------------------------------------
# Execução programática (exemplo)
# --------------------------------------------
if __name__ == "__main__":
    main(argv=sys.argv[1:])  # se nenhum argumento, executa exportar com padrões
