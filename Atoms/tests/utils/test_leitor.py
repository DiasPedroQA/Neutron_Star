# Atoms/tests/models/test_leitor.py

"""Testes unitários para o leitor físico e cascata de encodings."""

from collections.abc import Callable
from pathlib import Path

import pytest

from src.utils.leitor import LeitorLocal


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def escrever_bytes(tmp_path: Path) -> Callable[..., Path]:
    """Grava bytes crus em arquivo temporário e devolve o Path."""

    def _escrever(nome: str, conteudo: bytes) -> Path:
        caminho: Path = tmp_path / nome
        caminho.write_bytes(data=conteudo)
        return caminho

    return _escrever


# ---------------------------------------------------------------------------
# 1ª tentativa: UTF-8 (parametrizado)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames=("conteudo", "nome_arquivo"),
    argvalues=[
        pytest.param("Olá, mundo!", "saudacao.txt", id="utf8-portugues"),
        pytest.param(
            "Relatório de vendas — março",
            "relatorio.txt",
            id="utf8-acentos-travessao",
        ),
        pytest.param(
            "<p>Acentuação: á, é, í, ó, ú, ç, ã</p>",
            "acentos.html",
            id="utf8-html-acentuado",
        ),
        pytest.param(
            "Linha 1\nLinha 2\nLinha 3",
            "multiplas-linhas.txt",
            id="utf8-multiplas-linhas",
        ),
        pytest.param(
            "Emoji: ☕ 🚀 日本語",
            "unicode.txt",
            id="utf8-unicode-multibyte",
        ),
    ],
)
def test_le_conteudo_utf8(tmp_path: Path, conteudo: str, nome_arquivo: str) -> None:
    """Lê corretamente arquivos codificados em UTF-8 (1ª tentativa da cascata)."""
    arquivo: Path = tmp_path / nome_arquivo
    arquivo.write_text(data=conteudo, encoding="utf-8")

    assert LeitorLocal.ler_arquivo(caminho=arquivo) == conteudo


# ---------------------------------------------------------------------------
# 2ª tentativa: CP1252
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames=("conteudo", "nome_arquivo"),
    argvalues=[
        pytest.param(
            "Preço em Euro: €100 — citação com “aspas”",
            "cp1252-completo.txt",
            id="cp1252-euro-travessao-aspas",
        ),
        pytest.param(
            "Texto com aspas “curvas”",
            "aspas-curvas.txt",
            id="cp1252-aspas-curvas",
        ),
        pytest.param(
            "Período 2020–2024",
            "travessao.txt",
            id="cp1252-travessao",
        ),
    ],
)
def test_le_conteudo_cp1252(tmp_path: Path, conteudo: str, nome_arquivo: str) -> None:
    """Recorre ao CP1252 quando o conteúdo não é UTF-8 válido (2ª tentativa)."""
    arquivo: Path = tmp_path / nome_arquivo
    arquivo.write_bytes(data=conteudo.encode(encoding="cp1252"))

    assert LeitorLocal.ler_arquivo(caminho=arquivo) == conteudo


# ---------------------------------------------------------------------------
# 3ª tentativa: Latin-1 (bytes inválidos em CP1252)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames=("conteudo_bytes", "resultado_esperado"),
    argvalues=[
        pytest.param(
            b"Texto legado com byte: \x81",
            "Texto legado com byte: \x81",
            id="latin1-byte-81-invalido-em-cp1252",
        ),
        pytest.param(
            b"\x8d\x8e\x8f\x90",  # todos inválidos em CP1252, válidos em latin-1
            "\x8d\x8e\x8f\x90",
            id="latin1-bytes-de-controle",
        ),
        pytest.param(
            b"ASCII seguido de \xff",
            "ASCII seguido de \xff",
            id="latin1-byte-255",
        ),
    ],
)
def test_le_conteudo_latin1(tmp_path: Path, conteudo_bytes: bytes, resultado_esperado: str) -> None:
    """Usa latin-1 como último recurso quando o conteúdo é inválido em CP1252."""
    arquivo: Path = tmp_path / "legado.bin"
    arquivo.write_bytes(data=conteudo_bytes)

    assert LeitorLocal.ler_arquivo(caminho=arquivo) == resultado_esperado


