# Atoms/src/controllers/cli_controller.py
# pylint: disable=broad-exception-caught, line-too-long

"""Controller de Linha de Comando (CLI) para o ecossistema Neutron Star."""

import argparse
import json
import sys
from collections.abc import Generator
from typing import Any, Literal, LiteralString

from ..models.conversor import ConversorService
from ..models.entidades import InfoSistema, ResultadoEscaneamento, StatusConversao
from ..models.excecoes import DiretorioInexistenteError, PathInseguroError

LARGURA_BARRA_PROGRESSO: int = 30
PROGRESSO_CONCLUIDO: int = 100


class CLIController:
    """Controller para execução via terminal / linha de comando."""

    servico = ConversorService()

    @classmethod
    def criar_parser(cls) -> argparse.ArgumentParser:
        """Cria e configura a árvore de comandos e argumentos do CLI."""
        parser = argparse.ArgumentParser(
            prog="neutron-star",
            description="🛸 Neutron Star — Processamento Inteligente de Bookmarks Netscape",
        )
        subparsers: argparse._SubParsersAction = parser.add_subparsers(
            dest="comando",
            title="Comandos disponíveis",
            description="Escolha uma das ações abaixo:",
            required=True,
        )

        # Subcomando: sistema
        parser_sistema: argparse.ArgumentParser = subparsers.add_parser(
            name="sistema",
            help="Exibe dados do S.O., usuário ativo e atalhos rápidos da Home.",
        )
        parser_sistema.add_argument(
            "--json",
            dest="saida_json",
            action="store_true",
            help="Exibe o resultado formatado como JSON puro.",
        )

        # Subcomando: escanear
        parser_escanear = subparsers.add_parser(
            name="escanear",
            help="Varre pastas buscando arquivos HTML de favoritos elegíveis.",
        )
        parser_escanear.add_argument(
            "-c",
            "--caminho",
            default="~/",
            help="Diretório inicial para varredura (padrão: ~/)",
        )
        parser_escanear.add_argument(
            "-e",
            "--extensao",
            default=".html",
            help="Extensão de busca (.html, .htm ou todos - padrão: .html)",
        )
        parser_escanear.add_argument(
            "-p",
            "--profundidade",
            type=int,
            default=5,
            help="Profundidade máxima de busca em subpastas (padrão: 5)",
        )
        parser_escanear.add_argument(
            "--json",
            dest="saida_json",
            action="store_true",
            help="Exibe o resultado estruturado em JSON.",
        )

        # Subcomando: converter
        parser_converter = subparsers.add_parser(
            name="converter",
            help="Converte arquivos HTML de favoritos para JSON, CSV ou MD.",
        )
        parser_converter.add_argument(
            "arquivos",
            nargs="+",
            help="Caminhos dos arquivos HTML a serem processados.",
        )
        parser_converter.add_argument(
            "-f",
            "--formato",
            choices=["json", "csv", "md"],
            default="json",
            help="Formato de saída desejado (padrão: json)",
        )
        parser_converter.add_argument(
            "-o",
            "--saida",
            default=None,
            help="Pasta de destino (padrão: salva junto aos originais)",
        )

        return parser

    @classmethod
    def executar_comando_sistema(cls, args: argparse.Namespace) -> int:
        """Executa a coleta de informações ambientais do sistema operacional."""
        try:
            info: InfoSistema = cls.servico.obter_info_sistema()
            if args.saida_json:
                print(json.dumps(info, indent=2, ensure_ascii=False))
                return 0

            print("\n🌌 Informações do Ambiente:")
            print(f"  • Sistema Operacional : {info['so']}")
            print(f"  • Usuário Ativo       : {info['usuario']}")
            print(f"  • Diretório Pessoal   : {info['pasta_home']}")
            print("\n📂 Atalhos Rápidos Recomendados:")
            for atalho in info["atalhos_sugeridos"]:
                print(f"  - {atalho['label']} -> {atalho['caminho']}")
            print()
            return 0
        except Exception as erro:
            print(f"❌ Erro ao obter dados do sistema: {erro}", file=sys.stderr)
            return 1

    @classmethod
    def executar_comando_escanear(cls, args: argparse.Namespace) -> int:
        """Executa a varredura recursiva de diretórios."""
        try:
            res: ResultadoEscaneamento = cls.servico.escanear(
                caminho_str=args.caminho,
                extensao=args.extensao,
                profundidade=args.profundidade,
            )
            if args.saida_json:
                print(json.dumps(res, indent=2, ensure_ascii=False))
                return 0

            print(f"\n🔍 Varredura Concluída em '{res['caminho_varrido']}':")
            print(f"  • Total de Arquivos HTML Encontrados : {res['total_arquivos']}")
            print(f"  • Favoritos Netscape Elegíveis       : {res['total_elegiveis']}")
            print(f"  • Volume Total em Disco              : {res['tamanho_total_mb']} MB")

            if res["arquivos"]:
                print("\n📋 Arquivos Identificados:")
                for arq in res["arquivos"]:
                    status_elegivel: Literal["✅ [ELEGÍVEL]"] | Literal["⚠️ [OUTRO]"] = (
                        "✅ [ELEGÍVEL]" if arq["elegivel"] else "⚠️ [OUTRO]"
                    )
                    tamanho: float = arq["tamanho_kb"]
                    caminho: str = arq["caminho_completo"]
                    print(f"  {status_elegivel} {arq['nome']} ({tamanho} KB) -> {caminho}")
            else:
                print("\n⚠️ Nenhum arquivo de favoritos encontrado com os critérios.")

            print()
            return 0
        except PathInseguroError as erro:
            print(f"🚫 Acesso Proibido (Path Traversal): {erro}", file=sys.stderr)
            return 1
        except DiretorioInexistenteError as erro:
            print(f"⚠️ Diretório Não Encontrado: {erro}", file=sys.stderr)
            return 1
        except Exception as erro:
            print(f"❌ Erro durante o escaneamento: {erro}", file=sys.stderr)
            return 1

    @classmethod
    def executar_comando_converter(cls, args: argparse.Namespace) -> int:
        """Executa a conversão com barra de progresso no terminal."""
        arquivos: list[str] = args.arquivos
        formato: str = args.formato
        pasta_saida: str | None = args.saida

        total: int = len(arquivos)
        formato_str: str = formato.upper()
        print(f"\n⚡ Iniciando conversão de {total} arquivo(s) para [{formato_str}]...")

        try:
            gerador: Generator[StatusConversao, None, None] = cls.servico.converter_com_progresso(
                arquivos_selecionados=arquivos,
                extensao_destino=formato,
                pasta_saida=pasta_saida,
            )

            for evento in gerador:
                progresso: int = evento.get("progresso", 0)
                mensagem: Any = evento.get("arquivo_atual", "")

                tamanho_preenchido = int(LARGURA_BARRA_PROGRESSO * progresso // 100)
                tamanho_vazio: int = LARGURA_BARRA_PROGRESSO - tamanho_preenchido
                barra_grafica: LiteralString = "█" * tamanho_preenchido + "░" * tamanho_vazio

                sys.stdout.write(f"\r[{barra_grafica}] {progresso:3.0f}% | Processando: {mensagem}")
                sys.stdout.flush()

                if progresso >= PROGRESSO_CONCLUIDO:
                    print()

            print("✨ Conversão finalizada com sucesso!\n")
            return 0
        except PathInseguroError as erro:
            print(f"\n🚫 Acesso Proibido (Path Traversal): {erro}", file=sys.stderr)
            return 1
        except Exception as erro:
            print(f"\n❌ Erro crítico no pipeline de conversão: {erro}", file=sys.stderr)
            return 1

    @classmethod
    def main(cls, argv: list[str] | None = None) -> int:
        """Ponto de entrada principal da interface CLI."""
        parser: argparse.ArgumentParser = cls.criar_parser()
        args: argparse.Namespace = parser.parse_args(argv)

        if args.comando == "sistema":
            return cls.executar_comando_sistema(args)
        if args.comando == "escanear":
            return cls.executar_comando_escanear(args)
        if args.comando == "converter":
            return cls.executar_comando_converter(args)

        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(CLIController.main())
