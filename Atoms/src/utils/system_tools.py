"""Ferramentas de acesso ao sistema de arquivos para arquivos.

Funções utilitárias para extrair metadados, calcular hashes,
verificar permissões e detecção de ocultos (Windows e Unix).
"""

from __future__ import annotations

import ctypes
import hashlib
import mimetypes
import os
import re
import sys
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Literal, TypedDict

# ── Constantes ──────────────────────────────────────────────────────

EXTENSAO_PADRAO = ".html"
FORMATO_DATA = r"\d{1,2}_\d{1,2}_\d{2}"  # MM_DD_YY


# ── Detecção de ocultos ───────────────────────────────────────────


def _oculto_windows(caminho: Path) -> bool:
    """Verifica se o arquivo tem atributo oculto no Windows."""
    if sys.platform != "win32":
        return False
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(caminho))
        # INVALID_FILE_ATTRIBUTES (constante da API do Windows) é 0xFFFFFFFF,
        # mas sem um `restype` explícito o ctypes trata o retorno como um
        # inteiro assinado (c_int) por padrão — então o valor de erro chega
        # como -1, nunca como 4294967295. Checar só 0xFFFFFFFF fazia esse
        # ramo de erro nunca disparar no Windows real.
        return False if attrs in (-1, 0xFFFFFFFF) else bool(attrs & 0x2)
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def _verificar_oculto(caminho: Path, raiz_busca: Path | None = None) -> bool:
    """Determina se um item é oculto conforme a política do SO.

    No Linux/macOS: qualquer componente do caminho relativo à raiz da
    busca que comece com '.' torna o item oculto.
    No Windows: utiliza a API GetFileAttributesW.
    """
    if sys.platform == "win32":
        return _oculto_windows(caminho=caminho)

    if raiz_busca is None:
        return caminho.name.startswith(".")
    try:
        rel: Path = caminho.relative_to(raiz_busca)
        return any(parte.startswith(".") for parte in rel.parts)
    except ValueError:
        return caminho.name.startswith(".")


# ── Permissões ──────────────────────────────────────────────────────


def _ler_permissoes(caminho: Path) -> tuple[bool, bool, bool]:
    """Retorna permissões de leitura, escrita e execução para o arquivo."""
    try:
        return (
            os.access(str(caminho), os.R_OK),
            os.access(str(caminho), os.W_OK),
            os.access(str(caminho), os.X_OK),
        )
    except OSError:
        return False, False, False


# ── Cálculo de hash ──────────────────────────────────────────────────


def _calcular_hash(caminho: Path, algoritmo: str = "sha256") -> str | None:
    """Calcula o hash do arquivo usando o algoritmo especificado."""
    try:
        hashfile = hashlib.new(algoritmo)
        with open(caminho, "rb") as f:
            for bloco in iter(lambda: f.read(65536), b""):
                hashfile.update(bloco)
        return hashfile.hexdigest()
    except Exception:  # pylint: disable=broad-exception-caught
        return None


# ── Normalização de data digitada pelo usuário (apenas numérica) ───


