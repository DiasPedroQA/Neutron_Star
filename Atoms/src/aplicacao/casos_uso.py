# Atoms/src/aplicacao/casos_uso.py
# pylint: disable=broad-exception-caught, too-few-public-methods

"""
Casos de uso da aplicação.

Cada classe representa um único caso de uso público.
"""

import logging
from pathlib import Path

from src.aplicacao.portas import Diretorio, LeitorArquivo
from src.dominio.entidades import (
    ArquivoTemp,
    ConversaoResultado,
    TagExtraida,
)
from src.dominio.excecoes import ArquivoNaoEncontradoError

# Configuração de logging
logger: logging.Logger = logging.getLogger(name=__name__)


class ListarArquivos:
    """Caso de uso: listar arquivos HTML com metadados."""

    def __init__(self, diretorio: Diretorio) -> None:
        """Recebe a porta responsável por localizar os arquivos HTML."""
        self.diretorio: Diretorio = diretorio

    def executar_busca(self) -> list[ArquivoTemp]:
        """Executa a busca e retorna a lista de arquivos encontrados."""
        return self.diretorio.buscar_arquivos_html()


class ExtrairTags:
    """Caso de uso: extrair tags de um arquivo HTML."""

    def __init__(self, leitor: LeitorArquivo) -> None:
        """Recebe a porta responsável por ler e extrair tags do arquivo."""
        self.leitor: LeitorArquivo = leitor

    def executar_extracao(self, caminho: Path) -> list[TagExtraida]:
        """Executa a extração de tags do arquivo especificado."""
        return self.leitor.extrair_tags(caminho=caminho)


class BuscarEExtrairTags:
    """Coordena a busca de arquivos e a extração de tags em uma única operação.
    Combina os casos de uso especializados para produzir resultados consolidados de conversão."""

    def __init__(self, listar_arquivos: ListarArquivos, extrair_tags: ExtrairTags) -> None:
        """Cria o caso de uso combinando busca de arquivos e extração de tags."""
        self.listar_arquivos: ListarArquivos = listar_arquivos
        self.extrair_tags: ExtrairTags = extrair_tags

    def executar(self) -> list[ConversaoResultado]:
        """Executa a busca de arquivos e a extração de tags em sequência.
        Retorna uma lista de resultados contendo tags extraídas ou erros de processamento."""

        arquivos: list[ArquivoTemp] = self.listar_arquivos.executar_busca()
        resultados: list[ConversaoResultado] = []

        for arquivo in arquivos:
            try:
                tags: list[TagExtraida] = self.extrair_tags.executar_extracao(
                    caminho=Path(arquivo.caminho_absoluto)
                )
                resultados.append(
                    ConversaoResultado(arquivo=arquivo, tags_extraidas=tags, erro=None)
                )
            except (ArquivoNaoEncontradoError, FileNotFoundError, ValueError) as e:
                # Erros esperados: arquivo não existe ou conteúdo inválido
                resultados.append(
                    ConversaoResultado(
                        arquivo=arquivo,
                        tags_extraidas=[],
                        erro=f"Falha ao extrair tags: {e}",
                    )
                )
                # Log com stack trace
                logger.exception("Erro no arquivo %s", arquivo.caminho_absoluto)
            # Captura inesperada (para não quebrar o fluxo)
            except Exception:
                # Erros inesperados também entram no resultado, mas com mensagem genérica
                resultados.append(
                    ConversaoResultado(
                        arquivo=arquivo,
                        tags_extraidas=[],
                        erro="Erro inesperado ao processar arquivo.",
                    )
                )
                logger.exception("Erro inesperado no arquivo %s", arquivo.caminho_absoluto)

        return resultados
