# Atoms/src/models/buscador.py
# pylint: disable=too-few-public-methods

"""Módulo de varredura de disco e gerenciamento de caminhos do sistema."""

import getpass
import os
import platform
from datetime import UTC, datetime
from pathlib import Path

from .entidades import (
    AtalhoSugerido,
    InfoSistema,
    MetadadosArquivo,
    NoArvore,
    ResultadoEscaneamento,
)

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


class GerenciadorSistemaLocal:
    """Coleta informações ambientais do sistema operacional e atalhos da Home."""

    __slots__ = ()

    @staticmethod
    def obter_informacoes_so() -> InfoSistema:
        """Retorna dados do S.O., usuário atual e atalhos rápidos."""
        home_usuario: Path = Path.home()
        usuario_atual: str = getpass.getuser()
        sistema_op: str = platform.system()
        versao_so: str = platform.release()

        atalhos: list[AtalhoSugerido] = [{"label": "Pasta Home (~/)", "caminho": "~/"}]
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


class BuscadorLocal:
    """Executa a varredura profunda no disco e constrói a árvore hierárquica."""

    def __init__(self, max_arquivos: int = 5000) -> None:
        self.max_arquivos: int = max_arquivos

    def _tem_marcadores_netscape(self, arquivo: Path, amostra_bytes: int = _AMOSTRA_BYTES) -> bool:
        """Heurística rápida: verifica se o arquivo possui marcadores Netscape (<DL> e <DT>)."""
        try:
            with open(file=arquivo, mode="rb") as f:
                amostra: bytes = f.read(amostra_bytes).lower()
        except OSError:
            return False
        return b"<dl" in amostra and b"<dt" in amostra

    def _normalizar_sufixos(self, extensao: str) -> list[str]:
        """Normaliza a extensão informada em uma lista de sufixos aceitos."""
        ext: str = extensao.strip().lower()
        if ext in {"", "todos", "*", "todas"}:
            return [".html", ".htm"]
        if not ext.startswith("."):
            ext = f".{ext}"
        return [ext]

    @staticmethod
    def validar_pasta(caminho: Path) -> bool:
        """Verifica se o caminho existe e é um diretório válido."""
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
        """Localiza arquivos HTML respeitando a profundidade máxima."""
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

    def _obter_metadados(self, arquivo: Path) -> tuple[MetadadosArquivo | None, int]:
        """Obtém metadados detalhados de um arquivo."""
        try:
            status: os.stat_result = arquivo.stat()
        except OSError:
            return None, 0

        metadados: MetadadosArquivo = {
            "nome": arquivo.name,
            "caminho_completo": str(arquivo),
            "tamanho_kb": round(status.st_size / 1024, 2),
            "modificado_em": datetime.fromtimestamp(timestamp=status.st_mtime, tz=UTC).strftime(
                format="%d/%m/%Y %H:%M:%S"
            ),
            "selecionado": False,
            "elegivel": self._tem_marcadores_netscape(arquivo),
        }
        return metadados, status.st_size

    @staticmethod
    def _obter_ou_criar_pasta(
        parent_no: NoArvore,
        parent_path: str,
        parte: str,
        cache_pastas: dict[str, NoArvore],
    ) -> tuple[NoArvore, str]:
        """Retorna nó da pasta criando-o se ainda não existir."""
        current_path: str = f"{parent_path}/{parte}" if parent_path else parte
        if current_path not in cache_pastas:
            novo: NoArvore = {
                "type": "folder",
                "name": parte,
                "path": current_path,
                "children": [],
            }
            if "children" in parent_no:
                parent_no["children"].append(novo)
            cache_pastas[current_path] = novo
        return cache_pastas[current_path], current_path

    @staticmethod
    def _adicionar_arquivo(parent_no: NoArvore, arq: MetadadosArquivo, rel: Path) -> None:
        """Anexa nó de arquivo à pasta pai."""
        novo_arquivo: NoArvore = {
            "type": "file",
            "name": rel.parts[-1],
            "path": str(rel),
            "size_kb": float(arq.get("tamanho_kb", 0)),
            "elegivel": bool(arq.get("elegivel", False)),
        }
        if "children" in parent_no:
            parent_no["children"].append(novo_arquivo)

    @classmethod
    def _ordenar_arvore(cls, no: NoArvore) -> None:
        """Ordena recursivamente: pastas primeiro, depois arquivos alfabeticamente."""
        if no.get("type") != "folder" or "children" not in no:
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
        arquivos: list[MetadadosArquivo],
        caminho_raiz: Path,
    ) -> list[NoArvore]:
        """Constrói a árvore hierárquica a partir da lista plana de arquivos."""
        raiz_visual: NoArvore = {
            "type": "folder",
            "name": caminho_raiz.name,
            "path": "",
            "children": [],
        }
        cache_pastas: dict[str, NoArvore] = {"": raiz_visual}

        for arq in arquivos:
            caminho_arq: Path = Path(str(arq["caminho_completo"])).resolve()
            try:
                rel: Path = caminho_arq.relative_to(caminho_raiz)
            except ValueError:
                continue

            partes: tuple[str, ...] = rel.parts
            if not partes:
                continue

            parent_no: NoArvore = raiz_visual
            parent_path: str = ""
            for parte in partes[:-1]:
                parent_no, parent_path = cls._obter_ou_criar_pasta(
                    parent_no, parent_path, parte, cache_pastas
                )

            cls._adicionar_arquivo(parent_no, arq, rel)

        cls._ordenar_arvore(raiz_visual)
        return raiz_visual.get("children", [])

    def escanear(
        self,
        caminho: Path,
        extensao: str = ".html",
        profundidade: int = 5,
    ) -> ResultadoEscaneamento:
        """Executa a varredura completa retornando o resumo e a árvore."""
        caminho_resolvido: Path = caminho.expanduser().resolve()
        if not self.validar_pasta(caminho=caminho_resolvido):
            raise FileNotFoundError(f"A pasta '{caminho_resolvido}' não pôde ser encontrada.")

        sufixos: list[str] = self._normalizar_sufixos(extensao=extensao)
        profundidade_efetiva: int = max(0, profundidade)

        arquivos_encontrados: list[MetadadosArquivo] = []
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
        arvore: list[NoArvore] = self._construir_arvore(
            arquivos=arquivos_encontrados, caminho_raiz=caminho_resolvido
        )

        return {
            "caminho_varrido": str(caminho_resolvido),
            "extensao_usada": ",".join(sufixos),
            "profundidade_usada": profundidade_efetiva,
            "total_arquivos": len(arquivos_encontrados),
            "total_elegiveis": elegiveis,
            "tamanho_total_mb": round(number=tamanho_total_bytes / (1024 * 1024), ndigits=2),
            "data_busca": datetime.now(tz=UTC).strftime(format="%d/%m/%Y %H:%M:%S"),
            "arquivos": arquivos_encontrados,
            "tree": arvore,
        }
