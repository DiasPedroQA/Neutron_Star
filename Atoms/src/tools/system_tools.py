"""Ferramentas de acesso ao sistema de arquivos.

Funções utilitárias que interagem diretamente com o SO para listar
diretórios, extrair metadados e calcular hashes, sempre tratando
erros de permissão e outros problemas de IO de forma transparente.
"""

from __future__ import annotations

import ctypes
import hashlib
import mimetypes
import os
import sys
from collections.abc import Callable, Generator
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

from src.model.arquivo_info import ItemArquivo
from src.model.diretorio_info import ItemDiretorio
from src.model.item_neutro import ItemBase

# ── Tipagem genérica para a função de tentativa ──────────────────────
T = TypeVar("T")


def _tentar_operacao(
    func: Callable[..., T],
    *args: Any,
    valor_padrao: T | None = None,
    **kwargs: Any,
) -> T | None:
    """Executa func(*args, **kwargs) e retorna valor_padrao em caso de erro.

    Captura exceções comuns de IO (PermissionError, FileNotFoundError, OSError)
    para evitar que a busca seja interrompida por itens inacessíveis.

    Args:
        func: Função a ser executada.
        *args: Argumentos posicionais para func.
        valor_padrao: Valor retornado se ocorrer uma exceção.
        **kwargs: Argumentos nomeados para func.

    Returns:
        O retorno de func ou valor_padrao em caso de falha.
    """
    try:
        return func(*args, **kwargs)
    except OSError:
        return valor_padrao


# ── Detecção de itens ocultos ─────────────────────────────────────────


def _verificar_oculto(caminho: Path, raiz_busca: Path | None = None) -> bool:
    """Determina se um item é oculto conforme a política do SO.

    No Linux/macOS: qualquer componente do caminho relativo à raiz da
    busca que comece com '.' torna o item oculto.
    No Windows: utiliza a API GetFileAttributesW para verificar o atributo
    FILE_ATTRIBUTE_HIDDEN.

    Args:
        caminho: Caminho absoluto do item.
        raiz_busca: Raiz da busca, usada para cálculo do caminho relativo.

    Returns:
        True se o item é considerado oculto.
    """
    if sys.platform == "win32":
        return _oculto_windows(caminho)

    if raiz_busca is None:
        return caminho.name.startswith(".")
    try:
        rel: Path = caminho.relative_to(raiz_busca)
    except ValueError:
        return caminho.name.startswith(".")
    return any(parte.startswith(".") for parte in rel.parts)


def _oculto_windows(caminho: Path) -> bool:
    """Verifica o atributo hidden via API do Windows.

    Args:
        caminho: Caminho absoluto do item.

    Returns:
        True se o atributo FILE_ATTRIBUTE_HIDDEN estiver setado.
    """
    try:
        # Import condicional para evitar erro em sistemas não-Windows
        if sys.platform != "win32":
            return False

        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(caminho))
        return False if attrs == -1 else bool(attrs & 0x2)
    except Exception:  # pylint: disable=broad-exception-caught
        return False


# ── Permissões de acesso ──────────────────────────────────────────────


def _permissoes(caminho: Path) -> tuple[bool, bool, bool]:
    """Retorna as permissões de leitura, escrita e execução para o processo.

    Args:
        caminho: Caminho a ser verificado.

    Returns:
        Tupla (legivel, gravavel, executavel).
    """
    return (
        _tentar_operacao(os.access, caminho, os.R_OK, valor_padrao=False) or False,
        _tentar_operacao(os.access, caminho, os.W_OK, valor_padrao=False) or False,
        _tentar_operacao(os.access, caminho, os.X_OK, valor_padrao=False) or False,
    )


# ── Metadados comuns ─────────────────────────────────────────────────


def _dados_comuns(
    caminho: Path, raiz_busca: Path | None = None
) -> dict[str, str | Path | datetime | int | bool | None]:
    """Extrai os metadados compartilhados entre arquivos e diretórios.

    Args:
        caminho: Caminho absoluto do item.
        raiz_busca: Raiz da busca para cálculo de oculto.

    Returns:
        Dicionário com os campos: caminho, modificado, tamanho,
        legivel, gravavel, executavel, oculto.
    """
    stat: os.stat_result | None = _tentar_operacao(func=caminho.stat)
    if stat is None:
        modificado: datetime | None = None
        tamanho: int | None = None
    else:
        modificado = datetime.fromtimestamp(timestamp=stat.st_mtime)
        tamanho = stat.st_size if caminho.is_file() else None

    legivel, gravavel, executavel = _permissoes(caminho)
    oculto: bool = _verificar_oculto(caminho, raiz_busca)

    return {
        "caminho": caminho.absolute(),
        "modificado": modificado,
        "tamanho": tamanho,
        "legivel": legivel,
        "gravavel": gravavel,
        "executavel": executavel,
        "oculto": oculto,
    }


# ── Factory de itens ──────────────────────────────────────────────────


def criar_item(
    caminho: Path,
    raiz_busca: Path | None = None,
    calcular_hash: bool = False,
) -> ItemBase | None:
    """Cria uma instância de ItemArquivo ou ItemDiretorio a partir do caminho.

    Detecta automaticamente o tipo e preenche todos os metadados disponíveis,
    tratando erros de acesso sem lançar exceções.

    Args:
        caminho: Caminho absoluto do item.
        raiz_busca: Raiz da busca para cálculo de oculto.
        calcular_hash: Se True, calcula o checksum do arquivo.

    Returns:
        Um ItemArquivo, ItemDiretorio ou None se o tipo não puder ser determinado.
    """
    dados: dict[str, Any] = _dados_comuns(caminho=caminho, raiz_busca=raiz_busca)

    eh_arquivo: bool = _tentar_operacao(func=caminho.is_file, valor_padrao=False) or False
    if eh_arquivo:
        return _montar_item_arquivo(dados=dados, caminho=caminho, calcular_hash=calcular_hash)
    eh_diretorio: bool = _tentar_operacao(func=caminho.is_dir, valor_padrao=False) or False

    return _montar_item_diretorio(dados=dados, caminho=caminho) if eh_diretorio else None


