# Atoms/src/infra/buscador.py
# pylint: disable=too-few-public-methods

"""Implementação concreta de varredura do S.O. e gerenciamento de caminhos."""

import getpass
import os
import platform
from datetime import UTC, datetime
from pathlib import Path

from ..aplicacao.portas import BuscadorPort, GerenciadorSistemaPort

NOMES_PASTAS_RECOMENDADAS: list[str] = [
    "Documentos",
    "Documents",
    "Downloads",
    "Desktop",
    "Área de Trabalho",
    "Imagens",
    "Pictures",
    "Videos",
    "Vídeos",
]

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

_AMOSTRA_BYTES: int = 64 * 1024

# Tipos auxiliares para legibilidade
_TipoMetadado = dict[str, str | float | bool]
_TipoResultadoMetadado = tuple[_TipoMetadado | None, int]


def _normalizar_sufixos(extensao: str) -> list[str]:
    """Normaliza a extensão informada em uma lista de sufixos aceitos.

    Devolve uma lista (e não tupla) porque o número de sufixos varia entre 1 e 2
    e a regra Sonar S8495 exige que funções que retornam tuplas devolvam sempre
    o mesmo comprimento.
    """
    ext: str = extensao.strip().lower()
    if ext in {"", "todos", "*", "todas"}:
        return [".html", ".htm"]
    if not ext.startswith("."):
        ext = f".{ext}"
    return [ext]


def _tem_marcadores_netscape(arquivo: Path, amostra_bytes: int = _AMOSTRA_BYTES) -> bool:
    """Heurística estrutural rápida: o arquivo tem ``<DL>`` e ``<DT>``?"""
    try:
        with open(file=arquivo, mode="rb") as f:
            amostra: bytes = f.read(amostra_bytes).lower()
    except OSError:
        return False
    return b"<dl" in amostra and b"<dt" in amostra


class GerenciadorSistemaLocal(GerenciadorSistemaPort):
    """Implementação real de coleta ambiental de dados e atalhos do S.O."""

    __slots__ = ()

    def obter_informacoes_so(self) -> dict[str, str | list[dict[str, str]]]:
        home_usuario: Path = Path.home()
        usuario_atual: str = getpass.getuser()
        sistema_op: str = platform.system()
        versao_so: str = platform.release()

        atalhos: list[dict[str, str]] = [{"label": "Pasta Home (~/)", "caminho": "~/"}]
        for nome in NOMES_PASTAS_RECOMENDADAS:
            caminho_completo: Path = home_usuario / nome
            if caminho_completo.is_dir():
                atalhos.append(
                    {
                        "label": f"{nome} ({home_usuario}/{nome})",
                        "caminho": f"~/{nome}",
                    }
                )
        atalhos.append({"label": "Outro Caminho...", "caminho": "editável"})

        return {
            "so": f"{sistema_op} ({versao_so})",
            "usuario": usuario_atual,
            "pasta_home": str(home_usuario),
            "atalhos_sugeridos": atalhos,
        }


