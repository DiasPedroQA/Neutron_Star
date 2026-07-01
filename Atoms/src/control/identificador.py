"""Identificador de sistema operacional e gerador de configuração.

Detecta características do SO e produz uma instância de ConfigApp
adequada ao ambiente, utilizando uma configuração base e sobrescrevendo
apenas os campos específicos de cada plataforma.
"""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast  # se ainda não estiver importado

from ..model.configuracoes import ConfigApp


@dataclass(frozen=True)
class InfoSistema:
    """Características brutas do sistema operacional.

    Atributos:
        nome_so (str): 'linux', 'windows', 'darwin' ou 'outro'.
        case_sensitive (bool): se o sistema de arquivos padrão diferencia maiúsculas.
        separador_caminho (str): separador de diretórios nativo ('/' ou '\').
        suporta_symlinks (bool): se o SO oferece suporte real a links simbólicos.
        ocultacao_por_atributo (bool): True = Windows (atributo hidden), False = prefixo '.'.
        extensoes_executaveis (list[str]): extensões consideradas executáveis.
        diretorios_usuario (list[Path]): diretórios padrão do usuário (home, documentos, etc.).
        codificacao_fs (str): codificação do sistema de arquivos.
        permissoes_posix (bool): se o SO utiliza permissões POSIX.
    """

    nome_so: str
    case_sensitive: bool
    separador_caminho: str
    suporta_symlinks: bool
    ocultacao_por_atributo: bool
    extensoes_executaveis: list[str]
    diretorios_usuario: list[Path]
    codificacao_fs: str
    permissoes_posix: bool


