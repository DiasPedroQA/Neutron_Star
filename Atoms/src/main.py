#!/usr/bin/env python3
"""
Neutron Star — Buscador de arquivos por metadados.

Ponto de entrada principal. Detecta o sistema operacional, configura
o buscador e executa uma busca com critérios fornecidos via CLI.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.control.buscador import BuscadorSistemaArquivos, CriteriosBusca, FiltroTexto
from src.control.identificador import IdentificadorSistema
from src.model.configuracoes import ConfigApp
from src.model.resultado_busca import ResultadoBusca
from src.view.apresentador import exibir_resultado

# ---------------------------------------------------------------------------
# Configuração de logging simples
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log: logging.Logger = logging.getLogger(name="neutron_star")

# Banner exibido no modo verboso
BANNER = r"""
   _   _      _                  _   ____  _
  | \ | | ___| |_ _ __ ___  _ __| |_/ ___|| |_ __ _ _ __
  |  \| |/ _ | __| '__/ _ \| '__| __\___ \| __/ _` | '__|
  | |\  |  __| |_| | | (_) | |  | |_ ___) | || (_| | |
  |_| \_|\___|\__|_|  \___/|_|   \__|____/ \__\__,_|_|
"""


def construir_argumentos() -> argparse.Namespace:
    """Configura e retorna os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Neutron Star — Busca arquivos por nome, tipo e metadados.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemplo: python -m src.main --consulta 'relatório' --extensoes .pdf .docx",
    )

    # Grupo de busca
    busca: argparse._ArgumentGroup = parser.add_argument_group(title="Critérios de busca")
    busca.add_argument(
        "-r",
        "--raiz",
        type=Path,
        default=Path.home(),
        help="Diretório raiz da busca (padrão: home do usuário).",
    )
    busca.add_argument(
        "-c",
        "--consulta",
        default="",
        help="Substring para buscar no nome do arquivo/diretório.",
    )
    busca.add_argument(
        "-g",
        "--glob",
        default=None,
        help='Padrão glob para filtrar nomes (ex.: "*.pdf").',
    )
    busca.add_argument(
        "--regex",
        default=None,
        help="Expressão regular para o nome do arquivo.",
    )
    busca.add_argument(
        "-e",
        "--extensoes",
        nargs="*",
        default=None,
        help="Lista de extensões desejadas (ex.: .pdf .txt).",
    )
    busca.add_argument(
        "--mime",
        nargs="*",
        default=None,
        help="Tipos MIME aceitos (ex.: text/plain application/pdf).",
    )
    busca.add_argument(
        "--min-tamanho",
        type=int,
        default=None,
        help="Tamanho mínimo do arquivo em bytes.",
    )
    busca.add_argument(
        "--max-tamanho",
        type=int,
        default=None,
        help="Tamanho máximo do arquivo em bytes.",
    )
    busca.add_argument(
        "--modificado-apos",
        default=None,
        help="Data mínima de modificação (formato: AAAA-MM-DD).",
    )
    busca.add_argument(
        "--modificado-antes",
        default=None,
        help="Data máxima de modificação (formato: AAAA-MM-DD).",
    )
    busca.add_argument(
        "--apenas-legiveis",
        action="store_true",
        help="Restringir a arquivos legíveis.",
    )
    busca.add_argument(
        "--apenas-executaveis",
        action="store_true",
        help="Restringir a arquivos executáveis.",
    )
    busca.add_argument(
        "-d",
        "--incluir-diretorios",
        action="store_true",
        help="Incluir diretórios nos resultados.",
    )

    # Grupo de configuração do buscador
    config: argparse._ArgumentGroup = parser.add_argument_group(title="Configuração do buscador")
    config.add_argument(
        "--max-profundidade",
        type=int,
        default=-1,
        help="Profundidade máxima de busca (-1 = ilimitado).",
    )
    config.add_argument(
        "--seguir-symlinks",
        action="store_true",
        help="Seguir links simbólicos.",
    )
    config.add_argument(
        "--mostrar-ocultos",
        action="store_true",
        help="Incluir arquivos e pastas ocultos.",
    )
    config.add_argument(
        "--calcular-hash",
        action="store_true",
        help="Calcular hash SHA-256 de cada arquivo (mais lento).",
    )
    config.add_argument(
        "--case-sensitive",
        action="store_true",
        default=None,
        help="Forçar diferenciação de maiúsculas/minúsculas.",
    )

    # Grupo de saída
    saida: argparse._ArgumentGroup = parser.add_argument_group(title="Saída e exibição")
    saida.add_argument(
        "-n",
        "--max-itens",
        type=int,
        default=100,
        help="Número máximo de itens exibidos (padrão: 100).",
    )
    saida.add_argument(
        "--texto-puro",
        action="store_true",
        help="Usar saída em texto puro, sem rich.",
    )
    saida.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Caminho para salvar o resultado em JSON.",
    )
    saida.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Exibir informações de diagnóstico.",
    )

    return parser.parse_args()


def montar_criterios(args: argparse.Namespace) -> CriteriosBusca:
    """Converte argumentos da CLI em um objeto CriteriosBusca."""
    # Datas
    mod_apos: datetime | None = None
    mod_antes: datetime | None = None
    if args.modificado_apos:
        mod_apos = datetime.strptime(args.modificado_apos, "%Y-%m-%d")
    if args.modificado_antes:
        mod_antes = datetime.strptime(args.modificado_antes, "%Y-%m-%d")

    filtro_nome: FiltroTexto | None = FiltroTexto(regex=args.regex) if args.regex else None
    # Filtro de caminho (não exposto na CLI ainda, mas podemos deixar None)

    return CriteriosBusca(
        consulta=args.consulta,
        filtro_nome=filtro_nome,
        padrao_glob=args.glob,
        extensoes=args.extensoes,
        tipos_mime=args.mime,
        tamanho_min=args.min_tamanho,
        tamanho_max=args.max_tamanho,
        modificado_apos=mod_apos,
        modificado_antes=mod_antes,
        apenas_legiveis=args.apenas_legiveis,
        apenas_executaveis=args.apenas_executaveis,
        incluir_diretorios=args.incluir_diretorios,
        incluir_arquivos=True,  # sempre incluímos arquivos, a menos que só diretórios?
    )


def aplicar_config_cli(config: ConfigApp, args: argparse.Namespace) -> None:
    """Ajusta a configuração base com opções da linha de comando."""
    if args.max_profundidade != -1:
        config.profundidade_maxima = args.max_profundidade
    if args.seguir_symlinks:
        config.seguir_symlinks = True
    if args.mostrar_ocultos:
        config.ignorar_ocultos = False
    if args.calcular_hash:
        config.calcular_hashes = True
    if args.case_sensitive is not None:
        config.case_sensitive = args.case_sensitive


def salvar_resultado_json(resultado: ResultadoBusca, caminho: Path) -> None:
    """Salva o resultado em um arquivo JSON."""
    try:
        with open(file=caminho, mode="w", encoding="utf-8") as f:
            json.dump(resultado.para_dict(), f, indent=2, ensure_ascii=False)
        log.info("Resultado salvo em %s", caminho)
    except OSError as e:
        log.error("Erro ao salvar resultado: %s", e)


def main() -> None:
    """Função principal."""
    args: argparse.Namespace = construir_argumentos()

    if args.verbose:
        log.setLevel(logging.DEBUG)
        print(BANNER)

    log.info("Iniciando Neutron Star")
    log.debug("Argumentos recebidos: %s", args)

    # Etapa 1: identificar SO e gerar configuração
    identificador = IdentificadorSistema()
    config: ConfigApp = identificador.gerar_config()
    log.info("SO detectado: %s", identificador.info.nome_so)
    log.debug("Case sensitive: %s", config.case_sensitive)

    # Aplicar sobrescritas da CLI na configuração
    aplicar_config_cli(config, args)

    # Montar critérios de busca
    criterios: CriteriosBusca = montar_criterios(args)
    log.debug("Critérios: %s", criterios)

    # Instanciar buscador
    buscador: BuscadorSistemaArquivos = BuscadorSistemaArquivos(config=config)

    # Validar raiz
    raiz: Path = args.raiz
    if not raiz.exists():
        log.error("O diretório %s não existe.", raiz)
        sys.exit(1)
    if not raiz.is_dir():
        log.error("O caminho %s não é um diretório.", raiz)
        sys.exit(1)

    log.info("Iniciando busca em %s...", raiz)
    try:
        resultado: ResultadoBusca = buscador.buscar(raiz=raiz, criterios=criterios)
    except PermissionError as e:
        log.error("Sem permissão para acessar %s: %s", raiz, e)
        sys.exit(1)

    log.info("Busca concluída: %d itens encontrados.", resultado.total_encontrado)

    # Exibir resultado
    exibir_resultado(
        resultado=resultado,
        max_itens=args.max_itens,
        nome_so=identificador.info.nome_so,
    )

    # Salvar em arquivo, se solicitado
    if args.output:
        salvar_resultado_json(resultado=resultado, caminho=args.output)


if __name__ == "__main__":
    main()
