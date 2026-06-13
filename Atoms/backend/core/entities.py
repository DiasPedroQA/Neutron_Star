# backend/models.py

"""Modelos de dados principais do domínio: Sistema Operacional, ModeloPasta e Arquivo."""


from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ModeloSistemaOperacional:
    """Representa o sistema operacional onde a execução ocorre."""

    nome_sistema: str  # "Windows", "Linux", "Darwin"
    versao_sistema: str  # ex: "10", "22.04"
    user_home: Path  # caminho absoluto para o diretório do usuário

    def __post_init__(self) -> None:
        # Validação de tipo (embora as anotações já ajudem, checamos para segurança)
        if not isinstance(self.nome_sistema, str) or not self.nome_sistema.strip():
            raise ValueError("nome_sistema deve ser uma string não vazia.")
        if not isinstance(self.versao_sistema, str) or not self.versao_sistema.strip():
            raise ValueError("versao_sistema deve ser uma string não vazia.")
        if not isinstance(self.user_home, Path):
            raise TypeError("user_home deve ser uma instância de pathlib.Path.")

        # Restrições de formato para nome/versão (evita caracteres indesejados)
        for attr, valor in [
            ("nome_sistema", self.nome_sistema),
            ("versao_sistema", self.versao_sistema),
        ]:
            if "\n" in valor or "\r" in valor:
                raise ValueError(f"{attr} não pode conter quebras de linha.")
            if "/" in valor or "\\" in valor:
                raise ValueError(f"{attr} não pode conter barras (path).")

        # Validação de caminho
        if not self.user_home.is_absolute():
            raise ValueError(f"Home deve ser caminho absoluto: {self.user_home}")
        # Exigir que seja um diretório existente
        if not self.user_home.is_dir():
            raise ValueError(f"Home deve ser um diretório existente: {self.user_home}")


@dataclass
class ModeloArquivo:
    """Representa um arquivo (ex: bookmark HTML, qualquer arquivo)."""

    nome_arquivo: str
    caminho_arquivo: Path  # caminho absoluto
    tamanho_arquivo_bytes: int = 0
    file_is_html: bool = False  # atalho para saber se é HTML

    def __post_init__(self) -> None:
        # Validações de tipo
        if not isinstance(self.nome_arquivo, str) or not self.nome_arquivo.strip():
            raise ValueError("nome_arquivo deve ser uma string não vazia.")
        if not isinstance(self.caminho_arquivo, Path):
            raise TypeError("caminho_arquivo deve ser um Path.")
        if not isinstance(self.tamanho_arquivo_bytes, int):
            raise TypeError("tamanho_arquivo_bytes deve ser int.")
        if not isinstance(self.file_is_html, bool):
            raise TypeError("file_is_html deve ser bool.")

        # nome_arquivo não deve conter separadores de diretório
        if "/" in self.nome_arquivo or "\\" in self.nome_arquivo:
            raise ValueError(f"nome_arquivo não pode conter barras: {self.nome_arquivo}")

        # Caminho absoluto obrigatório
        if not self.caminho_arquivo.is_absolute():
            raise ValueError(f"Caminho deve ser absoluto: {self.caminho_arquivo}")

        # O caminho deve apontar para um arquivo (não uma pasta existente)
        # (essa checagem só faz sentido se o arquivo existir; ajuste conforme necessidade)
        # if self.caminho_arquivo.exists() and not self.caminho_arquivo.is_file():
        #     raise ValueError(
        #         f"caminho_arquivo deve ser um arquivo, não um diretório: {self.caminho_arquivo}"
        #     )

        # Tamanho nunca negativo
        if self.tamanho_arquivo_bytes < 0:
            raise ValueError("tamanho_arquivo_bytes não pode ser negativo.")

        # Inferência do flag HTML (mantida como estava)
        if not self.file_is_html and self.caminho_arquivo.suffix.lower() == ".html":
            # Em dataclass normal podemos reatribuir (não é frozen)
            self.file_is_html = True

        # Consistência opcional: se foi explicitamente marcado como HTML, forçar sufixo .html/.htm?
        # (descomente se quiser essa rigidez)
        # if self.file_is_html and self.caminho_arquivo.suffix.lower() not in (".html", ".htm"):
        #     raise ValueError(
        #         f"Arquivo marcado como HTML mas sufixo é {self.caminho_arquivo.suffix}"
        #     )


