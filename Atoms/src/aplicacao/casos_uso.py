# Atoms/src/aplicacao/casos_uso.py

"""Casos de uso da aplicação."""

# Cada classe representa um único caso de uso público.
# pylint: disable=too-few-public-methods

import logging
from pathlib import Path

from dominio.entidades import (
    ArquivoTemp,
    ConversaoResultado,
    TagExtraida,
)

from .portas import Diretorio, LeitorArquivo

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
    def __init__(
        self, listar_arquivos: ListarArquivos, extrair_tags: ExtrairTags
    ) -> None:
        self.listar_arquivos: ListarArquivos = listar_arquivos
        self.extrair_tags: ExtrairTags = extrair_tags

    def executar(self) -> list[ConversaoResultado]:
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
            except Exception as e:  # noqa: BLE001
                # ✅ Preenche o erro
                resultados.append(
                    ConversaoResultado(
                        arquivo=arquivo,
                        tags_extraidas=[],
                        erro=f"Falha ao extrair tags: {e!s}",
                    )
                )
                # Opcional: log do erro
                logger.error(msg=f"Erro no arquivo {arquivo.caminho_absoluto}: {e}")

        return resultados
