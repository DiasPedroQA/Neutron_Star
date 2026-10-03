# Atoms/tests/arquitetura/test_convencao_imports.py

"""Guarda de arquitetura: uma única convenção de import (``src.*``) em todo o projeto.

Contexto: a mistura de ``from models.x`` (absoluto, raiz implícita ``src/``) com
``from ..utils.x`` (relativo) quebrou a coleta da suíte inteira. Este teste impede a volta.
"""

import ast
from pathlib import Path

RAIZ: Path = Path(__file__).resolve().parents[2]
PACOTES_INTERNOS: frozenset[str] = frozenset({"models", "utils", "controllers", "views"})


def _imports_fora_da_convencao(codigo: str) -> list[str]:
    """Retorna imports absolutos de pacotes internos sem o prefixo ``src.``."""
    proibidos: list[str] = []
    for no in ast.walk(ast.parse(codigo)):
        if isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            if no.module.split(".")[0] in PACOTES_INTERNOS:
                proibidos.append(no.module)
        elif isinstance(no, ast.Import):
            proibidos.extend(
                alias.name for alias in no.names if alias.name.split(".")[0] in PACOTES_INTERNOS
            )
    return proibidos


def test_detector_pega_o_import_que_quebrou_a_suite() -> None:
    """Detecta imports absolutos de pacotes internos sem o prefixo ``src.``."""
    assert _imports_fora_da_convencao(codigo="from models.conversor import ConversorService") == [
        "models.conversor"
    ]


def test_detector_aceita_import_relativo_e_import_com_prefixo_src() -> None:
    """Aceita imports relativos e imports absolutos já prefixados com ``src.``."""
    codigo: str = "from ..models.conversor import X\nfrom src.utils.parser import Y\n"

    assert not _imports_fora_da_convencao(codigo)


def test_codigo_de_producao_segue_a_convencao_de_imports() -> None:
    """Garante que os arquivos de produção não tenham imports fora da convenção."""
    arquivos: list[Path] = [*RAIZ.joinpath("src").rglob("*.py"), RAIZ / "main.py", RAIZ / "cli.py"]
    violacoes: dict[str, list[str]] = {}
    for arquivo in arquivos:
        if encontrados := _imports_fora_da_convencao(codigo=arquivo.read_text(encoding="utf-8")):
            violacoes[str(arquivo.relative_to(RAIZ))] = encontrados

    assert not violacoes, f"Imports fora da convenção src.*: {violacoes}"


def test_raiz_do_projeto_nao_e_pacote_python() -> None:
    """``Atoms/__init__.py`` duplicava a identidade dos módulos (``src.x`` vs ``Atoms.src.x``)."""
    assert not (RAIZ / "__init__.py").exists()