def normalizar_data(data: str) -> str:
    """Converte uma data numérica (com separadores) para o formato M_D_AA (underscore).

    Exemplos, ambos equivalentes a (year=2026, month=05, day=20):
        "2026-05-20"   -> "5_20_26"
        "20/05/2026"   -> "5_20_26"
        "5-20-2026"    -> "5_20_26"
        "05.20.26"     -> "5_20_26"
        "5-20-26"      -> "5_20_26"
        "2026_05_20"   -> "5_20_26"
    Levanta ValueError se não for possível interpretar como data.
    """
    if not data or not data.strip():
        raise ValueError("data não pode ser vazia")

    # Remove espaços e substitui separadores comuns por '/'
    # para facilitar o parsing com strptime
    data_limpa = data.strip().replace("-", "/").replace(".", "/").replace("_", "/")

    # Tenta uma lista de formatos possíveis
    formatos = (
        "%Y/%m/%d",  # 2026/05/20
        "%d/%m/%Y",  # 20/05/2026
        "%m/%d/%Y",  # 05/20/2026
        "%y/%m/%d",  # 26/05/20
        "%m/%d/%y",  # 05/20/26
        "%d/%m/%y",  # 20/05/26
    )
    dt: datetime | None = None
    for fmt in formatos:
        try:
            dt = datetime.strptime(data_limpa, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        raise ValueError(f"data não reconhecível: {data!r}")

    ano_2: str = dt.strftime("%y")
    return f"{dt.month}_{dt.day}_{ano_2}"


# ── Padrões de busca de regex ──────────────────────────────

SEPARADOR_ACEITO = "[_]"  # separador aceito entre componentes de data


def _construir_padrao_data(data: str) -> str:
    """Recebe M_D_AA (ex: "5_20_26") e retorna regex tolerante."""
    partes: list[str] = data.split("_")
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        return re.escape(data)
    componentes: list[str] = [rf"0?{int(p)}" for p in partes]
    separador: str = r"[_.-]"  # aceita qualquer separador
    return separador.join(componentes)


def _compilar_regex(
    prefixo: str | Iterable[str],
    data: str | None = None,
    separador: str = "_",
    extensoes: tuple[str, ...] = (EXTENSAO_PADRAO,),
    case_sensitive: bool = False,
) -> re.Pattern[str]:
    """Monta e compila uma regex para nomes de arquivo no formato:
    <prefixo><separador><data>.<extensão>  ou <prefixo>.<extensão>.

    `prefixo` aceita uma única string ou um iterável de aliases equivalentes
    (ex.: `("favoritos", "bookmarks")` para aceitar nomes em pt-BR e en-US
    como o mesmo padrão lógico).

    A data, se fornecida, é tolerante a zero à esquerda e a variações de
    separador (ex.: "6_23_26", "06_23_26" e "06-23-26" são equivalentes).
    `extensoes` aceita uma ou mais extensões (ex.: (".html", ".htm")).
    """
    lista_prefixos: list[str] = [prefixo] if isinstance(prefixo, str) else list(prefixo)
    if not lista_prefixos:
        raise ValueError("prefixo não pode ser vazio")

    prefixos_escapados: str = "|".join(re.escape(pattern=p) for p in lista_prefixos)
    prefixo_escapado: str = prefixos_escapados if len(lista_prefixos) == 1 else rf"(?:{prefixos_escapados})"
    separador_escapado: str = re.escape(pattern=separador)
    extensoes_escapadas: str = "|".join(re.escape(pattern=ext) for ext in extensoes)

    if data:
        data_padrao: str = _construir_padrao_data(data=data)
        padrao: str = (
            rf"^{prefixo_escapado}{separador_escapado}{data_padrao}"
            rf"(.*)?({extensoes_escapadas})$"
        )
    else:
        padrao = (
            rf"^{prefixo_escapado}({separador_escapado}{FORMATO_DATA})?"
            rf"(.*)?({extensoes_escapadas})$"
        )
    flags: Literal[0] | re.RegexFlag = 0 if case_sensitive else re.IGNORECASE
    return re.compile(pattern=padrao, flags=flags)


# ── Travessia com poda de diretórios ocultos ────────────────────────


def _caminhos_visiveis(raiz: Path) -> Iterator[Path]:
    """Percorre `raiz` recursivamente retornando apenas arquivos visíveis.

    Diferente de `Path.glob("**/*")`, esta função poda diretórios ocultos
    (nome iniciado com '.') ANTES de descer neles via `os.walk`. Isso evita
    stat()/abertura de milhares de arquivos irrelevantes em `.venv`,
    `.local/share/Trash`, `.npm`, `.cache` etc. — que antes eram varridos
    pelo glob e só descartados depois, em `_validar_caminho`.

    Arquivos ocultos soltos num diretório visível também são ignorados aqui
    (checagem redundante com `_verificar_oculto`, mantida por defesa em
    profundidade caso a função seja usada fora do `Buscador`).
    """
    for dirpath, dirnames, filenames in os.walk(top=raiz):
        # Poda in-place: os.walk não desce em diretórios removidos daqui.
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for nome in sorted(filenames):
            if nome.startswith("."):
                continue
            yield Path(dirpath) / nome


# ── Metadados completos ─────────────────────────────────────────────


class PermissoesMetadados(TypedDict):
    """Formato do sub-dicionário `permissoes` dentro de MetadadosArquivo."""

    legivel: bool
    gravavel: bool
    executavel: bool


class MetadadosArquivo(TypedDict):
    """Formato do dicionário de metadados retornado por
    `_extrair_metadados_arquivo`/`metadados_simples`.

    Cada chave tem um tipo próprio e fixo — por isso um TypedDict, e não
    `dict[str, <união de todos os tipos>]`: essa união genérica faz o
    verificador de tipos achar que *qualquer* valor (inclusive o
    sub-dicionário `permissoes`) pode ser `Path`, `int`, `bool`, `datetime`
    ou `None`, e então reclamar que esses tipos não suportam `__getitem__`
    ao acessar `dados["permissoes"]["legivel"]`.
    """

    caminho: Path
    tamanho: int
    modificado: datetime
    permissoes: PermissoesMetadados
    oculto: bool
    tipo_mime: str | None
    hash_checksum: str | None


def _extrair_metadados_arquivo(
    caminho: Path,
    raiz_busca: Path | None = None,
    calcular_hash: bool = False,
) -> MetadadosArquivo | None:
    """Extrai metadados completos de um arquivo, com hash e tipo MIME."""
    try:
        stat: os.stat_result = caminho.stat()
        legivel, gravavel, executavel = _ler_permissoes(caminho=caminho)
        oculto: bool = (
            _verificar_oculto(caminho=caminho, raiz_busca=raiz_busca) if raiz_busca else caminho.name.startswith(".")
        )

        tipo_mime, _ = mimetypes.guess_type(str(caminho))
        hash_checksum: str | None = _calcular_hash(caminho=caminho) if calcular_hash else None

        return {
            "caminho": caminho,
            "tamanho": stat.st_size,
            "modificado": datetime.fromtimestamp(timestamp=stat.st_mtime),
            "permissoes": {
                "legivel": legivel,
                "gravavel": gravavel,
                "executavel": executavel,
            },
            "oculto": oculto,
            "tipo_mime": tipo_mime,
            "hash_checksum": hash_checksum,
        }
    except OSError:
        return None


# ── Função auxiliar para obter metadados simples (atalho) ──────────


def metadados_simples(caminho: Path) -> MetadadosArquivo | None:
    """Versão simplificada de metadados (sem hash, sem MIME, sem oculto por raiz)."""
    return _extrair_metadados_arquivo(caminho=caminho, raiz_busca=None, calcular_hash=False)
