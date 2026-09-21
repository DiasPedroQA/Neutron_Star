# Atoms/tests/e2e/test_fluxo_conversao.py
# pylint: disable=import-error

"""Testes E2E: Varredura de pasta, seleção de arquivos e exportação em tempo real (SSE)."""

import re
import shutil
from pathlib import Path

import pytest

try:
    from playwright.sync_api import Locator, Page, expect
except ImportError:
    pytest.skip(reason="Playwright não instalado no ambiente", allow_module_level=True)

CONTEUDO_NETSCAPE_DEMO = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3>Trabalho</H3>
    <DL><p>
        <DT><A HREF="https://github.com">GitHub</A>
        <DT><A HREF="https://atlassian.com">Atlassian</A>
    </DL><p>
</DL><p>
"""


# =============================================================================
# Mini-funções auxiliares (Passos do Fluxo E2E)
# =============================================================================


def _configurar_pasta_teste(nome_pasta: str = "_e2e_teste_neutron") -> tuple[Path, Path]:
    """Cria pasta temporária de teste dentro de ~/ com um arquivo de bookmarks válido."""
    pasta: Path = Path.home() / nome_pasta
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo: Path = pasta / "meus_bookmarks.html"
    arquivo.write_text(data=CONTEUDO_NETSCAPE_DEMO, encoding="utf-8")
    return pasta, arquivo


def _executar_busca_na_ui(page: Page, nome_subpasta: str) -> None:
    """Preenche a subpasta na interface e dispara o escaneamento."""
    input_subpasta: Locator = page.locator(
        selector="input[placeholder*='Documents'], input[name='subpasta'], #input-subpasta"
    ).first
    input_subpasta.fill(value=nome_subpasta)

    btn_escanear: Locator = page.locator(selector="button:has-text('Escanear')")
    btn_escanear.click()


def _selecionar_arquivo_e_processar(page: Page, nome_arquivo: str) -> None:
    """Aguarda o arquivo na tabela, marca a seleção e clica em Processar Lote."""
    # 1. Aguarda aparição do arquivo na tela
    item: Locator = page.get_by_text(nome_arquivo).first
    expect(item).to_be_visible(timeout=5000)

    # 2. Marca o checkbox de seleção do arquivo (habilita o botão Processar)
    checkbox: Locator = page.locator(
        selector="input[type='checkbox']#chkSelectAll, tbody input[type='checkbox']"
    ).first
    if not checkbox.is_checked():
        checkbox.check()

    # 3. Dispara a conversão agora que o botão está habilitado
    btn_processar: Locator = page.locator(
        selector="button:has-text('Processar Lote'), #btnConverter"
    )
    expect(btn_processar).to_be_enabled(timeout=5000)
    btn_processar.click()


def _validar_sucesso_conversao(page: Page, arquivo_esperado: Path) -> None:
    """Valida o modal de sucesso na UI e a criação física do arquivo no disco."""
    sucesso_modal: Locator = page.get_by_text(text="Lote Processado com Sucesso!")
    expect(sucesso_modal).to_be_visible(timeout=8000)
    assert arquivo_esperado.exists()


# =============================================================================
# Caso de Teste E2E Principal (Orquestrador Limpo)
# =============================================================================


@pytest.mark.e2e
def test_fluxo_completo_varredura_e_conversao(page: Page, live_server_url: str) -> None:
    """Valida o fluxo completo: Varredura -> Seleção -> Conversão SSE -> Sucesso."""
    pasta_teste, arquivo_bookmarks = _configurar_pasta_teste()
    arquivo_esperado: Path = pasta_teste / "meus_bookmarks_processado.csv"

    try:
        page.goto(url=live_server_url)
        expect(page).to_have_title(title_or_reg_exp=re.compile(pattern=r"Neutron Star"))

        _executar_busca_na_ui(page=page, nome_subpasta=pasta_teste.name)
        _selecionar_arquivo_e_processar(page=page, nome_arquivo=arquivo_bookmarks.name)
        _validar_sucesso_conversao(page=page, arquivo_esperado=arquivo_esperado)

    finally:
        if pasta_teste.exists():
            shutil.rmtree(pasta_teste, ignore_errors=True)
