# Atoms/backend/core/entidades/entidade_diretorio.py

"""Modelos de dados principais do domínio: ModeloPasta."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .entidade_arquivo import ModeloArquivo


@dataclass
class ModeloPasta:
    """Representa um diretório no sistema de arquivos."""

    nome_pasta: str
    caminho_absoluto: Path
    pasta_pai: ModeloPasta | None = None
    subpastas: list[ModeloPasta] = field(default_factory=list)
    subarquivos: list[ModeloArquivo] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Validações de tipo
        if not isinstance(self.nome_pasta, str) or not self.nome_pasta.strip():
            raise ValueError("nome_pasta deve ser uma string não vazia.")
        if not isinstance(self.caminho_absoluto, Path):
            raise TypeError("caminho_absoluto deve ser um Path.")
        if self.pasta_pai is not None and not isinstance(self.pasta_pai, ModeloPasta):
            raise TypeError("pasta_pai deve ser None ou ModeloPasta.")
        if not isinstance(self.subpastas, list):
            raise TypeError("subpastas deve ser uma lista.")
        if not isinstance(self.subarquivos, list):
            raise TypeError("subarquivos deve ser uma lista.")

        # nome_pasta não deve conter separadores
        if "/" in self.nome_pasta or "\\" in self.nome_pasta:
            raise ValueError(f"nome_pasta não pode conter barras: {self.nome_pasta}")

        # Caminho absoluto
        if not self.caminho_absoluto.is_absolute():
            raise ValueError(f"Caminho deve ser absoluto: {self.caminho_absoluto}")

        # Consistência com a pasta pai
        if self.pasta_pai is not None and (
            self.caminho_absoluto.parent != self.pasta_pai.caminho_absoluto
        ):
            raise ValueError(
                f"Pasta pai inconsistente: {self.caminho_absoluto} "
                + f"deveria estar dentro de {self.pasta_pai.caminho_absoluto}"
            )

        # Valida os elementos das listas e impõe unicidade de nome
        self._validar_e_ajustar_subpastas()
        self._validar_e_ajustar_arquivos()

    def _validar_e_ajustar_subpastas(self) -> None:
        """Verifica consistência e ajusta o pai das subpastas."""
        nomes_vistos: set[str] = set()
        for sub_pasta in self.subpastas:
            if not isinstance(sub_pasta, ModeloPasta):
                raise TypeError(
                    "Todos os elementos de subpastas devem ser ModeloPasta."
                )
            if sub_pasta is self:
                raise ValueError("Uma pasta não pode ser subpasta de si mesma.")
            # Garante que o pai seja esta pasta
            if sub_pasta.pasta_pai is None:
                sub_pasta.pasta_pai = self
            elif sub_pasta.pasta_pai is not self:
                raise ValueError(f"Subpasta {sub_pasta.nome_pasta} já tem outro pai.")
            # Unicidade de nome dentro da pasta
            if sub_pasta.nome_pasta in nomes_vistos:
                raise ValueError(f"Subpasta com nome duplicado: {sub_pasta.nome_pasta}")
            nomes_vistos.add(sub_pasta.nome_pasta)

    def _validar_e_ajustar_arquivos(self) -> None:
        """Verifica se arquivos pertencem a esta pasta e se não há nomes duplicados."""
        nomes_vistos: set[str] = set()
        for arq in self.subarquivos:
            if not isinstance(arq, ModeloArquivo):
                raise TypeError(
                    "Todos os elementos de arquivos devem ser ModeloArquivo."
                )
            # Consistência de diretório pai do arquivo
            if arq.caminho_arquivo.parent != self.caminho_absoluto:
                raise ValueError(
                    f"Arquivo {arq.nome_arquivo} não está nesta pasta "
                    + f"(esperado pai {self.caminho_absoluto}, obtido {arq.caminho_arquivo.parent})"
                )
            # Unicidade de nome de arquivo
            if arq.nome_arquivo in nomes_vistos:
                raise ValueError(f"Arquivo com nome duplicado: {arq.nome_arquivo}")
            nomes_vistos.add(arq.nome_arquivo)

    @property
    def arquivos(self) -> list[ModeloArquivo]:
        """Alias legível para a lista de arquivos desta pasta."""
        return self.subarquivos

    def adicionar_subpasta(self, sub_pasta: ModeloPasta) -> None:
        """Adiciona uma subpasta, ajustando seu 'pai' para esta pasta."""
        if not isinstance(sub_pasta, ModeloPasta):
            raise TypeError("A subpasta deve ser do tipo ModeloPasta.")
        if sub_pasta is self:
            raise ValueError("Uma pasta não pode ser subpasta de si mesma.")
        if sub_pasta.pasta_pai is not None and sub_pasta.pasta_pai is not self:
            raise ValueError("Subpasta já pertence a outro pai.")
        # Evita duplicatas pelo caminho (como já existia)
        if any(
            p.caminho_absoluto == sub_pasta.caminho_absoluto for p in self.subpastas
        ):
            return
        # Ajusta pai e adiciona
        sub_pasta.pasta_pai = self
        self.subpastas.append(sub_pasta)
        # Revalida unicidade de nomes (pode ser que já exista mesmo nome com caminho diferente)
        self._validar_e_ajustar_subpastas()

    def adicionar_arquivo(self, sub_arquivo: ModeloArquivo) -> None:
        """Adiciona um arquivo, garantindo consistência."""
        if not isinstance(sub_arquivo, ModeloArquivo):
            raise TypeError("O arquivo deve ser do tipo ModeloArquivo.")
        # Verifica se o arquivo realmente pertence a esta pasta
        if sub_arquivo.caminho_arquivo.parent != self.caminho_absoluto:
            raise ValueError(
                f"O arquivo {sub_arquivo.nome_arquivo} não está na pasta {self.caminho_absoluto}"
            )
        # Evita duplicatas pelo caminho
        if any(
            a.caminho_arquivo == sub_arquivo.caminho_arquivo for a in self.subarquivos
        ):
            return
        self.subarquivos.append(sub_arquivo)
        # Revalida unicidade de nomes
        self._validar_e_ajustar_arquivos()
