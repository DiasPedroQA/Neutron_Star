// Atoms/tests/frontend/test_render_sem_xss.js

// Regressão de segurança: nomes/caminhos de arquivo, vindos do disco ou da API,
// nunca podem ser interpretados como HTML ao serem exibidos (XSS armazenado).
//
// A prova é estrutural: o nó malicioso injetado não pode aparecer como ELEMENTO
// filho (ex.: um <img> de verdade), só como TEXTO literal.

import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import {
    renderizarLinha,
    renderizarItemConvertido,
    renderizarItemErro,
    criarLinhaDeLog,
} from "../../src/views/static/scripts/logica.js";

const PAYLOAD = '<img src=x onerror="window.__pwned = true">';

function montarDocumento() {
    return new JSDOM("<!DOCTYPE html><table><tbody id='corpo'></tbody></table>").window.document;
}

test("renderizarLinha: nome de arquivo malicioso vira texto, nunca elemento", () => {
    const documento = montarDocumento();
    const arq = {
        nome: PAYLOAD,
        caminho_completo: `/home/pedro/${PAYLOAD}`,
        tamanho_kb: 10,
        modificado_em: "01/01/2026 10:00:00",
        selecionado: false,
        elegivel: true,
    };

    const tr = renderizarLinha(documento, arq, 0);

    assert.equal(tr.querySelector("img"), null, "um <img> real não deve existir no DOM");
    assert.ok(
        tr.textContent.includes(PAYLOAD),
        "o payload deve aparecer como texto visível, não executado"
    );
});

test("renderizarLinha: nome de arquivo comum continua legível normalmente", () => {
    const documento = montarDocumento();
    const arq = {
        nome: "favoritos-trabalho.html",
        caminho_completo: "/home/pedro/Documents/favoritos-trabalho.html",
        tamanho_kb: 24,
        modificado_em: "01/01/2026 10:00:00",
        selecionado: false,
        elegivel: true,
    };

    const tr = renderizarLinha(documento, arq, 0);

    assert.ok(tr.textContent.includes("favoritos-trabalho.html"));
    assert.ok(tr.textContent.includes("/home/pedro/Documents/favoritos-trabalho.html"));
});

test("renderizarLinha: item não elegível fica desabilitado e recebe o badge visível", () => {
    const documento = montarDocumento();
    const arq = {
        nome: "arquivo.html",
        caminho_completo: "/home/pedro/arquivo.html",
        tamanho_kb: 5,
        modificado_em: "01/01/2026 10:00:00",
        selecionado: false,
        elegivel: false,
    };

    const tr = renderizarLinha(documento, arq, 0);

    assert.equal(tr.querySelector("input[type=checkbox]").disabled, true);
    assert.ok(tr.textContent.includes("não elegível"));
});

test("renderizarItemConvertido: origem/destino maliciosos viram texto, nunca elemento", () => {
    const documento = new JSDOM("<!DOCTYPE html><ul id='lista'></ul>").window.document;
    const arq = { origem: PAYLOAD, destino: `convertido${PAYLOAD}.json`, total_links: 7 };

    const li = renderizarItemConvertido(documento, arq);

    assert.equal(li.querySelector("img"), null);
    assert.ok(li.textContent.includes(PAYLOAD));
    assert.ok(li.textContent.includes("7 favoritos"));
});

test("renderizarItemErro: nome de arquivo malicioso no erro vira texto, nunca elemento", () => {
    const documento = new JSDOM("<!DOCTYPE html><ul id='lista'></ul>").window.document;
    const err = { arquivo: PAYLOAD, erro: "permissão negada" };

    const li = renderizarItemErro(documento, err);

    assert.equal(li.querySelector("img"), null);
    assert.ok(li.textContent.includes(PAYLOAD));
    assert.ok(li.textContent.includes("permissão negada"));
});

test("criarLinhaDeLog: nome de arquivo malicioso na mensagem vira texto, nunca elemento", () => {
    const documento = new JSDOM("<!DOCTYPE html><div id='log'></div>").window.document;

    const linha = criarLinhaDeLog(documento, "INFO", `Processando: ${PAYLOAD}`, "01/01/2026 10:00:00");

    assert.equal(linha.querySelector("img"), null);
    assert.ok(linha.textContent.includes(PAYLOAD));
    assert.ok(linha.textContent.includes("INFO"));
    assert.ok(linha.classList.contains("log__line--info"));
});

test("criarLinhaDeLog: nível desconhecido cai no estilo 'info' por padrão", () => {
    const documento = new JSDOM("<!DOCTYPE html><div id='log'></div>").window.document;

    const linha = criarLinhaDeLog(documento, "QUALQUER", "mensagem", "01/01/2026 10:00:00");

    assert.ok(linha.classList.contains("log__line--info"));
});
