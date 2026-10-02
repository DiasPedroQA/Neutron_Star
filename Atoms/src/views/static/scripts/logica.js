// Atoms/src/views/static/scripts/logica.js

/**
 * Funções puras e de renderização segura do frontend do Neutron Star.
 *
 * Isoladas de main.js para serem testáveis sem depender do evento
 * DOMContentLoaded nem de referências de elementos da página real.
 * As funções de renderização recebem `documento` (Document) como parâmetro
 * em vez de usar o `document` global, para funcionar tanto no navegador
 * quanto sob jsdom nos testes.
 */

/**
 * Monta o caminho final de varredura a partir do modo ativo (prefixo/Home ou absoluto).
 * @param {{usarPrefixo: boolean, prefixo: string, sufixo: string, caminhoAbsoluto: string}} args
 * @returns {string} Caminho pronto para a API, ou "" se inválido/incompleto.
 */
export function montarCaminhoFinal({ usarPrefixo, prefixo, sufixo, caminhoAbsoluto }) {
    if (usarPrefixo) {
        const sufixoLimpo = sufixo.trim().replace(/^\/+/, "");
        if (!sufixoLimpo) return "";
        const prefixoLimpo = prefixo.replace(/\/$/, "");
        return `${prefixoLimpo}/${sufixoLimpo}`;
    }
    return caminhoAbsoluto.trim();
}

/**
 * Decide se um arquivo varrido deve aparecer sob o filtro de chip ativo.
 * @param {{elegivel: boolean}} arquivo
 * @param {"todos"|"elegiveis"|"nao-elegiveis"} filtroAtivo
 */
export function estaVisivelNoFiltro(arquivo, filtroAtivo) {
    if (filtroAtivo === "elegiveis") return !!arquivo.elegivel;
    if (filtroAtivo === "nao-elegiveis") return !arquivo.elegivel;
    return true;
}

/**
 * Constrói, a partir do mock.json de desenvolvimento, o mesmo formato de
 * resposta que a API real devolveria para /api/escanear.
 * @param {string} caminho
 * @param {{files?: Array<{name: string, location: string, size_kb: number}>, tree?: unknown[]}} mock
 */
export function construirResultadoDoMock(caminho, mock) {
    const arquivos = (mock.files || []).map((f) => ({
        nome: f.name,
        caminho_completo: `${caminho.replace(/\/$/, "")}/${f.location}${f.name}`,
        tamanho_kb: f.size_kb,
        modificado_em: "--/--/---- --:--:--",
        selecionado: false,
        elegivel: true,
    }));
    const total = arquivos.length;
    const totalBytes = arquivos.reduce((soma, a) => soma + a.tamanho_kb, 0);
    return {
        caminho_varrido: caminho,
        total_arquivos: total,
        total_elegiveis: total,
        tamanho_total_mb: Number.parseFloat((totalBytes / 1024).toFixed(2)),
        data_busca: new Date().toLocaleString("pt-BR"),
        arquivos,
        tree: mock.tree || [],
        __mock_arquivos: mock,
    };
}

/**
 * Cria o <tr> de um arquivo varrido usando createElement/textContent — nunca
 * innerHTML — para que nome e caminho (que vêm do disco, fora do nosso controle)
 * jamais sejam interpretados como HTML. Regressão: ver test_render_sem_xss.js.
 * @param {Document} documento
 * @param {{nome: string, caminho_completo: string, tamanho_kb: number, modificado_em: string, selecionado: boolean, elegivel: boolean}} arq
 * @param {number} indice
 */
