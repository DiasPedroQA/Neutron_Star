# Atoms/tests/infra/test_buscador.py
# pylint: disable=protected-access, redefined-outer-name, missing-function-docstring

"""Testes unitários da varredura local (``src/infra/buscador.py``)."""

from pathlib import Path

import pytest

from src.dominio.entidades import InfoSistema, ResultadoEscaneamento
from src.infra.buscador import BuscadorLocal, GerenciadorSistemaLocal

CONTEUDO_NETSCAPE = "<DL><DT><A HREF='https://exemplo.com'>x</A></DL>"


def _nomes(resultado: ResultadoEscaneamento) -> set[str]:
    """Extrai os nomes dos arquivos do resultado do escaneamento."""
    return {item["nome"] for item in resultado["arquivos"]}


@pytest.fixture
def buscador() -> BuscadorLocal:
    """Buscador com configuração padrão."""
    return BuscadorLocal()


def test_validar_pasta_existente_retorna_true(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Valida se uma pasta existente é reconhecida com sucesso."""
    assert buscador.validar_pasta(caminho=tmp_path) is True


def test_validar_pasta_inexistente_retorna_false(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Valida se uma pasta inexistente é rejeitada."""
    assert buscador.validar_pasta(caminho=tmp_path / "nao-existe") is False


def test_validar_pasta_com_byte_nulo_retorna_false_sem_excecao(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """Valida se caminhos com caracteres inválidos são tratados sem crash."""
    assert buscador.validar_pasta(caminho=Path(tmp_path, "arquivo\x00nulo.html")) is False


def test_escanear_padrao_considera_apenas_html(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Valida filtro padrão para extensão .html."""
    (tmp_path / "favoritos.html").write_text("html", encoding="utf-8")
    (tmp_path / "outro.htm").write_text("html", encoding="utf-8")
    (tmp_path / "ignorado.txt").write_text("texto", encoding="utf-8")

    resultado: ResultadoEscaneamento = buscador.escanear(caminho=tmp_path)
    assert _nomes(resultado) == {"favoritos.html"}


def test_escanear_extensao_todos_inclui_html_e_htm_sem_diferenciar_caixa(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """Valida se a opção 'todos' captura .html e .htm indiferente a maiúsculas."""
    (tmp_path / "favoritos.html").write_text("html", encoding="utf-8")
    (tmp_path / "outro.HTM").write_text("html", encoding="utf-8")
    (tmp_path / "ignorado.txt").write_text("texto", encoding="utf-8")

    resultado: ResultadoEscaneamento = buscador.escanear(tmp_path, extensao="todos")
    assert _nomes(resultado) == {"favoritos.html", "outro.HTM"}
    assert resultado["total_arquivos"] == 2


def test_escanear_respeita_profundidade_maxima(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Valida se a profundidade máxima é respeitada na descida de subpastas."""
    pasta_profunda: Path = tmp_path / "nivel1" / "nivel2"
    pasta_profunda.mkdir(parents=True)
    (tmp_path / "raso.html").write_text("html", encoding="utf-8")
    (pasta_profunda / "profundo.html").write_text("html", encoding="utf-8")

    resultado: ResultadoEscaneamento = buscador.escanear(tmp_path, profundidade=1)
    assert _nomes(resultado) == {"raso.html"}


def test_escanear_ignora_arquivos_ocultos(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Valida se arquivos ocultos (.nomedoarquivo) são desconsiderados."""
    (tmp_path / ".oculto.html").write_text("html", encoding="utf-8")
    (tmp_path / "visivel.html").write_text("html", encoding="utf-8")

    assert _nomes(resultado=buscador.escanear(caminho=tmp_path)) == {"visivel.html"}


def test_escanear_ignora_diretorios_protegidos(buscador: BuscadorLocal, tmp_path: Path) -> None:
    """Valida se diretórios de controle de versão (.git) são ignorados."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "interno.html").write_text("html", encoding="utf-8")
    (tmp_path / "normal.html").write_text("html", encoding="utf-8")

    assert _nomes(buscador.escanear(tmp_path)) == {"normal.html"}


def test_escanear_marca_elegibilidade_pelos_marcadores_netscape(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """Valida a marcação de elegibilidade pelo padrão Netscape."""
    (tmp_path / "favoritos.html").write_text(CONTEUDO_NETSCAPE, encoding="utf-8")
    (tmp_path / "comum.html").write_text("<p>nada</p>", encoding="utf-8")

    resultado: ResultadoEscaneamento = buscador.escanear(tmp_path)
    elegibilidade: dict[str, bool] = {a["nome"]: a["elegivel"] for a in resultado["arquivos"]}

    assert elegibilidade == {"favoritos.html": True, "comum.html": False}


def test_escanear_pasta_inexistente_levanta_file_not_found(
    buscador: BuscadorLocal, tmp_path: Path
) -> None:
    """Valida se o erro de arquivo/pasta inexistente é disparado."""
    with pytest.raises(expected_exception=FileNotFoundError):
        buscador.escanear(tmp_path / "inexistente")


def test_metadados_de_arquivo_inexistente_retornam_sentinela_none_zero(tmp_path: Path) -> None:
    """Valida retorno sentinela (None, 0) para arquivo sem permissão ou inexistente."""
    assert BuscadorLocal._obter_metadados(tmp_path / "inexistente.html") == (None, 0)


def test_metadados_contem_nome_tamanho_e_selecionado_falso(tmp_path: Path) -> None:
    """Valida estrutura dos metadados extraídos de um arquivo válido."""
    arquivo: Path = tmp_path / "favoritos.html"
    arquivo.write_text("1234", encoding="utf-8")

    metadados, tamanho_bytes = BuscadorLocal._obter_metadados(arquivo)

    assert metadados is not None
    assert metadados["nome"] == "favoritos.html"
    assert tamanho_bytes == 4
    assert metadados["tamanho_kb"] == 0.0
    assert metadados["selecionado"] is False


def test_obter_informacoes_so_contem_campos_e_atalhos_fixos() -> None:
    """Valida coleta de dados ambientais do SO e atalhos de navegação."""
    dados: InfoSistema = GerenciadorSistemaLocal().obter_informacoes_so()

    assert {"so", "usuario", "pasta_home", "atalhos_sugeridos"} <= dados.keys()
    assert dados["pasta_home"] == str(Path.home())
    caminhos: set[str] = {atalho["caminho"] for atalho in dados["atalhos_sugeridos"]}
    assert {"~/", "editável"} <= caminhos
