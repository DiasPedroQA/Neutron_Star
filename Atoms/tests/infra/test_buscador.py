# Atoms/tests/infra/test_buscador.py
# pylint: disable=protected-access

"""Testes unitários da varredura local (``src/infra/buscador.py``)."""

from pathlib import Path

import pytest

from src.infra.buscador import BuscadorLocal, GerenciadorSistemaLocal

CONTEUDO_NETSCAPE = "<DL><DT><A HREF='https://exemplo.com'>x</A></DL>"


def _nomes(resultado: dict) -> set[str]:
    """Extrai os nomes dos arquivos do resultado do escaneamento."""
    return {item["nome"] for item in resultado["arquivos"]}


@pytest.fixture
def buscador() -> BuscadorLocal:
    """Buscador com configuração padrão."""
    return BuscadorLocal()


# ===========================================================================
# validar_pasta
# ===========================================================================


def test_validar_pasta_existente_retorna_true(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Aceita um diretório existente."""
    assert buscador.validar_pasta(tmp_path) is True


def test_validar_pasta_inexistente_retorna_false(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Rejeita um diretório que não existe."""
    assert buscador.validar_pasta(tmp_path / "nao-existe") is False


def test_validar_pasta_com_byte_nulo_retorna_false_sem_excecao(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """Caminho irresolvível (byte nulo) deve ser rejeitado sem lançar exceção."""
    assert buscador.validar_pasta(Path(tmp_path, "arquivo\x00nulo.html")) is False


# ===========================================================================
# escanear
# ===========================================================================


def test_escanear_padrao_considera_apenas_html(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Extensão padrão é ``.html``: ``.htm`` e ``.txt`` ficam de fora."""
    (tmp_path / "favoritos.html").write_text("html", encoding="utf-8")
    (tmp_path / "outro.htm").write_text("html", encoding="utf-8")
    (tmp_path / "ignorado.txt").write_text("texto", encoding="utf-8")

    resultado = buscador.escanear(tmp_path)

    assert _nomes(resultado) == {"favoritos.html"}


def test_escanear_extensao_todos_inclui_html_e_htm_sem_diferenciar_caixa(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """``extensao='todos'`` cobre ``.html`` e ``.htm`` (também em maiúsculas)."""
    (tmp_path / "favoritos.html").write_text("html", encoding="utf-8")
    (tmp_path / "outro.HTM").write_text("html", encoding="utf-8")
    (tmp_path / "ignorado.txt").write_text("texto", encoding="utf-8")

    resultado = buscador.escanear(tmp_path, extensao="todos")

    assert _nomes(resultado) == {"favoritos.html", "outro.HTM"}
    assert resultado["total_arquivos"] == 2


def test_escanear_respeita_profundidade_maxima(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Não desce em subpastas além da profundidade informada."""
    pasta_profunda: Path = tmp_path / "nivel1" / "nivel2"
    pasta_profunda.mkdir(parents=True)
    (tmp_path / "raso.html").write_text("html", encoding="utf-8")
    (pasta_profunda / "profundo.html").write_text("html", encoding="utf-8")

    resultado = buscador.escanear(tmp_path, profundidade=1)

    assert _nomes(resultado) == {"raso.html"}


def test_escanear_ignora_arquivos_ocultos(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Arquivos iniciados por ponto não devem aparecer."""
    (tmp_path / ".oculto.html").write_text("html", encoding="utf-8")
    (tmp_path / "visivel.html").write_text("html", encoding="utf-8")

    assert _nomes(buscador.escanear(tmp_path)) == {"visivel.html"}


def test_escanear_ignora_diretorios_protegidos(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Pastas como ``.git`` não devem ser percorridas."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "interno.html").write_text("html", encoding="utf-8")
    (tmp_path / "normal.html").write_text("html", encoding="utf-8")

    assert _nomes(buscador.escanear(tmp_path)) == {"normal.html"}


def test_escanear_marca_elegibilidade_pelos_marcadores_netscape(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """Só HTML com ``<DL>``/``<DT>`` é elegível para conversão."""
    (tmp_path / "favoritos.html").write_text(CONTEUDO_NETSCAPE, encoding="utf-8")
    (tmp_path / "comum.html").write_text("<p>nada</p>", encoding="utf-8")

    resultado = buscador.escanear(tmp_path)
    elegibilidade: dict[str, bool] = {a["nome"]: a["elegivel"] for a in resultado["arquivos"]}

    assert elegibilidade == {"favoritos.html": True, "comum.html": False}


def test_escanear_pasta_inexistente_levanta_file_not_found(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """Pasta inexistente deve levantar ``FileNotFoundError``."""
    with pytest.raises(FileNotFoundError):
        buscador.escanear(tmp_path / "inexistente")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG confirmado: com mais arquivos que 'max_arquivos' na mesma pasta, o "
        "os.walk aborta ANTES de coletar qualquer um (retorna 0 em vez do limite)."
    ),
)
def test_escanear_com_limite_retorna_exatamente_o_limite(tmp_path: Path) -> None:
    """Ao exceder ``max_arquivos``, deve devolver os primeiros N (não zero)."""
    for indice in range(3):
        (tmp_path / f"f{indice}.html").write_text("html", encoding="utf-8")

    resultado = BuscadorLocal(max_arquivos=2).escanear(tmp_path)

    assert resultado["total_arquivos"] == 2


# ===========================================================================
# _obter_metadados
# ===========================================================================


def test_metadados_de_arquivo_inexistente_retornam_sentinela_none_zero(tmp_path: Path) -> None:
    """Contrato atual: arquivo ilegível devolve ``(None, 0)`` (nunca ``None`` puro)."""
    assert BuscadorLocal._obter_metadados(tmp_path / "inexistente.html") == (None, 0)


def test_metadados_contem_nome_tamanho_e_selecionado_falso(tmp_path: Path) -> None:
    """Metadados básicos; a seleção inicial é sempre ``False`` (decisão da UI)."""
    arquivo: Path = tmp_path / "favoritos.html"
    arquivo.write_text("1234", encoding="utf-8")

    metadados, tamanho_bytes = BuscadorLocal._obter_metadados(arquivo)

    assert metadados is not None
    assert metadados["nome"] == "favoritos.html"
    assert tamanho_bytes == 4
    assert metadados["tamanho_kb"] == 0.0
    assert metadados["selecionado"] is False


# ===========================================================================
# GerenciadorSistemaLocal
# ===========================================================================


def test_obter_informacoes_so_contem_campos_e_atalhos_fixos() -> None:
    """Retorna S.O., usuário, home e os atalhos fixos (``~/`` e ``editável``)."""
    dados = GerenciadorSistemaLocal().obter_informacoes_so()

    assert {"so", "usuario", "pasta_home", "atalhos_sugeridos"} <= dados.keys()
    assert dados["pasta_home"] == str(Path.home())
    caminhos: set[str] = {atalho["caminho"] for atalho in dados["atalhos_sugeridos"]}
    assert {"~/", "editável"} <= caminhos
