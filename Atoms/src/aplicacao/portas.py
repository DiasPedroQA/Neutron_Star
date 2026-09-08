# Atoms/src/aplicacao/portas.py
# pylint: disable=too-few-public-methods

"""Interfaces abstratas (portas) para a aplicação."""

from abc import ABC, abstractmethod
from pathlib import Path


class GerenciadorSistemaPort(ABC):
    """
    Porta de Saída (Outbound Port).
    Define o contrato para detecção de informações ambientais e atalhos do S.O.
    """

    @abstractmethod
    def obter_informacoes_so(self) -> dict[str, str | list[dict[str, str]]]:
        """Coleta e retorna dados do sistema operacional, usuário atual e atalhos de pastas."""


class BuscadorPort(ABC):
    """
    Porta de Saída (Outbound Port).
    Define o contrato para varredura física profunda e listagem de caminhos de arquivos.
    """

    @abstractmethod
    def validar_pasta(self, caminho: Path) -> bool:
        """Verifica se a pasta informada realmente existe no disco e é acessível."""

    @abstractmethod
    def escanear(
        self, caminho: Path
    ) -> dict[
        str,
        str | int | float | list[dict[str, str | float | bool]],
    ]:
        """
        Varre recursivamente o diretório resolvido buscando arquivos HTML de favoritos.
        Retorna dicionário contendo estatísticas gerais e lista com metadados dos arquivos.
        """


class LeitorHTMLPort(ABC):
    """
    Porta de Saída (Outbound Port).
    Define o contrato para leitura física de dados textuais com suporte a cascata de encodings.
    """

    @abstractmethod
    def ler_arquivo(self, caminho: Path) -> str:
        """Lê o conteúdo físico do arquivo HTML e o retorna como string limpa."""


class EscritorPort(ABC):
    """
    Porta de Saída (Outbound Port).
    Define o contrato para a gravação física dos favoritos convertidos (CSV/JSON).
    """

    @abstractmethod
    def salvar_lote(
        self,
        caminho_original: Path,
        dados: list[dict[str, str | float | bool]],
        extensao: str,
        sufixo: str = "_processado",
    ) -> str:
        """
        Calcula o novo caminho, seleciona a estratégia física adequada e grava os dados.
        Retorna o caminho absoluto do arquivo gravado no disco como string.
        """


class ParserPort(ABC):
    """
    Porta de Saída (Outbound Port).
    Define o contrato para o motor que extrai tags de favoritos a partir do HTML cru.
    """

    @abstractmethod
    def extrair_favoritos(self, html_conteudo: str) -> list:
        """Processa a string do HTML e retorna uma lista de entidades do tipo Favorito."""