export function renderizarLinha(documento, arq, indice) {
    const tr = documento.createElement("tr");
    if (!arq.elegivel) tr.classList.add("row-nao-elegivel");

    const tdCheckbox = documento.createElement("td");
    tdCheckbox.className = "text-center";
    const checkbox = documento.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "form-check-input custom-checkbox-lg item-checkbox";
    checkbox.dataset.index = String(indice);
    checkbox.checked = !!arq.selecionado;
    checkbox.disabled = !arq.elegivel;
    tdCheckbox.appendChild(checkbox);

    const tdNome = documento.createElement("td");
    tdNome.className = "fw-bold text-white";
    tdNome.appendChild(documento.createTextNode(arq.nome));
    if (!arq.elegivel) {
        const badge = documento.createElement("span");
        badge.className = "badge-nao-elegivel";
        badge.textContent = "não elegível";
        tdNome.appendChild(badge);
    }

    const tdCaminho = documento.createElement("td");
    tdCaminho.className = "text-secondary";
    tdCaminho.style.fontSize = "0.85rem";
    tdCaminho.textContent = arq.caminho_completo;

    const tdTamanho = documento.createElement("td");
    tdTamanho.className = "text-info";
    tdTamanho.textContent = `${arq.tamanho_kb} KB`;

    const tdModificado = documento.createElement("td");
    tdModificado.className = "text-secondary";
    tdModificado.style.fontSize = "0.85rem";
    tdModificado.textContent = arq.modificado_em;

    tr.append(tdCheckbox, tdNome, tdCaminho, tdTamanho, tdModificado);
    return tr;
}

/**
 * Cria o <li> de um arquivo convertido com sucesso, para a lista do modal de
 * resultados. Mesma regra de segurança de `renderizarLinha`: nomes de origem/
 * destino vêm do disco e nunca podem virar HTML.
 * @param {Document} documento
 * @param {{origem: string, destino: string, total_links: number}} arq
 */
export function renderizarItemConvertido(documento, arq) {
    const li = documento.createElement("li");
    li.className =
        "list-group-item bg-transparent text-light border-secondary d-flex " +
        "justify-content-between align-items-center px-0";

    const div = documento.createElement("div");
    const spanOrigem = documento.createElement("span");
    spanOrigem.className = "text-secondary";
    spanOrigem.textContent = arq.origem;
    const seta = documento.createElement("i");
    seta.className = "bi bi-arrow-right mx-2 text-info";
    seta.setAttribute("aria-hidden", "true");
    const spanDestino = documento.createElement("strong");
    spanDestino.className = "text-success";
    spanDestino.textContent = arq.destino;
    div.append(spanOrigem, seta, spanDestino);

    const badge = documento.createElement("span");
    badge.className = "badge bg-dark border border-success text-success";
    badge.textContent = `${arq.total_links} favoritos`;

    li.append(div, badge);
    return li;
}

/**
 * Cria o <li> de um erro de conversão, para a lista de problemas do modal.
 * @param {Document} documento
 * @param {{arquivo: string, erro: string}} err
 */
export function renderizarItemErro(documento, err) {
    const li = documento.createElement("li");
    const forte = documento.createElement("strong");
    forte.className = "text-white";
    forte.textContent = err.arquivo;
    li.append("O arquivo ", forte, ` falhou: ${err.erro}`);
    return li;
}

const ESTILOS_NIVEL_LOG = new Set(["info", "ok", "warn", "error"]);

/**
 * Cria uma linha do painel de log. A mensagem é sempre texto puro: qualquer
 * dado de origem externa (nome de arquivo, caminho, erro do servidor) chega
 * aqui já formatado como string simples, nunca como HTML.
 * @param {Document} documento
 * @param {string} nivel "INFO" | "OK" | "WARN" | "ERROR" (case-insensitive)
 * @param {string} mensagem
 * @param {string} horario Já formatado (ex.: "28/09/2026 14:30:00")
 */
export function criarLinhaDeLog(documento, nivel, mensagem, horario) {
    const cls = ESTILOS_NIVEL_LOG.has(nivel.toLowerCase()) ? nivel.toLowerCase() : "info";

    const linha = documento.createElement("div");
    linha.className = `log__line log__line--${cls}`;

    const tempo = documento.createElement("span");
    tempo.className = "log__time";
    tempo.textContent = `[${horario}]`;

    const nivelSpan = documento.createElement("span");
    nivelSpan.className = `log__level log__level--${cls}`;
    nivelSpan.textContent = nivel;

    const msgSpan = documento.createElement("span");
    msgSpan.className = "log__msg";
    msgSpan.textContent = mensagem;

    linha.append(tempo, nivelSpan, msgSpan);
    return linha;
}