class BuscadorLocal(BuscadorPort):
    """Implementação física de varredura profunda e performática do disco."""

    def __init__(self, max_arquivos: int = 5000) -> None:
        self.max_arquivos: int = max_arquivos

    def validar_pasta(self, caminho: Path) -> bool:
        try:
            caminho_resolvido: Path = caminho.expanduser().resolve()
            return caminho_resolvido.is_dir()
        except (OSError, RuntimeError, ValueError):
            return False

    def _localizar_html(
        self,
        caminho: Path,
        sufixos: list[str],
        profundidade_max: int,
    ) -> set[Path]:
        encontrados: set[Path] = set()
        examinados = 0

        for raiz, pastas, arquivos in os.walk(caminho):
            examinados += len(arquivos)
            if examinados > self.max_arquivos:
                break

            caminho_raiz = Path(raiz)
            profundidade: int = len(caminho_raiz.relative_to(caminho).parts)

            if profundidade > profundidade_max:
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
                if not nome.startswith(".") and any(nome.lower().endswith(s) for s in sufixos)
            )

        return encontrados

    @staticmethod
    def _obter_metadados(arquivo: Path) -> _TipoResultadoMetadado:
        """Obtém metadados do arquivo.

        Sempre devolve uma tupla de 2 elementos: ``(metadados_ou_None, tamanho)``.
        Se o arquivo não puder ser lido, o primeiro elemento é ``None`` e o
        segundo é ``0`` — mantendo o contrato de "sempre 2-tupla" (Sonar S8495).
        """
        try:
            status: os.stat_result = arquivo.stat()
        except OSError:
            return None, 0

        metadados: _TipoMetadado = {
            "nome": arquivo.name,
            "caminho_completo": str(arquivo),
            "tamanho_kb": round(status.st_size / 1024, 2),
            "modificado_em": datetime.fromtimestamp(timestamp=status.st_mtime, tz=UTC).strftime(
                format="%d/%m/%Y %H:%M:%S"
            ),
            "selecionado": False,
            "elegivel": _tem_marcadores_netscape(arquivo),
        }
        return metadados, status.st_size

    # ------------------------------------------------------------------
    # Construção da árvore hierárquica
    # ------------------------------------------------------------------

    @staticmethod
    def _obter_ou_criar_pasta(
        parent_no: dict,
        parent_path: str,
        parte: str,
        cache_pastas: dict[str, dict],
    ) -> tuple[dict, str]:
        """Retorna (nó da pasta, caminho atualizado). Cria o nó se ainda não existir."""
        current_path = f"{parent_path}/{parte}" if parent_path else parte
        if current_path not in cache_pastas:
            novo: dict = {
                "type": "folder",
                "name": parte,
                "path": current_path,
                "children": [],
            }
            parent_no["children"].append(novo)
            cache_pastas[current_path] = novo
        return cache_pastas[current_path], current_path

    @staticmethod
    def _adicionar_arquivo(parent_no: dict, arq: _TipoMetadado, rel: Path) -> None:
        """Anexa um nó de arquivo ao nó pai, usando o caminho relativo."""
        parent_no["children"].append(
            {
                "type": "file",
                "name": rel.parts[-1],
                "path": str(rel),
                "size_kb": float(arq.get("tamanho_kb", 0)),
                "elegivel": bool(arq.get("elegivel", False)),
            }
        )

    @classmethod
    def _ordenar_arvore(cls, no: dict) -> None:
        """Ordena recursivamente: pastas antes de arquivos, depois alfabético."""
        if no.get("type") != "folder":
            return
        no["children"].sort(
            key=lambda c: (
                0 if c.get("type") == "folder" else 1,
                c.get("name", "").lower(),
            )
        )
        for filho in no["children"]:
            cls._ordenar_arvore(filho)

    @classmethod
    def _construir_arvore(
        cls,
        arquivos: list[_TipoMetadado],
        caminho_raiz: Path,
    ) -> list[dict]:
        """Constrói hierarquia de pastas/arquivos a partir da lista plana.

        Devolve uma lista de nós no formato esperado pelo frontend:
        ``{type, name, path, size_kb?, elegivel?, children?}``.
        """
        raiz_visual: dict = {
            "type": "folder",
            "name": caminho_raiz.name,
            "path": "",
            "children": [],
        }
        cache_pastas: dict[str, dict] = {"": raiz_visual}

        for arq in arquivos:
            caminho_arq: Path = Path(str(arq["caminho_completo"])).resolve()
            try:
                rel: Path = caminho_arq.relative_to(caminho_raiz)
            except ValueError:
                continue

            partes: tuple[str, ...] = rel.parts
            if not partes:
                continue

            parent_no: dict = raiz_visual
            parent_path: str = ""
            for parte in partes[:-1]:
                parent_no, parent_path = cls._obter_ou_criar_pasta(
                    parent_no, parent_path, parte, cache_pastas
                )

            cls._adicionar_arquivo(parent_no, arq, rel)

        cls._ordenar_arvore(raiz_visual)
        return raiz_visual["children"]

    def escanear(
        self,
        caminho: Path,
        extensao: str = ".html",
        profundidade: int = 5,
    ) -> dict[str, str | int | float | list]:
        caminho_resolvido: Path = caminho.expanduser().resolve()
        if not self.validar_pasta(caminho=caminho_resolvido):
            raise FileNotFoundError(f"A pasta '{caminho_resolvido}' não pôde ser encontrada.")

        sufixos: list[str] = _normalizar_sufixos(extensao=extensao)
        profundidade_efetiva: int = max(0, profundidade)

        arquivos_encontrados: list[_TipoMetadado] = []
        tamanho_total_bytes: int = 0

        for arquivo in sorted(
            self._localizar_html(
                caminho=caminho_resolvido,
                sufixos=sufixos,
                profundidade_max=profundidade_efetiva,
            )
        ):
            metadados, tamanho = self._obter_metadados(arquivo)
            if metadados is not None:
                arquivos_encontrados.append(metadados)
                tamanho_total_bytes += tamanho

        elegiveis: int = sum(bool(a.get("elegivel")) for a in arquivos_encontrados)
        arvore = self._construir_arvore(
            arquivos=arquivos_encontrados, caminho_raiz=caminho_resolvido
        )

        return {
            "caminho_varrido": str(caminho_resolvido),
            "extensao_usada": ",".join(sufixos),
            "profundidade_usada": profundidade_efetiva,
            "total_arquivos": len(arquivos_encontrados),
            "total_elegiveis": elegiveis,
            "tamanho_total_mb": round(tamanho_total_bytes / (1024 * 1024), 2),
            "data_busca": datetime.now(tz=UTC).strftime(format="%d/%m/%Y %H:%M:%S"),
            "arquivos": arquivos_encontrados,
            "tree": arvore,
        }
