"""Modelo de configurações da aplicação."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConfigApp:
    """Configurações do indexador/buscador.

    Atributos:
        case_sensitive: Se a busca deve diferenciar maiúsculas/minúsculas.
        executavel_por_extensao: Se True, usa extensões para definir executáveis (Windows).
        extensoes_executaveis: Lista de extensões executáveis (ex.: ['.exe', '.bat']).
        ignorar_ocultos: Se True, ignora itens ocultos.
        seguir_symlinks: Se True, segue links simbólicos.
        profundidade_maxima: Profundidade máxima de varredura (-1 = ilimitado).
        calcular_hashes: Se True, calcula checksum dos arquivos.
        padroes_exclusao: Lista de expressões regulares para itens a ignorar.
        caminhos_indexados: Pastas raiz para busca/indexação (não usado diretamente pelo buscador).
    """

    case_sensitive: bool = True
    executavel_por_extensao: bool = False
    extensoes_executaveis: list[str] = field(default_factory=list)
    ignorar_ocultos: bool = True
    seguir_symlinks: bool = False
    profundidade_maxima: int = -1
    calcular_hashes: bool = False
    padroes_exclusao: list[str] = field(default_factory=lambda: [r"\.git", r"__pycache__", r".*\.pyc"])
    caminhos_indexados: list[Path] = field(default_factory=list)

    @classmethod
    def carregar_de_arquivo(cls, caminho: Path) -> ConfigApp:
        """Carrega configurações de um arquivo YAML/JSON (a ser implementado).

        Args:
            caminho: Caminho do arquivo de configuração.

        Returns:
            Instância de ConfigApp populada.
        """
        raise NotImplementedError("Ainda não implementado")

    def salvar_em_arquivo(self, caminho: Path) -> None:
        """Salva as configurações em arquivo (a ser implementado).

        Args:
            caminho: Caminho do arquivo de destino.
        """
        raise NotImplementedError("Ainda não implementado")
