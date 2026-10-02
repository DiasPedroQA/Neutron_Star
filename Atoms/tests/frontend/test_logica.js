// Atoms/tests/frontend/test_logica.js

// Testes das funções puras extraídas de main.js (sem dependência de DOM).

import { test } from "node:test";
import assert from "node:assert/strict";
import {
    montarCaminhoFinal,
    estaVisivelNoFiltro,
    construirResultadoDoMock,
} from "../../src/views/static/scripts/logica.js";

test("montarCaminhoFinal: modo prefixo junta prefixo e sufixo sem barra duplicada", () => {
    const resultado = montarCaminhoFinal({
        usarPrefixo: true,
        prefixo: "/home/pedro/",
        sufixo: "/Documents/bookmarks",
        caminhoAbsoluto: "",
    });

    assert.equal(resultado, "/home/pedro/Documents/bookmarks");
});

test("montarCaminhoFinal: modo prefixo com sufixo vazio retorna string vazia", () => {
    const resultado = montarCaminhoFinal({
        usarPrefixo: true,
        prefixo: "/home/pedro/",
        sufixo: "   ",
        caminhoAbsoluto: "",
    });

    assert.equal(resultado, "");
});

test("montarCaminhoFinal: modo absoluto ignora prefixo e usa o campo absoluto", () => {
    const resultado = montarCaminhoFinal({
        usarPrefixo: false,
        prefixo: "/home/pedro/",
        sufixo: "Documents",
        caminhoAbsoluto: "  /mnt/dados/backup  ",
    });

    assert.equal(resultado, "/mnt/dados/backup");
});

test("estaVisivelNoFiltro: filtro 'todos' aceita elegíveis e não elegíveis", () => {
    assert.equal(estaVisivelNoFiltro({ elegivel: true }, "todos"), true);
    assert.equal(estaVisivelNoFiltro({ elegivel: false }, "todos"), true);
});

test("estaVisivelNoFiltro: filtro 'elegiveis' aceita só elegíveis", () => {
    assert.equal(estaVisivelNoFiltro({ elegivel: true }, "elegiveis"), true);
    assert.equal(estaVisivelNoFiltro({ elegivel: false }, "elegiveis"), false);
});

test("estaVisivelNoFiltro: filtro 'nao-elegiveis' aceita só não elegíveis", () => {
    assert.equal(estaVisivelNoFiltro({ elegivel: false }, "nao-elegiveis"), true);
    assert.equal(estaVisivelNoFiltro({ elegivel: true }, "nao-elegiveis"), false);
});

test("construirResultadoDoMock: monta arquivos com caminho completo e soma tamanho em MB", () => {
    const mock = {
        files: [
            { name: "a.html", location: "sub/", size_kb: 512 },
            { name: "b.html", location: "", size_kb: 512 },
        ],
        tree: [{ type: "folder", name: "sub", children: [] }],
    };

    const resultado = construirResultadoDoMock("/home/pedro/Docs", mock);

    assert.equal(resultado.total_arquivos, 2);
    assert.equal(resultado.arquivos[0].caminho_completo, "/home/pedro/Docs/sub/a.html");
    assert.equal(resultado.arquivos[1].caminho_completo, "/home/pedro/Docs/b.html");
    assert.equal(resultado.tamanho_total_mb, 1);
    assert.deepEqual(resultado.tree, mock.tree);
});
