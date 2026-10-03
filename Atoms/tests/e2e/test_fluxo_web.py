"""Fluxo ponta a ponta da interface web com conversão real de favoritos Netscape."""

import json
from pathlib import Path

import pytest
from playwright.sync_api import Page, Route, expect

CSS_TESTE: str = """
.d-none { display: none !important; }
.modal:not(.show) { display: none; }
.modal.show { display: block; }
"""

JS_BOOTSTRAP_TESTE: str = """
window.bootstrap = {
  Modal: class {
    constructor(element) { this.element = element; }
    show() {
      this.element.classList.add("show");
      this.element.style.display = "block";
      this.element.setAttribute("aria-hidden", "false");
    }
  }
};
"""


@pytest.mark.e2e
def test_interface_escanear_selecionar_e_converter_arquivo(
    page: Page,
    servidor_local: str,
    home_e2e: Path,
) -> None:
    """Processa um HTML real pela interface e confirma o arquivo JSON gerado."""
    origem: Path = home_e2e / "favoritos.html"
    origem.write_text(
        """<!DOCTYPE NETSCAPE-Bookmark-file-1>
        <DL><p>
          <DT><A HREF="https://exemplo.com" ADD_DATE="1710001000">Portal de teste</A>
        </DL><p>
        """,
        encoding="utf-8",
    )

    def responder_cdn(rota: Route) -> None:
        """Bloqueia recursos CDN, que dependem de rede externa e SRI."""
        rota.fulfill(body="")

    page.add_init_script(JS_BOOTSTRAP_TESTE)
    page.route("https://cdn.jsdelivr.net/**", responder_cdn)
    page.goto(servidor_local)
    page.add_style_tag(content=CSS_TESTE)

    page.locator("#togglePrefixo").uncheck()
    page.locator("#inputCaminhoAbsoluto").fill(str(home_e2e))
    page.locator("#btnEscanear").click()

    caixa_arquivo = page.locator(".item-checkbox")
    expect(caixa_arquivo).to_be_visible()
    expect(caixa_arquivo).to_be_enabled()
    caixa_arquivo.check()
    expect(page.locator("#meta-selecionados")).to_have_text("1")

    page.locator("#radioJSON").check()
    page.locator("#btnConverter").click()
    expect(page.get_by_text("Lote Processado com Sucesso!")).to_be_visible(timeout=10_000)

    destino: Path = home_e2e / "favoritos_processado.json"
    assert destino.is_file()
    favoritos: list[dict[str, str]] = json.loads(destino.read_text(encoding="utf-8"))
    assert favoritos[0]["titulo"] == "Portal de teste"
    assert favoritos[0]["url"] == "https://exemplo.com"
