"""
Adaptador de linha de comando (CLI).

Fino de propósito: apenas interpreta argumentos e chama os casos de
uso da camada de aplicação. Nenhuma regra de negócio mora aqui.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

from pandas import DataFrame

from src.aplicacao.casos_de_uso.buscar_bookmarks import gerar_relatorio
from src.aplicacao.casos_de_uso.converter_bookmarks import (
    adicionar_favicon_url,
    converter_arquivos,
    parse_bookmarks_html,
)

logger: logging.Logger = logging.getLogger(name=__name__)


def _comando_buscar(args: argparse.Namespace) -> int:
    """Executa o comando de busca de arquivos de bookmarks com base nos argumentos da linha de comando.

    Gera um relatório dos arquivos encontrados na pasta informada,
    imprime um resumo de sucessos e erros e retorna um código de saída adequado ao resultado.

    Args:
        args: Namespace com os argumentos da CLI, incluindo a pasta de origem onde serão buscados os arquivos de bookmarks.

    Returns:
        Código de saída inteiro, onde 0 indica que todos os arquivos foram processados com sucesso e 1 indica que houve pelo menos um erro.
    """
    relatorio: list[dict[str, Any]] = gerar_relatorio(pasta_entrada=Path(args.origem))
    sucessos: list[dict[str, Any]] = [m for m in relatorio if m["status"] == "sucesso"]
    erros: list[dict[str, Any]] = [m for m in relatorio if m["status"] == "erro"]

    print(f"Encontrados: {len(relatorio)} arquivo(s)")
    for meta in relatorio:
        if meta["status"] == "sucesso":
            print(f"  ✅ {meta['nome']}: {meta['itens_raiz']} raiz, {meta['total_links']} links")
        else:
            print(f"  ❌ {meta['nome']}: {meta['erro']}")
    print(f"Total: {len(relatorio)}, sucesso: {len(sucessos)}, erros: {len(erros)}")
    return 1 if erros else 0


def _comando_converter(args: argparse.Namespace) -> int:
    """Executa o comando de conversão de arquivos de bookmarks
    a partir dos argumentos da linha de comando.

    Constrói um parser de bookmarks com opções de ícone e favicon,
    aplica a conversão para os formatos solicitados e informa o
    resultado ao usuário via saída padrão.

    Args:
        args: Namespace com os argumentos da CLI, incluindo arquivos de entrada,
        formatos de saída e opções de favicon/ícone.

    Returns:
        Código de saída inteiro, onde 0 indica conversão bem-sucedida e 1 indica que nenhum arquivo foi gerado.
    """
    caminhos: list[Path] = [Path(p) for p in args.arquivos]

    def parser(caminho: Path) -> DataFrame:
        """Constrói um DataFrame de bookmarks a partir de um arquivo HTML conforme opções da linha de comando.

        Aplica o parse do HTML, opcionalmente inclui dados de ícones e adiciona a URL de favicon quando solicitado.

        Args:
            caminho: Caminho para o arquivo HTML de bookmarks que será convertido em tabela.

        Returns:
            Um DataFrame contendo os bookmarks extraídos, possivelmente enriquecido com colunas de ícone e favicon.
        """
        df: DataFrame = parse_bookmarks_html(html_path=caminho, extrair_icone=args.icone)
        return adicionar_favicon_url(df) if args.favicon else df

    gerados: list[Path] = converter_arquivos(
        lista_paths=caminhos,
        parser=parser,
        output_formats=args.formatos,
        sufixo_saida=args.sufixo,
    )
    if not gerados:
        print("Nenhum arquivo gerado.")
        return 1
    print(f"Gerado(s) {len(gerados)} arquivo(s):")
    for caminho in gerados:
        print(f"  {caminho}")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    """Constrói o parser de linha de comando para os comandos de busca e conversão de bookmarks.

    Define os subcomandos disponíveis, seus argumentos e o vínculo entre cada comando
    e a função que o executa, permitindo a interpretação consistente da CLI.

    Returns:
        Um objeto ArgumentParser configurado com os subparsers e opções necessárias para a ferramenta de bookmarks.
    """
    parser = argparse.ArgumentParser(
        prog="bookmarks",
        description="Descobre, lê e converte arquivos de bookmarks (Netscape).",
    )
    subparsers: argparse._SubParsersAction = parser.add_subparsers(dest="comando", required=True)

    p_buscar: argparse.ArgumentParser = subparsers.add_parser(
        "buscar", help="Busca arquivos de bookmarks em uma pasta e gera um relatório."
    )
    p_buscar.add_argument(
        "origem",
        nargs="?",
        default=str(Path.home()),
        help="Pasta onde procurar (padrão: pasta do usuário).",
    )
    p_buscar.set_defaults(func=_comando_buscar)

    p_converter: argparse.ArgumentParser = subparsers.add_parser(
        "converter", help="Converte arquivos de bookmarks para outros formatos."
    )
    p_converter.add_argument("arquivos", nargs="+", help="Um ou mais arquivos HTML de bookmarks.")
    p_converter.add_argument(
        "--formatos",
        nargs="+",
        default=[".csv", ".json"],
        help="Extensões de saída desejadas (padrão: .csv .json).",
    )
    p_converter.add_argument(
        "--sufixo", default=None, help="Sufixo adicionado ao nome do arquivo gerado."
    )
    p_converter.add_argument(
        "--favicon", action="store_true", help="Adiciona coluna com URL do favicon."
    )
    p_converter.add_argument(
        "--icone", action="store_true", help="Inclui a coluna 'icon' (base64 original)."
    )
    p_converter.set_defaults(func=_comando_converter)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI de bookmarks responsável por interpretar argumentos e despachar comandos.

    Constrói o parser de linha de comando, faz o parse da lista de argumentos recebida e
    executa a função associada ao subcomando escolhido, retornando seu código de saída.

    Args:
        argv: Lista opcional de argumentos da linha de comando; se None, usa os argumentos de sys.argv.

    Returns:
        Código de saída inteiro retornado pela função do comando executado.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser: argparse.ArgumentParser = construir_parser()
    args: argparse.Namespace = parser.parse_args(args=argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
