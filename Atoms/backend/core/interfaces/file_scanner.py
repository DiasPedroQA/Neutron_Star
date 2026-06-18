"""Interface para varredura de diretórios em busca de arquivos HTML."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta


class FileScanner(ABC):
    """Define as operações de varredura do sistema de arquivos."""

    @abstractmethod
    def varrer_diretorio(self, pasta_raiz: ModeloPasta) -> None:
        """Preenche a estrutura de pastas a partir do diretório raiz."""

    @abstractmethod
    def localizar_arquivos_html(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """Retorna todos os arquivos HTML encontrados na árvore de pastas."""

    def scan_directory(self, pasta_home: ModeloPasta) -> None:
        """Alias de compatibilidade para `varrer_diretorio`."""
        self.varrer_diretorio(pasta_raiz=pasta_home)

    def find_html_files(self, pasta_atual: ModeloPasta) -> list[ModeloArquivo]:
        """Alias de compatibilidade para `localizar_arquivos_html`."""
        return self.localizar_arquivos_html(pasta=pasta_atual)