class IdentificadorSistema:
    """Coleta informações do SO e gera uma configuração adaptada para o buscador.

    Exemplo de uso:
        ident = IdentificadorSistema()
        config = ident.gerar_config()
        buscador = BuscadorSistemaArquivos(config)
    """

    def __init__(self, info: InfoSistema | None = None) -> None:
        """Inicializa o identificador.

        Args:
            info: Instância de InfoSistema pré-preenchida (útil para testes).
                  Se None, a coleta é executada automaticamente.
        """
        self.info: InfoSistema = info if info is not None else self._coletar()
        self._config_cache: ConfigApp | None = None

    # ── Propriedades de conveniência ─────────────────────────────────

    @property
    def eh_windows(self) -> bool:
        """True se o sistema for Windows."""
        return self.info.nome_so == "windows"

    @property
    def eh_linux(self) -> bool:
        """True se o sistema for Linux."""
        return self.info.nome_so == "linux"

    @property
    def eh_mac(self) -> bool:
        """True se o sistema for macOS."""
        return self.info.nome_so == "darwin"

    @property
    def caminho_home(self) -> Path:
        """Caminho do diretório home do usuário."""
        return self.info.diretorios_usuario[0] if self.info.diretorios_usuario else Path.home()

    # ── Coleta de informações ────────────────────────────────────────

    def _coletar(self) -> InfoSistema:
        """Executa todas as verificações e monta o objeto InfoSistema.

        Returns:
            InfoSistema preenchido com dados reais do ambiente.
        """
        nome: str = self._detectar_nome_so()
        case: bool = self._verificar_case_sensitivity()
        sym: bool = self._verificar_symlinks()
        oculto_attr: bool = nome == "windows"
        extensoes: list[str] = self._extensoes_executaveis(nome_so=nome)
        dirs: list[Path] = self._diretorios_usuario(nome_so=nome)

        return InfoSistema(
            nome_so=nome,
            case_sensitive=case,
            separador_caminho=os.sep,
            suporta_symlinks=sym,
            ocultacao_por_atributo=oculto_attr,
            extensoes_executaveis=extensoes,
            diretorios_usuario=dirs,
            codificacao_fs=sys.getfilesystemencoding(),
            permissoes_posix=(os.name == "posix"),
        )

    def _detectar_nome_so(self) -> str:
        """Identifica o nome do sistema operacional via sys.platform.

        Returns:
            'linux', 'windows', 'darwin' ou 'outro'.
        """
        if sys.platform.startswith("linux"):
            return "linux"
        if sys.platform == "darwin":
            return "darwin"
        return "windows" if sys.platform == "win32" else "outro"

    def _verificar_case_sensitivity(self) -> bool:
        """Testa se o sistema de arquivos diferencia maiúsculas/minúsculas.

        Cria um arquivo temporário com nome em maiúsculas e tenta acessá-lo
        em minúsculas.

        Returns:
            True se o sistema de arquivos é case‑sensitive.
        """
        try:
            with tempfile.TemporaryDirectory() as tmp:
                alto: Path = Path(tmp) / "TesteCase.txt"
                baixo: Path = Path(tmp) / "testecase.txt"
                alto.write_text(data="teste")
                return not baixo.exists()
        except Exception:  # pylint: disable=broad-exception-caught
            # Em caso de falha, assume o comportamento típico do SO
            return sys.platform != "win32"

    def _verificar_symlinks(self) -> bool:
        """Verifica se o SO suporta a criação de links simbólicos.

        Returns:
            True se um symlink pôde ser criado com sucesso.
        """
        if hasattr(os, "symlink"):
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    origem: Path = Path(tmp) / "alvo"
                    link: Path = Path(tmp) / "link"
                    origem.touch()
                    os.symlink(origem, link)
                    return True
            except OSError:
                return False
        return False

    def _extensoes_executaveis(self, nome_so: str) -> list[str]:
        """Retorna as extensões consideradas executáveis nativamente.

        Args:
            nome_so: Nome do SO.

        Returns:
            Lista de extensões (incluindo o ponto).
        """
        return [".exe", ".bat", ".cmd", ".com", ".ps1"] if nome_so == "windows" else []

    def _diretorios_usuario(self, nome_so: str) -> list[Path]:
        """Lista diretórios padrão do usuário, dependendo do SO.

        Args:
            nome_so: Nome do SO.

        Returns:
            Lista de Paths comuns (home, documentos, downloads, imagens).
        """
        home: Path = Path.home()
        if nome_so in {"darwin", "windows"}:
            return [home, home / "Documents", home / "Downloads", home / "Pictures"]
        if nome_so == "linux":
            return [home, home / "Documentos", home / "Downloads", home / "Imagens"]
        return [home]

    # ── Geração da configuração ──────────────────────────────────────

    def gerar_config(self) -> ConfigApp:
        """Gera uma ConfigApp adaptada ao SO, com cache interno.

        Utiliza uma configuração base e sobrescreve apenas os campos
        que diferem por plataforma, evitando duplicação.

        Returns:
            Instância de ConfigApp pronta para uso no buscador.
        """
        if self._config_cache is not None:
            return self._config_cache

        # Configuração base comum a todos os SOs
        base = ConfigApp(
            case_sensitive=self.info.case_sensitive,
            seguir_symlinks=self.info.suporta_symlinks,
            ignorar_ocultos=True,
            profundidade_maxima=-1,
            calcular_hashes=False,
            padroes_exclusao=[r"\.git", r"__pycache__", r".*\.pyc"],
            executavel_por_extensao=False,
            extensoes_executaveis=[],
        )

        # Aplica ajustes específicos do Windows
        # No método gerar_config, após o if:

        if self.info.nome_so == "windows":
            config: ConfigApp = cast(
                ConfigApp,
                replace(
                    base,
                    executavel_por_extensao=True,
                    extensoes_executaveis=self.info.extensoes_executaveis,
                ),
            )
        else:
            config = base

        self._config_cache = config
        return config

    def atualizar(self) -> None:
        """Refaz a coleta de informações e invalida o cache da configuração."""
        self.info = self._coletar()
        self._config_cache = None
