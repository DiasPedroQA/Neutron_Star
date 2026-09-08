# Atoms/src/infra/buscador.py

"""Implementação concreta de varredura do S.O. e gerenciamento de caminhos."""

import getpass
import os
import platform
from datetime import UTC, datetime
from pathlib import Path

from ..aplicacao.portas import BuscadorPort, GerenciadorSistemaPort

# Whitelist de pastas recomendadas na Home do usuário para navegação ágil
NOMES_PASTAS_RECOMENDADAS: list[str] = [
    "Documentos",
    "Documents",
    "Downloads",
    "Desktop",
    "Área de Trabalho",
    "Imagens",
    "Pictures",
    "Videos",
]

# Diretórios de sistema pesados ignorados na busca profunda por performance
PASTAS_IGNORADAS: set[str] = {
    "node_modules",
    ".git",
    ".github",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "AppData",
    "Library",
    "Local Settings",
    "Application Data",
    "Temp",
    "Cache",
    "SystemVolumeInformation",
    "$RECYCLE.BIN",
}


class GerenciadorSistemaLocal(
    GerenciadorSistemaPort,
):
    """Implementação real de coleta ambiental de dados e atalhos do S.O."""

    # A porta define o único método público necessário nesta implementação.
    __slots__ = ()

    def obter_informacoes_so(self) -> dict[str, str | list[dict[str, str]]]:
        """Coleta e retorna dados do S.O., usuário logado e atalhos físicos."""
        home_usuario: Path = Path.home()
        usuario_atual: str = getpass.getuser()
        sistema_op: str = platform.system()
        versao_so: str = platform.release()

        # Atalhos amigáveis baseados em pastas existentes fisicamente na Home
        atalhos: list[dict[str, str]] = [{"label": "Pasta Home (~/)", "caminho": "~/"}]

        for nome in NOMES_PASTAS_RECOMENDADAS:
            caminho_completo: Path = home_usuario / nome
            if caminho_completo.is_dir():
                atalhos.append({"label": f"{nome} (~/{nome})", "caminho": f"~/{nome}"})

        atalhos.append({"label": "Outro Caminho...", "caminho": "custom"})

        return {
            "so": f"{sistema_op} ({versao_so})",
            "usuario": usuario_atual,
            "pasta_home": str(home_usuario),
            "atalhos_sugeridos": atalhos,
        }


class BuscadorLocal(BuscadorPort):
    """Implementação física de varredura profunda e performática do disco."""

    def __init__(self, max_profundidade: int = 5, max_arquivos: int = 5000) -> None:
        """Configura os limites de segurança de recursão e contagem."""
        self.max_profundidade: int = max_profundidade
        self.max_arquivos: int = max_arquivos

    def validar_pasta(self, caminho: Path) -> bool:
        """Verifica se a pasta informada existe e é um diretório acessível."""
        try:
            caminho_resolvido: Path = caminho.expanduser().resolve()
            return caminho_resolvido.is_dir()
        except (OSError, RuntimeError, ValueError):
            return False

    def _localizar_html(self, caminho: Path) -> set[Path]:
        """Localiza arquivos HTML respeitando os limites configurados."""
        encontrados: set[Path] = set()
        examinados = 0
        for raiz, pastas, arquivos in os.walk(caminho):
            examinados += len(arquivos)
            if examinados > self.max_arquivos:
                break
            caminho_raiz = Path(raiz)
            profundidade: int = len(caminho_raiz.relative_to(caminho).parts)
            if profundidade > self.max_profundidade:
                pastas[:] = []
                continue
            pastas[:] = [
                pasta
                for pasta in pastas
                if not pasta.startswith(".") and pasta not in PASTAS_IGNORADAS
            ]
            encontrados.update(
                caminho_raiz / nome
                for nome in arquivos
                if not nome.startswith(".") and nome.lower().endswith((".html", ".htm"))
            )
        return encontrados

    @staticmethod
    def _obter_metadados(arquivo: Path) -> tuple[dict[str, str | float | bool], int] | None:
        """Obtém metadados do arquivo, ignorando arquivos indisponíveis."""
        try:
            status: os.stat_result = arquivo.stat()
        except OSError:
            return None
        metadados: dict[str, str | float | bool] = {
            "nome": arquivo.name,
            "caminho_completo": str(arquivo),
            "tamanho_kb": round(status.st_size / 1024, 2),
            "modificado_em": datetime.fromtimestamp(timestamp=status.st_mtime, tz=UTC).strftime(
                format="%d/%m/%Y %H:%M:%S"
            ),
            "selecionado": True,
        }
        return metadados, status.st_size

    def escanear(
        self,
        caminho: Path,
    ) -> dict[
        str,
        str | int | float | list[dict[str, str | float | bool]],
    ]:
        """Varre recursivamente o diretório resolvido por arquivos .html/.htm."""
        caminho_resolvido: Path = caminho.expanduser().resolve()
        if not self.validar_pasta(caminho=caminho_resolvido):
            raise FileNotFoundError(f"A pasta '{caminho_resolvido}' não pôde ser encontrada.")

        arquivos_encontrados: list[dict[str, str | float | bool]] = []
        tamanho_total_bytes = 0
        for arquivo in sorted(self._localizar_html(caminho=caminho_resolvido)):
            resultado: (
                tuple[
                    dict[str, str | float | bool],
                    int,
                ]
                | None
            ) = self._obter_metadados(arquivo)
            if resultado is not None:
                metadados, tamanho = resultado
                arquivos_encontrados.append(metadados)
                tamanho_total_bytes += tamanho

        return {
            "caminho_varrido": str(caminho_resolvido),
            "total_arquivos": len(arquivos_encontrados),
            "tamanho_total_mb": round(tamanho_total_bytes / (1024 * 1024), 2),
            "data_busca": datetime.now(tz=UTC).strftime(format="%d/%m/%Y %H:%M:%S"),
            "arquivos": arquivos_encontrados,
        }
