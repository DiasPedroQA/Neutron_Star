# Atoms/src/aplicacao/casos_uso.py

"""Casos de uso da aplicação."""

# Cada classe representa um único caso de uso público.
# pylint: disable=too-few-public-methods

from pathlib import Path

from dominio.entidades import (
    ArquivoTemp,
    ConversaoResultado,
    TagExtraida,
)

from .portas import Diretorio, LeitorArquivo


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
    """Caso de uso: busca arquivos HTML e extrai tags de cada um,
    retornando uma lista de ConversaoResultado."""

    def __init__(self, diretorio: Diretorio, leitor: LeitorArquivo) -> None:
        """Recebe as portas de busca de arquivos e de extração de tags."""
        self.diretorio: Diretorio = diretorio
        self.leitor: LeitorArquivo = leitor

    def executar(self) -> list[ConversaoResultado]:
        """Busca cada arquivo e associa a ele as tags extraídas, se existirem."""
        arquivos: list[ArquivoTemp] = self.diretorio.buscar_arquivos_html()
        resultados: list[ConversaoResultado] = []
        for arquivo in arquivos:
            try:
                tags: list[TagExtraida] = self.leitor.extrair_tags(
                    caminho=Path(arquivo.caminho_absoluto)
                )
            except FileNotFoundError:
                tags = []
            resultados.append(ConversaoResultado(arquivo=arquivo, tags_extraidas=tags))
        return resultados
