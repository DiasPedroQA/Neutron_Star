# Atoms/src/aplicacao/casos_uso.py
# pylint: disable=broad-exception-caught, too-few-public-methods, too-many-locals

"""Módulo contendo as implementações de Casos de Uso do App Neutron Star."""

import os
from collections.abc import Generator
from pathlib import Path

from src.dominio.entidades import (
    ArquivoConvertido,
    ErroConversao,
    InfoSistema,
    ResultadoEscaneamento,
    StatusConversao,
)
from src.dominio.excecoes import DiretorioInexistenteError, PathInseguroError

from .portas import (
    BuscadorPort,
    EscritorPort,
    GerenciadorSistemaPort,
    LeitorHTMLPort,
    ParserPort,
)


def is_safe_path(caminho_input: str | Path) -> bool:
    """Verifica se o caminho está restrito estritamente à Home do usuário (~/).

    Garante que qualquer caminho manipulado esteja contido dentro do diretório
    pessoal, evitando ataques e acessos maliciosos do tipo Path Traversal.
    """
    try:
        caminho_resolvido: Path = Path(caminho_input).expanduser().resolve()
        home_resolvido: Path = Path.home().resolve()
        return caminho_resolvido == home_resolvido or caminho_resolvido.is_relative_to(
            home_resolvido
        )
    except Exception:
        return False


class ObterInfoSistemaUseCase:
    """Caso de Uso para coletar os metadados e atalhos de sistema do usuário."""

    def __init__(self, gerenciador_sistema: GerenciadorSistemaPort) -> None:
        self._gerenciador_sistema: GerenciadorSistemaPort = gerenciador_sistema

    def executar_leitura_sistema(self) -> InfoSistema:
        """Executa a coleta de informações e atalhos sugeridos do S.O."""
        return self._gerenciador_sistema.obter_informacoes_so()


class EscanearDiretorioUseCase:
    """Caso de Uso para realizar a varredura profunda de arquivos do disco."""

    def __init__(self, buscador: BuscadorPort) -> None:
        self._buscador: BuscadorPort = buscador

    def executar_scanner_de_pasta(
        self,
        caminho_str: str,
        extensao: str = ".html",
        profundidade: int = 5,
    ) -> ResultadoEscaneamento:
        """Valida a segurança do caminho e executa o escaneamento do disco."""
        caminho = Path(caminho_str)

        # 🛡️ Validação contra Path Traversal
        if not is_safe_path(caminho_input=caminho):
            raise PathInseguroError(caminho=caminho_str)

        if not self._buscador.validar_pasta(caminho):
            raise DiretorioInexistenteError(caminho=caminho_str)

        return self._buscador.escanear(
            caminho=caminho,
            extensao=extensao,
            profundidade=profundidade,
        )


class ConverterFavoritosLoteUseCase:
    """Caso de Uso para coordenar o pipeline de conversão de múltiplos arquivos."""

    def __init__(
        self,
        leitor: LeitorHTMLPort,
        parser: ParserPort,
        escritor: EscritorPort,
    ) -> None:
        self._leitor: LeitorHTMLPort = leitor
        self._parser: ParserPort = parser
        self._escritor: EscritorPort = escritor

    def executar_com_progresso(
        self,
        arquivos_selecionados: list[str],
        extensao_destino: str,
        pasta_saida: str | None = None,
    ) -> Generator[StatusConversao, None, None]:
        """Executa a conversão arquivo por arquivo com stream de progresso real."""
        total: int = len(arquivos_selecionados)
        arquivos_convertidos: list[ArquivoConvertido] = []
        erros: list[ErroConversao] = []

        # 🛡️ Valida a pasta de saída ANTES do loop, se informada
        pasta_saida_path: Path | None = None
        if pasta_saida:
            if not is_safe_path(caminho_input=pasta_saida):
                erros.append(
                    ErroConversao(
                        arquivo="—",
                        erro=f"Pasta de saída fora da Home: {pasta_saida}",
                    )
                )
                yield {
                    "progresso": 0,
                    "arquivo_atual": "—",
                    "concluido": True,
                    "sucesso": False,
                    "arquivos_convertidos": [],
                    "erros": erros,
                }
                return
            pasta_saida_path = Path(pasta_saida).expanduser().resolve()

        for index, arq_str in enumerate(arquivos_selecionados):
            caminho_original: Path = Path(arq_str)
            nome_arquivo: str = caminho_original.name

            if not is_safe_path(caminho_input=caminho_original):
                erros.append(
                    ErroConversao(
                        arquivo=nome_arquivo,
                        erro="Acesso proibido: O arquivo está em local inseguro.",
                    )
                )
                progresso = int(((index + 1) / total) * 100)
                yield {
                    "progresso": progresso,
                    "arquivo_atual": nome_arquivo,
                    "concluido": (index + 1) == total,
                    "sucesso": len(arquivos_convertidos) > 0,
                    "arquivos_convertidos": arquivos_convertidos,
                    "erros": erros,
                }
                continue

            try:
                html_conteudo: str = self._leitor.ler_arquivo(caminho=caminho_original)

                if favoritos := self._parser.extrair_favoritos(html_conteudo):
                    dados_serializaveis: list[dict[str, str]] = [fav.to_dict() for fav in favoritos]

                    caminho_gravado: str = self._escritor.salvar_lote(
                        caminho_original=caminho_original,
                        dados=dados_serializaveis,
                        extensao=extensao_destino,
                        pasta_saida=pasta_saida_path,
                    )

                    arquivos_convertidos.append(
                        ArquivoConvertido(
                            origem=nome_arquivo,
                            destino=os.path.basename(caminho_gravado),
                            total_links=len(favoritos),
                        )
                    )
                else:
                    erros.append(
                        ErroConversao(
                            arquivo=nome_arquivo,
                            erro="Nenhum favorito válido foi encontrado no HTML.",
                        )
                    )
            except Exception as e:
                erros.append(
                    ErroConversao(
                        arquivo=nome_arquivo,
                        erro=f"Falha no processamento: {e!s}",
                    )
                )

            progresso = int(((index + 1) / total) * 100)
            yield {
                "progresso": progresso,
                "arquivo_atual": nome_arquivo,
                "concluido": (index + 1) == total,
                "sucesso": len(arquivos_convertidos) > 0,
                "arquivos_convertidos": arquivos_convertidos,
                "erros": erros,
            }
