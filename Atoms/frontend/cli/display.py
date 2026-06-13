# frontend/display.py
# pylint: disable = too-many-arguments # R0913
# pylint: disable = too-many-positional-arguments # R0917

"""Funções de apresentação de dados para o Neutron Star/Atoms.

Este módulo concentra a lógica de exibição em diferentes
frontends simples, como saída em linha de comando.
"""

from pathlib import Path

from Atoms.backend.core.entities import ModeloArquivo, ModeloPasta


def exibir_sistema_operacional(
    nome_sistema: str, versao_sistema: str, caminho_pasta_home: str
) -> None:
    """Exibe informações básicas sobre o sistema operacional.

    Esta função mostra o nome, versão e diretório home do sistema
    operacional detectado.
    """
    print(f"Sistema: {nome_sistema}, Versão: {versao_sistema}, Home: {caminho_pasta_home}")


def exibir_pasta(
    nome_pasta: str,
    caminho_pasta: str,
    pasta_pai: ModeloPasta | None,
    subpastas: list[ModeloPasta],
    subarquivos: list[ModeloArquivo],
    titulo: str | None = None,
) -> None:
    """Exibe informações básicas sobre uma pasta.

    Esta função mostra o nome, caminho e quantidade de subpastas e arquivos
    contidos na pasta informada.
    """
    cabecalho: str = titulo or "ModeloPasta"
    print(f"{cabecalho}: {nome_pasta}, Caminho: {caminho_pasta}")
    print(f"Pasta pai: {Path(caminho_pasta).parent if pasta_pai is None else pasta_pai.nome_pasta}")
    print(f"  Subpastas: {len(subpastas)} | Arquivos: {len(subarquivos)}")


def exibir_arquivo(
    nome_arquivo: str, caminho_arquivo: str, tamanho_arquivo: int, is_html: bool
) -> None:
    """Exibe informações básicas sobre um arquivo.

    Esta função mostra o nome, caminho, tamanho em bytes e se o arquivo é
    identificado como HTML.
    """
    print(
        "Arquivo: "
        f"{nome_arquivo}, "
        f"Caminho: {caminho_arquivo}, "
        f"Tamanho: {tamanho_arquivo} bytes, "
        f"HTML: {is_html}"
    )
