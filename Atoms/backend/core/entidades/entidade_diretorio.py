# Atoms/backend/core/entidades/entidade_diretorio.py

"""Modelos de dados principais do domínio: ModeloPasta."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from .entidade_arquivo import ModeloArquivo

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class ModeloPasta:
    """Representa um diretório no sistema de arquivos."""

    nome_pasta: str
    caminho_absoluto: Path
    pasta_pai: ModeloPasta | None = None
    subpastas: list[ModeloPasta] = field(default_factory=list)
    subarquivos: list[ModeloArquivo] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validações pós-inicialização."""
        # Validações de tipo
        if not isinstance(self.nome_pasta, str) or not self.nome_pasta.strip():
            logger.error("nome_pasta inválido: %r", self.nome_pasta)
            raise ValueError("nome_pasta deve ser uma string não vazia.")
        if not isinstance(self.caminho_absoluto, Path):
            logger.error("caminho_absoluto não é Path: %r", self.caminho_absoluto)
            raise TypeError("caminho_absoluto deve ser um Path.")
        if self.pasta_pai is not None and not isinstance(self.pasta_pai, ModeloPasta):
            logger.error("pasta_pai não é ModeloPasta: %r", self.pasta_pai)
            raise TypeError("pasta_pai deve ser None ou ModeloPasta.")
        if not isinstance(self.subpastas, list):
            logger.error("subpastas não é lista: %r", self.subpastas)
            raise TypeError("subpastas deve ser uma lista.")
        if not isinstance(self.subarquivos, list):
            logger.error("subarquivos não é lista: %r", self.subarquivos)
            raise TypeError("subarquivos deve ser uma lista.")

        # nome_pasta não deve conter separadores
        if "/" in self.nome_pasta or "\\" in self.nome_pasta:
            logger.warning(
                "nome_pasta contém barra: %r (caminho: %s)",
                self.nome_pasta,
                self.caminho_absoluto,
            )
            raise ValueError(f"nome_pasta não pode conter barras: {self.nome_pasta}")

        # Caminho absoluto
        if not self.caminho_absoluto.is_absolute():
            logger.error("Caminho não absoluto: %s", self.caminho_absoluto)
            raise ValueError(f"Caminho deve ser absoluto: {self.caminho_absoluto}")

        # Consistência com a pasta pai
        if self.pasta_pai is not None and (
            self.caminho_absoluto.parent != self.pasta_pai.caminho_absoluto
        ):
            logger.error(
                "Inconsistência com pasta pai: %s (pai: %s, esperado: %s)",
                self.caminho_absoluto,
                self.pasta_pai.caminho_absoluto,
                self.caminho_absoluto.parent,
            )
            raise ValueError(
                f"Pasta pai inconsistente: {self.caminho_absoluto} "
                + f"deveria estar dentro de {self.pasta_pai.caminho_absoluto}"
            )

        # Valida os elementos das listas e impõe unicidade de nome
        self._validar_e_ajustar_subpastas()
        self._validar_e_ajustar_arquivos()

        logger.debug(
            "ModeloPasta criada: nome=%r, caminho=%s, subpastas=%d, arquivos=%d",
            self.nome_pasta,
            self.caminho_absoluto,
            len(self.subpastas),
            len(self.subarquivos),
        )

    def _validar_e_ajustar_subpastas(self) -> None:
        """Verifica consistência e ajusta o pai das subpastas."""
        nomes_vistos: set[str] = set()
        for sub_pasta in self.subpastas:
            if not isinstance(sub_pasta, ModeloPasta):
                logger.error("Elemento em subpastas não é ModeloPasta: %r", sub_pasta)
                raise TypeError(
                    "Todos os elementos de subpastas devem ser ModeloPasta."
                )
            if sub_pasta is self:
                logger.error(
                    "Subpasta é a própria pasta: %s", sub_pasta.caminho_absoluto
                )
                raise ValueError("Uma pasta não pode ser subpasta de si mesma.")
            # Garante que o pai seja esta pasta
            if sub_pasta.pasta_pai is None:
                logger.debug(
                    "Ajustando pasta_pai de %s para %s",
                    sub_pasta.nome_pasta,
                    self.nome_pasta,
                )
                sub_pasta.pasta_pai = self
            elif sub_pasta.pasta_pai is not self:
                logger.error(
                    "Subpasta %s já tem outro pai: %s",
                    sub_pasta.nome_pasta,
                    sub_pasta.pasta_pai.nome_pasta,
                )
                raise ValueError(f"Subpasta {sub_pasta.nome_pasta} já tem outro pai.")
            # Unicidade de nome dentro da pasta
            if sub_pasta.nome_pasta in nomes_vistos:
                logger.warning(
                    "Nome de subpasta duplicado: %s em %s",
                    sub_pasta.nome_pasta,
                    self.caminho_absoluto,
                )
                raise ValueError(f"Subpasta com nome duplicado: {sub_pasta.nome_pasta}")
            nomes_vistos.add(sub_pasta.nome_pasta)

    def _validar_e_ajustar_arquivos(self) -> None:
        """Verifica se arquivos pertencem a esta pasta e se não há nomes duplicados."""
        nomes_vistos: set[str] = set()
        for arq in self.subarquivos:
            if not isinstance(arq, ModeloArquivo):
                logger.error("Elemento em arquivos não é ModeloArquivo: %r", arq)
                raise TypeError(
                    "Todos os elementos de arquivos devem ser ModeloArquivo."
                )
            # Consistência de diretório pai do arquivo
            if arq.caminho_arquivo.parent != self.caminho_absoluto:
                logger.error(
                    "Arquivo %s não está na pasta %s (pai real: %s)",
                    arq.nome_arquivo,
                    self.caminho_absoluto,
                    arq.caminho_arquivo.parent,
                )
                raise ValueError(
                    f"Arquivo {arq.nome_arquivo} não está nesta pasta "
                    + f"(esperado pai {self.caminho_absoluto}, obtido {arq.caminho_arquivo.parent})"
                )
            # Unicidade de nome de arquivo
            if arq.nome_arquivo in nomes_vistos:
                logger.warning(
                    "Nome de arquivo duplicado: %s em %s",
                    arq.nome_arquivo,
                    self.caminho_absoluto,
                )
                raise ValueError(f"Arquivo com nome duplicado: {arq.nome_arquivo}")
            nomes_vistos.add(arq.nome_arquivo)

    @property
    def arquivos(self) -> list[ModeloArquivo]:
        """Alias legível para a lista de arquivos desta pasta."""
        return self.subarquivos

    def adicionar_subpasta(self, nova_sub_pasta: ModeloPasta) -> None:
        """Adiciona uma subpasta, ajustando seu 'pai' para esta pasta."""
        logger.debug(
            "Tentando adicionar subpasta %s a %s",
            nova_sub_pasta.nome_pasta,
            self.nome_pasta,
        )

        if not isinstance(nova_sub_pasta, ModeloPasta):
            logger.error("Tentativa de adicionar não-ModeloPasta: %r", nova_sub_pasta)
            raise TypeError("A subpasta deve ser do tipo ModeloPasta.")
        if nova_sub_pasta is self:
            logger.error("Tentativa de adicionar a própria pasta como subpasta")
            raise ValueError("Uma pasta não pode ser subpasta de si mesma.")
        if (
            nova_sub_pasta.pasta_pai is not None
            and nova_sub_pasta.pasta_pai is not self
        ):
            logger.error(
                "Subpasta %s já pertence a %s",
                nova_sub_pasta.nome_pasta,
                nova_sub_pasta.pasta_pai.nome_pasta,
            )
            raise ValueError("Subpasta já pertence a outro pai.")

        # Evita duplicatas pelo caminho
        if any(
            p.caminho_absoluto == nova_sub_pasta.caminho_absoluto
            for p in self.subpastas
        ):
            logger.info(
                "Subpasta já existente (mesmo caminho): %s, ignorando.",
                nova_sub_pasta.caminho_absoluto,
            )
            return

        # Ajusta pai e adiciona
        if nova_sub_pasta.pasta_pai is None:
            logger.debug(
                "Definindo pai de %s como %s",
                nova_sub_pasta.nome_pasta,
                self.nome_pasta,
            )
        nova_sub_pasta.pasta_pai = self
        self.subpastas.append(nova_sub_pasta)
        logger.info(
            "Subpasta adicionada: %s -> %s",
            self.caminho_absoluto,
            nova_sub_pasta.nome_pasta,
        )

        # Revalida unicidade de nomes
        self._validar_e_ajustar_subpastas()

    def adicionar_arquivo(self, sub_arquivo: ModeloArquivo) -> None:
        """Adiciona um arquivo, garantindo consistência."""
        logger.debug(
            "Tentando adicionar arquivo %s a %s",
            sub_arquivo.nome_arquivo,
            self.nome_pasta,
        )

        if not isinstance(sub_arquivo, ModeloArquivo):
            logger.error("Tentativa de adicionar não-ModeloArquivo: %r", sub_arquivo)
            raise TypeError("O arquivo deve ser do tipo ModeloArquivo.")

        # Verifica se o arquivo realmente pertence a esta pasta
        if sub_arquivo.caminho_arquivo.parent != self.caminho_absoluto:
            logger.error(
                "Arquivo %s não pertence à pasta %s (pai real: %s)",
                sub_arquivo.nome_arquivo,
                self.caminho_absoluto,
                sub_arquivo.caminho_arquivo.parent,
            )
            raise ValueError(
                f"O arquivo {sub_arquivo.nome_arquivo} não está na pasta {self.caminho_absoluto}"
            )

        # Evita duplicatas pelo caminho
        if any(
            a.caminho_arquivo == sub_arquivo.caminho_arquivo for a in self.subarquivos
        ):
            logger.info(
                "Arquivo já existente (mesmo caminho): %s, ignorando.",
                sub_arquivo.caminho_arquivo,
            )
            return

        self.subarquivos.append(sub_arquivo)
        logger.info(
            "Arquivo adicionado: %s -> %s",
            self.caminho_absoluto,
            sub_arquivo.nome_arquivo,
        )

        # Revalida unicidade de nomes
        self._validar_e_ajustar_arquivos()
