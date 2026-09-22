# Atoms/tests/infra/test_leitor.py
# pylint: disable=redefined-outer-name

"""Testes unitários para o leitor de arquivos HTML e cascata de encodings."""

from pathlib import Path

import pytest

from infra.leitor import LeitorLocal


@pytest.fixture
def leitor() -> LeitorLocal:
    """Fixture que fornece uma instância isolada de LeitorLocal."""
    return LeitorLocal()


@pytest.mark.parametrize(
    argnames=("conteudo_esperado", "arquivo_nome"),
    argvalues=[
        (
            "<html><body><h1>Favoritos com acentuação: áéíóú ç</h1></body></html>",
            "utf8_com_acentos.html",
        ),
        ("", "arquivo_vazio.html"),
    ],
)
def test_le_utf8_e_arquivo_vazio_sem_alterar_o_conteudo(
    leitor: LeitorLocal, tmp_path: Path, conteudo_esperado: str, arquivo_nome: str
) -> None:
    """Garante que arquivos em UTF-8 nativo ou vazios são lidos com total fidelidade."""
    arquivo: Path = tmp_path / arquivo_nome
    arquivo.write_text(data=conteudo_esperado, encoding="utf-8")

    resultado: str = leitor.ler_arquivo(caminho=arquivo)
    assert resultado == conteudo_esperado


def test_le_arquivo_latin1_sem_mojibake(leitor: LeitorLocal, tmp_path: Path) -> None:
    """Garante que arquivos legados em ISO-8859-1 (Latin-1)
    são decodificados sem caracteres quebrados."""
    conteudo = "<html><body>Favoritos da Seção de TI: Produção & Manutenção</body></html>"
    arquivo: Path = tmp_path / "bookmarks_latin1.html"
    arquivo.write_bytes(data=conteudo.encode(encoding="latin-1"))

    resultado: str = leitor.ler_arquivo(caminho=arquivo)
    assert resultado == conteudo


def test_le_arquivo_cp1252_preserva_aspas_curvas_e_euro(
    leitor: LeitorLocal, tmp_path: Path
) -> None:
    """Garante que caracteres exclusivos do Windows-1252
    (como €, aspas curvas e travessão) são preservados."""
    conteudo = "<html><body>Preço: 100 € — Livro: “Guia do QA”</body></html>"
    arquivo: Path = tmp_path / "bookmarks_cp1252.html"
    # 0x80 (€), 0x93 (“), 0x94 (”), 0x97 (—)
    arquivo.write_bytes(data=conteudo.encode(encoding="cp1252"))

    resultado: str = leitor.ler_arquivo(caminho=arquivo)
    assert "100 €" in resultado
    assert "“Guia do QA”" in resultado
    assert "—" in resultado
    assert resultado == conteudo


def test_arquivo_inexistente_levanta_file_not_found(leitor: LeitorLocal, tmp_path: Path) -> None:
    """Garante que tentar ler um arquivo fisicamente inexistente levanta FileNotFoundError."""
    caminho_inexistente: Path = tmp_path / "nao_existe.html"
    with pytest.raises(expected_exception=FileNotFoundError):
        leitor.ler_arquivo(caminho=caminho_inexistente)