# ---------------------------------------------------------------------------
# Garantia de projeto: latin-1 nunca falha, logo não existe 4º fallback
# ---------------------------------------------------------------------------
def test_latin1_decodifica_todos_os_256_valores_de_byte(tmp_path: Path) -> None:
    """Prova que a cascata termina em latin-1 sem precisar de ``errors='replace'``."""
    arquivo: Path = tmp_path / "todos_os_bytes.bin"
    arquivo.write_bytes(data=bytes(range(256)))

    conteudo: str = LeitorLocal.ler_arquivo(caminho=arquivo)

    assert len(conteudo) == 256


# ---------------------------------------------------------------------------
# Caminho inválido
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames="caminho_relativo",
    argvalues=[
        pytest.param("arquivo-inexistente.txt", id="arquivo-nao-existe"),
        pytest.param("diretorio-existente", id="caminho-e-diretorio"),
    ],
)
def test_lanca_filenotfounderror_para_caminho_invalido(
    tmp_path: Path, caminho_relativo: str
) -> None:
    """Levanta ``FileNotFoundError`` com mensagem clara para caminho ausente ou diretório."""
    caminho: Path = tmp_path / caminho_relativo
    if caminho_relativo == "diretorio-existente":
        caminho.mkdir()

    with pytest.raises(expected_exception=FileNotFoundError) as excecao:
        LeitorLocal.ler_arquivo(caminho)

    assert str(caminho) in str(excecao.value)
    assert "Arquivo não encontrado no disco" in str(excecao.value)


# ---------------------------------------------------------------------------
# Casos de borda
# ---------------------------------------------------------------------------
def test_arquivo_vazio_retorna_string_vazia(tmp_path: Path) -> None:
    """Devolve ``""`` para arquivo de zero bytes."""
    arquivo: Path = tmp_path / "vazio.html"
    arquivo.write_bytes(b"")

    assert LeitorLocal.ler_arquivo(caminho=arquivo) == ""


def test_bom_utf8_e_preservado_como_caractere(tmp_path: Path) -> None:
    """Documenta que 'utf-8' NÃO remove BOM — só 'utf-8-sig' faria isso."""
    arquivo: Path = tmp_path / "bom.html"
    arquivo.write_bytes(data=b"\xef\xbb\xbf<html/>")

    resultado: str = LeitorLocal.ler_arquivo(caminho=arquivo)
    assert resultado.startswith("\ufeff")
    assert resultado.endswith("<html/>")


# Indisponível pela lógica:
# def test_aceita_caminho_como_str(tmp_path: Path) -> None:
#     """Aceita ``str`` (não apenas ``Path``) no parâmetro ``caminho``."""
#     arquivo: Path = tmp_path / "a.html"
#     arquivo.write_bytes(b"<p>ok</p>")

#     assert LeitorLocal.ler_arquivo(caminho=str(arquivo)) == "<p>ok</p>"


# ---------------------------------------------------------------------------
# Contrato da classe
# ---------------------------------------------------------------------------
def test_metodo_e_estatico() -> None:
    """Confirma que ``ler_arquivo`` é um ``staticmethod``."""
    assert isinstance(LeitorLocal.__dict__["ler_arquivo"], staticmethod)


def test_pode_ser_chamado_via_instancia(tmp_path: Path) -> None:
    """Confirma que o método estático também funciona via instância."""
    arquivo: Path = tmp_path / "b.html"
    arquivo.write_bytes(b"y")

    assert LeitorLocal().ler_arquivo(caminho=arquivo) == "y"
