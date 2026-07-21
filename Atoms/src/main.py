# main.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Orquestrador de busca e extração de bookmarks.

Dois modos de operação:
- Padrão: busca arquivos, seleciona um (por índice) e roda o pipeline completo
  (buscar -> selecionar_arquivo -> extrair -> exportar).
- Lote (--lote): busca arquivos e processa TODOS eles, cada um exportado
  individualmente, sem parar no primeiro erro.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
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

EtapaPipeline = Callable[[ParametrosBusca], ParametrosBusca]

ETAPAS_DISPONIVEIS: dict[str, EtapaPipeline] = {
    "buscar": etapa_buscar,
    "selecionar_arquivo": etapa_selecionar_arquivo,
    "extrair": etapa_extrair,
    "exportar": etapa_exportar,
}


def construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos de linha de comando.

    Returns:
        argparse.ArgumentParser: Parser configurado com todas as opções da CLI.
    """
    parser = argparse.ArgumentParser(
        prog="neutron",
        description="Busca, extrai e exporta bookmarks em formato Netscape HTML.",
    )
    parser.add_argument(
        "--diretorio",
        type=Path,
        default=Path.home(),
        help="Diretório onde buscar os arquivos de bookmarks (padrão: home do usuário).",
    )
    parser.add_argument(
        "--extensao",
        default=".html",
        help="Extensão dos arquivos a buscar (padrão: .html).",
    )
    parser.add_argument(
        "--chaves",
        nargs="*",
        default=["favoritos", "bookmarks"],
        help="Palavras que devem aparecer no nome do arquivo (padrão: favoritos bookmarks).",
    )
    parser.add_argument(
        "--exigir-data",
        action="store_true",
        help="Exige que o nome do arquivo contenha uma data reconhecível.",
    )
    parser.add_argument(
        "--formatos",
        nargs="*",
        default=[".json", ".csv"],
        help="Formatos de exportação desejados (padrão: .json .csv).",
    )
    parser.add_argument(
        "--saida",
        default="resultados",
        help="Diretório de saída dos arquivos exportados (padrão: resultados).",
    )
    parser.add_argument(
        "--indice",
        type=int,
        default=0,
        help="Índice do arquivo a processar no modo padrão (padrão: 0).",
    )
    parser.add_argument(
        "--lote",
        action="store_true",
        help="Processa TODOS os arquivos encontrados, em vez de selecionar apenas um.",
    )
    return parser


def montar_contexto(args: argparse.Namespace) -> ParametrosBusca:
    """Converte os argumentos de linha de comando em um ParametrosBusca inicial.

    Args:
        args: Argumentos já interpretados pelo parser da CLI.

    Returns:
        ParametrosBusca: Contexto inicial pronto para alimentar o pipeline.
    """
    return ParametrosBusca(
        diretorio=args.diretorio,
        extensao=args.extensao,
        chaves=args.chaves,
        exigir_data=args.exigir_data,
        indice_arquivo=args.indice,
        formatos_exportacao=args.formatos,
        diretorio_saida=args.saida,
    )


def executar_modo_lote(contexto: ParametrosBusca) -> None:
    """Busca arquivos e processa todos eles, reportando falhas sem interromper o lote.

    Args:
        contexto: Contexto com os parâmetros de busca e exportação já definidos.
    """
    contexto = etapa_buscar(contexto_busca=contexto)
    arquivos: list[Path] = contexto.get("arquivos_encontrados", [])
    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return

    falhas: dict[Path, ErroBookmarks] = processar_arquivos_em_lote(
        arquivos=arquivos,
        formatos=contexto.get("formatos_exportacao", [".json"]),
        diretorio_saida=Path(contexto.get("diretorio_saida", ".")),
    )

    sucesso: int = len(arquivos) - len(falhas)
    print(f"Lote concluído: {sucesso}/{len(arquivos)} arquivo(s) processado(s) com sucesso.")
    for arquivo, erro in falhas.items():
        print(f"  [FALHA] {arquivo}: {erro}")


def executar_pipeline(contexto: ParametrosBusca, etapas: list[str]) -> None:
    """Executa as etapas em sequência, propagando o contexto.

    Args:
        contexto: Contexto inicial (ParametrosBusca) a ser passado adiante.
        etapas: Nomes das etapas a executar, na ordem desejada.
    """
    for nome in etapas:
        etapa: EtapaPipeline | None = ETAPAS_DISPONIVEIS.get(nome)
        if etapa is None:
            print(f"Etapa desconhecida: '{nome}' — ignorada.")
            continue

        try:
            contexto = etapa(contexto)
        except (ErroBookmarks, ValueError) as erro:
            print(f"Erro na etapa '{nome}': {erro}")
            break


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada: interpreta a linha de comando e executa o modo escolhido.

    Args:
        argv: Argumentos de linha de comando; se None, usa sys.argv (comportamento padrão).
    """
    args: argparse.Namespace = construir_parser().parse_args(argv)
    contexto: ParametrosBusca = montar_contexto(args=args)

    if args.lote:
        executar_modo_lote(contexto=contexto)
        return

    etapas: list[str] = ["buscar", "selecionar_arquivo", "extrair", "exportar"]
    executar_pipeline(contexto=contexto, etapas=etapas)


if __name__ == "__main__":
    main()
