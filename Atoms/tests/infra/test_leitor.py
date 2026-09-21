# Atoms/tests/infra/test_leitor.py
# pylint: disable=redefined-outer-name

"""Testes unitários do leitor de arquivos HTML (``src/infra/leitor.py``)."""

from pathlib import Path

import pytest

from src.infra.leitor import LeitorHTML


@pytest.fixture
def leitor() -> LeitorHTML:
    """Instância do leitor sob teste."""
    return LeitorHTML()


@pytest.mark.parametrize(
    "conteudo",
    ["Olá, favoritos!", ""],
    ids=["utf8_com_acentos", "arquivo_vazio"],
)
def test_le_utf8_e_arquivo_vazio_sem_alterar_o_conteudo(
    leitor: LeitorHTML, tmp_path: Path, conteudo: str
) -> None:
    """UTF-8 (inclusive vazio) deve ser devolvido exatamente como gravado."""
    arquivo: Path = tmp_path / "favoritos.html"
    arquivo.write_text(data=conteudo, encoding="utf-8")

    assert leitor.ler_arquivo(caminho=arquivo) == conteudo


def test_le_arquivo_latin1_sem_mojibake(leitor: LeitorHTML, tmp_path: Path) -> None:
    """Arquivo em Latin-1 deve ser decodificado corretamente (fallback do UTF-8)."""
    conteudo: str = "Favoritos: ação, opção, informação"
    arquivo: Path = tmp_path / "latin1.html"
    arquivo.write_text(data=conteudo, encoding="latin-1")

    assert leitor.ler_arquivo(caminho=arquivo) == conteudo


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG confirmado: 'latin-1' decodifica qualquer byte, então 'cp1252' nunca é "
        "alcançado e aspas curvas/euro viram caracteres de controle (\\x93, \\x94, \\x80)."
    ),
)
def test_le_arquivo_cp1252_preserva_aspas_curvas_e_euro(leitor: LeitorHTML, tmp_path: Path) -> None:
    """Exports antigos do Windows (cp1252) devem manter “aspas” e €."""
    conteudo: str = "“aspas” € ação"
    arquivo: Path = tmp_path / "windows.html"
    arquivo.write_bytes(data=conteudo.encode(encoding="cp1252"))

    assert leitor.ler_arquivo(caminho=arquivo) == conteudo


def test_arquivo_inexistente_levanta_file_not_found(leitor: LeitorHTML, tmp_path: Path) -> None:
    """Ler um caminho inexistente deve propagar ``FileNotFoundError``."""
    with pytest.raises(FileNotFoundError):
        leitor.ler_arquivo(caminho=tmp_path / "nao-existe.html")
