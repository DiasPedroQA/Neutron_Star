#!/usr/bin/env python3
"""
Neutron Star — Buscador de arquivos por prefixo + data (opcional).

Arquivos devem ter o formato:
    <prefixo>_<data>.<extensão>
Onde:
    - prefixo: obrigatório (ex: "favoritos", "bookmarks").
    - data: opcional, no formato M_D_AA (ex.: "6_23_26"), tolerante a
      zero à esquerda e a separador ('-', '_' ou '.').
    - extensão: obrigatoriamente ".html".

A data também pode ser informada em qualquer formato reconhecível
(ex.: "2026_06_23", "23/06/2026", "23 de junho de 2026") — o CLI a
converte automaticamente para o formato canônico via `normalizar_data`.
"""

from __future__ import annotations

import argparse
import sys

from src.controllers.buscador import Buscador
from src.models.arquivo import Arquivo
from src.utils.system_tools import normalizar_data


def _construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos de linha de comando do CLI."""
    parser = argparse.ArgumentParser(
        prog="neutron",
        description="Busca arquivos por prefixo e data (opcional) a partir da pasta do usuário.",
    )
    parser.add_argument(
        "--prefixo",
        "-p",
        required=True,
        action="append",
        help="Prefixo do arquivo a buscar. Pode ser repetido para aceitar aliases (ex.: -p favoritos -p bookmarks).",
    )
    parser.add_argument(
        "--data",
        "-d",
        default=None,
        help="Data do arquivo em qualquer formato reconhecível "
        "(ex.: '6_23_26', '2026_06_23', '23/06/2026', '23 de junho de 2026'). "
        "Se omitida, aceita qualquer data ou nenhuma.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada do CLI (também usado pelo entry point `neutron`)."""
    parser: argparse.ArgumentParser = _construir_parser()
    args: argparse.Namespace = parser.parse_args(args=argv)

    data_normalizada: str | None = None
    if args.data:
        try:
            data_normalizada = normalizar_data(data=args.data)
        except ValueError as erro:
            print(f"Data inválida: {erro}", file=sys.stderr)
            return 1

    prefixo: str | list[str] = args.prefixo[0] if len(args.prefixo) == 1 else args.prefixo

    buscador = Buscador(prefixo=prefixo, data=data_normalizada)
    arquivos: list[Arquivo] = buscador.buscar_arquivos()

    print(f"Arquivos encontrados: {len(arquivos)}")
    for a in arquivos:
        print(f"{a.caminho.name} ({a.tamanho} bytes) - Oculto? {a.oculto}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