@dataclass
class ModeloPasta:
    """Representa um diretório no sistema de arquivos."""

    nome_pasta: str
    caminho_pasta: Path
    pasta_pai: ModeloPasta | None = None
    subpastas: list[ModeloPasta] = field(default_factory=list)
    arquivos: list[ModeloArquivo] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Validações de tipo
        if not isinstance(self.nome_pasta, str) or not self.nome_pasta.strip():
            raise ValueError("nome_pasta deve ser uma string não vazia.")
        if not isinstance(self.caminho_pasta, Path):
            raise TypeError("caminho_pasta deve ser um Path.")
        if self.pasta_pai is not None and not isinstance(self.pasta_pai, ModeloPasta):
            raise TypeError("pasta_pai deve ser None ou ModeloPasta.")
        if not isinstance(self.subpastas, list):
            raise TypeError("subpastas deve ser uma lista.")
        if not isinstance(self.arquivos, list):
            raise TypeError("arquivos deve ser uma lista.")

        # nome_pasta não deve conter separadores
        if "/" in self.nome_pasta or "\\" in self.nome_pasta:
            raise ValueError(f"nome_pasta não pode conter barras: {self.nome_pasta}")

        # Caminho absoluto
        if not self.caminho_pasta.is_absolute():
            raise ValueError(f"Caminho deve ser absoluto: {self.caminho_pasta}")

        # Consistência com a pasta pai
        if self.pasta_pai is not None and self.caminho_pasta.parent != self.pasta_pai.caminho_pasta:
            raise ValueError(
                f"Pasta pai inconsistente: {self.caminho_pasta} "
                f"deveria estar dentro de {self.pasta_pai.caminho_pasta}"
            )

        # Valida os elementos das listas e impõe unicidade de nome
        self._validar_e_ajustar_subpastas()
        self._validar_e_ajustar_arquivos()

    def _validar_e_ajustar_subpastas(self) -> None:
        """Verifica consistência e ajusta o pai das subpastas."""
        nomes_vistos: set[str] = set()
        for sub_pasta in self.subpastas:
            if not isinstance(sub_pasta, ModeloPasta):
                raise TypeError("Todos os elementos de subpastas devem ser ModeloPasta.")
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
        for arq in self.arquivos:
            if not isinstance(arq, ModeloArquivo):
                raise TypeError("Todos os elementos de arquivos devem ser ModeloArquivo.")
            # Consistência de diretório pai do arquivo
            if arq.caminho_arquivo.parent != self.caminho_pasta:
                raise ValueError(
                    f"Arquivo {arq.nome_arquivo} não está nesta pasta "
                    f"(esperado pai {self.caminho_pasta}, obtido {arq.caminho_arquivo.parent})"
                )
            # Unicidade de nome de arquivo
            if arq.nome_arquivo in nomes_vistos:
                raise ValueError(f"Arquivo com nome duplicado: {arq.nome_arquivo}")
            nomes_vistos.add(arq.nome_arquivo)

    def adicionar_subpasta(self, sub_pasta: ModeloPasta) -> None:
        """Adiciona uma subpasta, ajustando seu 'pai' para esta pasta."""
        if not isinstance(sub_pasta, ModeloPasta):
            raise TypeError("A subpasta deve ser do tipo ModeloPasta.")
        if sub_pasta is self:
            raise ValueError("Uma pasta não pode ser subpasta de si mesma.")
        # Evita duplicatas pelo caminho (como já existia)
        if any(p.caminho_pasta == sub_pasta.caminho_pasta for p in self.subpastas):
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
        if sub_arquivo.caminho_arquivo.parent != self.caminho_pasta:
            raise ValueError(
                f"O arquivo {sub_arquivo.nome_arquivo} não está na pasta {self.caminho_pasta}"
            )
        # Evita duplicatas pelo caminho
        if any(a.caminho_arquivo == sub_arquivo.caminho_arquivo for a in self.arquivos):
            return
        self.arquivos.append(sub_arquivo)
        # Revalida unicidade de nomes
        self._validar_e_ajustar_arquivos()