def _montar_item_arquivo(
    dados: dict[str, Any],
    caminho: Path,
    calcular_hash: bool,
) -> ItemArquivo:
    """Preenche e retorna um ItemArquivo a partir dos dados comuns e do caminho."""
    tamanho: int | None = _obter_tamanho_seguro(dados=dados, caminho=caminho)
    tipo_mime, _ = mimetypes.guess_type(caminho)
    checksum: str | None = _calcular_hash(caminho=caminho) if calcular_hash else None

    return ItemArquivo(
        caminho=dados["caminho"],
        modificado=dados.get("modificado"),
        tamanho=tamanho,
        legivel=dados["legivel"],
        gravavel=dados["gravavel"],
        executavel=dados["executavel"],
        oculto=dados["oculto"],
        tipo_mime=tipo_mime,
        hash_checksum=checksum,
    )


def _montar_item_diretorio(
    dados: dict[str, Any],
    caminho: Path,
) -> ItemDiretorio:
    """Preenche e retorna um ItemDiretorio a partir dos dados comuns e do caminho."""
    qtd: int | None = None
    if dados.get("executavel"):
        lista: None | list[Any] = _tentar_operacao(func=os.listdir, args=(caminho,), valor_padrao=[])
        qtd = len(lista) if lista is not None else None

    return ItemDiretorio(
        caminho=dados["caminho"],
        modificado=dados.get("modificado"),
        tamanho=dados.get("tamanho"),
        legivel=dados["legivel"],
        gravavel=dados["gravavel"],
        executavel=dados["executavel"],
        oculto=dados["oculto"],
        qtd_itens=qtd,
    )


def _obter_tamanho_seguro(
    dados: dict[str, Any],
    caminho: Path,
) -> int | None:
    """Obtém o tamanho do arquivo, usando fallback via stat se necessário."""
    tamanho: int | None = dados.get("tamanho")
    if tamanho is None:
        stat_fallback: os.stat_result | None = _tentar_operacao(func=caminho.stat)
        if stat_fallback is not None:
            return stat_fallback.st_size
    return tamanho


def obter_info_arquivo(
    caminho: Path,
    raiz_busca: Path | None = None,
    calcular_hash: bool = False,
) -> ItemArquivo | None:
    """Atalho para obter um ItemArquivo a partir de um caminho.

    Args:
        caminho: Caminho do arquivo.
        raiz_busca: Raiz da busca para cálculo de oculto.
        calcular_hash: Se True, calcula o checksum.

    Returns:
        Um ItemArquivo ou None se o caminho não for um arquivo acessível.
    """
    item: ItemBase | None = criar_item(caminho=caminho, raiz_busca=raiz_busca, calcular_hash=calcular_hash)
    return item if isinstance(item, ItemArquivo) else None


# ── Listagem de diretórios ────────────────────────────────────────────


def listar_diretorio(
    caminho: Path,
    raiz_busca: Path | None = None,
    seguir_symlinks: bool = False,
    padrao_glob: str | None = None,
) -> list[ItemBase]:
    """Lista o conteúdo imediato de um diretório.

    Args:
        caminho: Diretório a ser listado.
        raiz_busca: Raiz da busca para cálculo de oculto.
        seguir_symlinks: Se True, segue links simbólicos.
        padrao_glob: Padrão glob para filtrar entradas (ex.: "*.txt").

    Returns:
        Lista de ItemArquivo e ItemDiretorio, sem filhos recursivos.
    """
    if padrao_glob:
        entradas_iter: Generator[Path, None, None] | list[str] | None = _tentar_operacao(
            caminho.glob, padrao_glob, valor_padrao=[]
        )
    else:
        entradas_iter = _tentar_operacao(caminho.iterdir, valor_padrao=[])

    itens: list[ItemBase] = []
    # entradas_iter pode ser list[str] (raro) ou Generator[Path] ou list[Path]
    for entrada in entradas_iter or []:
        # Garante que entrada seja Path
        entrada_path: Path = Path(entrada) if isinstance(entrada, str) else entrada

        # Pula symlinks se configurado
        if not seguir_symlinks and _tentar_operacao(entrada_path.is_symlink, valor_padrao=True):
            continue

        item = criar_item(entrada_path, raiz_busca)
        if item is not None:
            itens.append(item)
    return itens


# ── Cálculo de hash ──────────────────────────────────────────────────


def _calcular_hash(caminho: Path, algoritmo: str = "sha256") -> str | None:
    """Calcula o hash de um arquivo.

    Args:
        caminho: Caminho do arquivo.
        algoritmo: Nome do algoritmo de hash (padrão: sha256).

    Returns:
        String hexadecimal do hash ou None em caso de erro.
    """
    try:
        h = hashlib.new(algoritmo)
        with open(caminho, "rb") as f:
            for bloco in iter(lambda: f.read(65536), b""):
                h.update(bloco)
        return h.hexdigest()
    except Exception:  # pylint: disable=broad-exception-caught
        return None
