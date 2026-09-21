# Atoms/src/aplicacao/portas.py
# pylint: disable=too-few-public-methods, too-many-positional-arguments, too-many-arguments

"""Interfaces abstratas (portas) para a aplicação."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.dominio.entidades import Favorito, FavoritoDict, InfoSistema, ResultadoEscaneamento


class GerenciadorSistemaPort(ABC):
    """Porta de Saída (Outbound Port).
    Define o contrato para detecção de informações ambientais e atalhos do S.O.
    """

    @abstractmethod
    def obter_informacoes_so(self) -> InfoSistema:
        """Coleta e retorna dados do sistema operacional, usuário atual e atalhos de pastas."""


class BuscadorPort(ABC):
    """Porta de Saída (Outbound Port).
    Define o contrato para varredura física profunda e listagem de caminhos de arquivos.
    """

    @abstractmethod
    def validar_pasta(self, caminho: Path) -> bool:
        """Verifica se a pasta informada realmente existe no disco e é acessível."""

    @abstractmethod
    def escanear(
        self,
        caminho: Path,
        extensao: str = ".html",
        profundidade: int = 5,
    ) -> ResultadoEscaneamento:
        """Varre recursivamente o diretório resolvido buscando arquivos da extensão alvo."""


class LeitorHTMLPort(ABC):
    """Porta de Saída (Outbound Port).
    Define o contrato para leitura física de dados textuais com suporte a cascata de encodings.
    """

    @abstractmethod
    def ler_arquivo(self, caminho: Path) -> str:
        """Lê o conteúdo físico do arquivo HTML e o retorna como string limpa."""


class EscritorPort(ABC):
    """Porta de Saída (Outbound Port).
    Define o contrato para a gravação física dos favoritos convertidos (CSV/JSON).
    """

    @abstractmethod
    def salvar_lote(
        self,
        caminho_original: Path,
        dados: list[FavoritoDict] | list[dict[str, str]],
        extensao: str,
        sufixo: str = "_processado",
        pasta_saida: Path | None = None,
    ) -> str:
        """Calcula o novo caminho, seleciona a estratégia física adequada e grava os dados."""


class ParserPort(ABC):
    """Porta de Saída (Outbound Port).
    Define o contrato para o motor que extrai tags de favoritos a partir do HTML cru.
    """

    @abstractmethod
    def extrair_favoritos(self, html_conteudo: str) -> list[Favorito]:
        """Processa a string do HTML e retorna uma lista de entidades do tipo Favorito."""
