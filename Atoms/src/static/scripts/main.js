/**
 * main.js — Neutron Star frontend.
 *
 * Integra:
 *   - /api/sistema   → badges com SO, usuário e pasta home
 *   - /api/escanear  → lista + árvore dos HTMLs encontrados
 *   - /api/processar → conversão em lote via SSE (text/event-stream)
*
* Modo dev: se o backend não responder, carrega /static/mock.json e mantém
* a UI funcional para desenvolvimento visual.
 */

// sourcery skip: avoid-function-declarations-in-blocks
// ============================================================ Constantes
const MOCK_SISTEMA_URL = "/static/mock.json";

// ============================================================ Estado global
// Só o que precisa sobreviver entre carregamento de página.
let USE_MOCK = false;

// ============================================================ Helpers puros
// (não dependem de estado interno do DOMContentLoaded)

/** Hora atual no formato HH:MM:SS. */
function agora() {
    return new Date().toLocaleTimeString("pt-BR", { hour12: false });
}

/** Carrega o mock local quando o backend está indisponível. */
async function fetchMock() {
    const res = await fetch(MOCK_SISTEMA_URL, { cache: "no-store" });
    if (!res.ok) throw new Error("mock.json não encontrado em /static/");
    const m = await res.json();
    return {
        so: "Linux (mock)",
        usuario: "dev",
        pasta_home: "/home/usuario",
        atalhos_sugeridos: [
            { label: "Pasta Home (~/)", caminho: "~/" },
            { label: "Documentos",      caminho: "~/Documents" },
            { label: "Downloads",       caminho: "~/Downloads" },
        ],
        __mock_arquivos: m,
    };
}

/** Dispara download de um blob como arquivo. */
function baixarArquivo(nome, conteudo, mime) {
    const blob = new Blob([conteudo], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = nome;
    a.click();
    URL.revokeObjectURL(url);
}

/** Constrói recursivamente um nó <li> da árvore a partir do nó da API. */
function buildTreeNode(node) {
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.className = `tree__node tree__node--${node.type}`;
    span.textContent = (node.type === "folder" ? "📁 " : "📄 ") + node.name;
    li.appendChild(span);

    if (Array.isArray(node.children) && node.children.length) {
        const ul = document.createElement("ul");
        node.children.forEach(c => ul.appendChild(buildTreeNode(c)));
        li.appendChild(ul);
    }
    return li;
}

// ============================================================ App
document.addEventListener("DOMContentLoaded", function () {
    // ---------------------------------------------------------- Refs de UI
    const selectAtalhos           = document.getElementById("selectAtalhos");
    const selectExtensao          = document.getElementById("selectExtensao");
    const inputProfundidade       = document.getElementById("inputProfundidade");
    const toggleSubpastas         = document.getElementById("toggleSubpastas");
    const togglePrefixo           = document.getElementById("togglePrefixo");
    const inputPrefixo            = document.getElementById("inputPrefixo");
    const inputCaminho            = document.getElementById("inputCaminho");
    const btnEscanear             = document.getElementById("btnEscanear");
    const spinnerBusca            = document.getElementById("spinnerBusca");
    const txtBusca                = document.getElementById("txtBusca");

    const introWelcome            = document.getElementById("intro-welcome");
    const alertaErro              = document.getElementById("alerta-erro");
    const alertaErroTexto         = document.getElementById("alerta-erro-texto");

    const secaoResultados         = document.getElementById("secao-resultados");
    const treeContainer           = document.getElementById("tree");
    const metaTotalArquivos       = document.getElementById("meta-total-arquivos");
    const metaAposFiltros         = document.getElementById("meta-apos-filtros");
    const metaSelecionados        = document.getElementById("meta-selecionados");
    const metaTamanhoTotal        = document.getElementById("meta-tamanho-total");
    const infoDataBusca           = document.getElementById("info-data-busca");

    const tabelaArquivos          = document.getElementById("tabelaArquivos").querySelector("tbody");
    const checkboxSelecionarTodos = document.getElementById("checkboxSelecionarTodos");
    const filtrosChips            = document.getElementById("filtrosChips");

    const barraLote               = document.getElementById("barraLote");
    const labelSelecionados       = document.getElementById("label-selecionados");
    const labelCaminhoPai         = document.getElementById("label-caminho-pai");
    const btnConverter            = document.getElementById("btnConverter");
    const spinnerConversao        = document.getElementById("spinnerConversao");
    const txtConversao            = document.getElementById("txtConversao");

    const containerProgresso      = document.getElementById("container-progresso");
    const barraProgresso          = document.getElementById("barra-progresso");
    const textoPorcentagem        = document.getElementById("texto-porcentagem");
    const labelArquivoAtual       = document.getElementById("label-arquivo-atual");

    const logContainer            = document.getElementById("logContainer");
    const btnLimparLog            = document.getElementById("btnLimparLog");
    const btnExportarLog          = document.getElementById("btnExportarLog");
    const btnExportarMeta         = document.getElementById("btnExportarMeta");

    const modalResultados         = new bootstrap.Modal(document.getElementById("modalResultados"));
    const modalCorpoConteudo      = document.getElementById("modalCorpoConteudo");

    // ---------------------------------------------------------- Estado local
    let arquivosVarridos = [];
    let arvoreEstrutura  = [];
    let filtroAtivo      = "todos";
    let infoSistemaCache = null;
    const logsAcumulados = [];

    // ============================================================
    // Helpers que dependem do DOM
    // ============================================================

    function setBadge(html) {
        document.getElementById("info-sistema").innerHTML = html;
    }

    function mostrarErro(msg) {
        alertaErroTexto.textContent = msg;
        alertaErro.classList.remove("d-none");
    }

    function esconderErro() {
        alertaErro.classList.add("d-none");
    }

    function logar(nivel, msg) {
        const niveis = { INFO: "info", OK: "ok", WARN: "warn", ERROR: "error" };
        const cls = niveis[nivel] || "info";

        const line = document.createElement("div");
        line.className = "log__line";
        line.innerHTML = `
            <span class="log__time">${agora()}</span>
            <span class="log__level log__level--${cls}">${nivel}</span>
            <span class="log__msg">${msg}</span>
        `;
        logContainer.appendChild(line);
        logContainer.scrollTop = logContainer.scrollHeight;

        logsAcumulados.push({ time: agora(), nivel, msg });
    }

    // ============================================================
    // 1. Carregar dados do sistema (/api/sistema)
    // ============================================================
    async function carregarSistema() {
        let data;
        try {
            const res = await fetch("/api/sistema");
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            data = await res.json();
        } catch (e) {
            console.warn("Backend indisponível, caindo para mock:", e.message);
            USE_MOCK = true;
            data = await fetchMock();
        }
        infoSistemaCache = data;

        setBadge(`
            <span class="badge badge-system rounded-pill text-info me-2">
                <i class="bi bi-cpu me-1"></i> ${data.so || "SO desconhecido"}
            </span>
            <span class="badge badge-system rounded-pill text-success me-2">
                <i class="bi bi-person me-1"></i> ${data.usuario || "usuário"}
            </span>
            ${USE_MOCK ? '<span class="badge badge-system rounded-pill text-warning"><i class="bi bi-bug me-1"></i> MODO MOCK</span>' : ""}
        `);

        if (data.pasta_home) inputPrefixo.value = data.pasta_home + "/";

        selectAtalhos.innerHTML = "";
        (data.atalhos_sugeridos || []).forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.caminho;
            opt.textContent = item.label;
            selectAtalhos.appendChild(opt);
        });
    }

    // ============================================================
    // 2. Toggle prefixo ($HOME ↔ caminho absoluto)
    // ============================================================
    togglePrefixo.addEventListener("change", function () {
        const usarPrefixo = this.checked;
        inputPrefixo.disabled = !usarPrefixo;
        inputCaminho.disabled = false;   // sufixo sempre editável
        inputCaminho.placeholder = usarPrefixo
            ? "ex: Documents/bookmarks"
            : "/caminho/completo/absoluto";
        inputPrefixo.value = usarPrefixo
            ? ((infoSistemaCache?.pasta_home || "/home") + "/")
            : "";
        inputCaminho.focus();
    });

    // ============================================================
    // 3. Atalhos rápidos → input de caminho
    // ============================================================
    selectAtalhos.addEventListener("change", function () {
        const v = selectAtalhos.value;
        if (togglePrefixo.checked) {
            // "~/Documents" → "Documents" (o prefixo já cobre o HOME)
            inputCaminho.value = v.replace(/^~\//, "").replace(/^~$/, "");
        } else {
            inputCaminho.value = v;
        }
    });

    // ============================================================
    // 4. Profundidade → toggle automático de subpastas
    // ============================================================
    inputProfundidade.addEventListener("input", function () {
        const d = Number.parseInt(this.value, 10);
        if (!Number.isNaN(d)) toggleSubpastas.checked = d > 0;
    });

    // ============================================================
    // 5. Escanear pasta (/api/escanear)
    // ============================================================
    btnEscanear.addEventListener("click", async function () {
        let caminhoFinal = inputCaminho.value.trim();
        if (!caminhoFinal) { mostrarErro("Informe um caminho."); return; }

        if (togglePrefixo.checked) {
            caminhoFinal = inputPrefixo.value.replace(/\/$/, "") + "/" + caminhoFinal;
        }

        esconderErro();
        introWelcome.classList.add("d-none");
        spinnerBusca.classList.remove("d-none");
        btnEscanear.disabled = true;
        txtBusca.textContent = "Buscando...";
        logar("INFO", `Busca iniciada em <code>${caminhoFinal}</code>`);

        try {
            let data;
            if (USE_MOCK) {
                data = construirResultadoDoMock(caminhoFinal);
            } else {
                const params = new URLSearchParams({
                    caminho: caminhoFinal,
                    extensao: selectExtensao.value,
                    profundidade: inputProfundidade.value,
                });
                const res = await fetch(`/api/escanear?${params.toString()}`);
                data = await res.json();
                if (!res.ok) throw new Error(data.erro || "Erro inesperado.");
            }

            arquivosVarridos = data.arquivos || [];
            arvoreEstrutura  = data.tree || data.__mock_arquivos?.tree || [];
            exibirListaArquivos(data);
        } catch (err) {
            console.error(err);
            logar("ERROR", err.message);
            mostrarErro(err.message);
            secaoResultados.classList.add("d-none");
            barraLote.classList.add("d-none");
            introWelcome.classList.remove("d-none");
        } finally {
            spinnerBusca.classList.add("d-none");
            btnEscanear.disabled = false;
            txtBusca.innerHTML = '<i class="bi bi-search me-1"></i> Escanear';
        }
    });

    function construirResultadoDoMock(caminho) {
        const m = infoSistemaCache.__mock_arquivos;
        const arquivos = (m.files || []).map(f => ({
            nome: f.name,
            caminho_completo: `${caminho.replace(/\/$/, "")}/${f.location}${f.name}`,
            tamanho_kb: f.size_kb,
            modificado_em: "--/--/---- --:--:--",
            selecionado: false,
            // No mock, tratamos todos como elegíveis para a UI ser explorável
            elegivel: true,
        }));
        const total = arquivos.length;
        const totalBytes = arquivos.reduce((s, a) => s + a.tamanho_kb, 0);
        return {
            caminho_varrido: caminho,
            total_arquivos: total,
            total_elegiveis: total,
            tamanho_total_mb: Number.parseFloat((totalBytes / 1024).toFixed(2)),
            data_busca: new Date().toLocaleString("pt-BR"),
            arquivos,
            tree: m.tree || [],
            __mock_arquivos: m,
        };
    }

    // ============================================================
    // 6. Renderização (árvore + tabela)
    // ============================================================
    function exibirListaArquivos(data) {
        tabelaArquivos.innerHTML = "";
        infoDataBusca.textContent = `Buscado em: ${data.data_busca}`;

        if (!arquivosVarridos.length) {
            mostrarErro(`Nenhum arquivo encontrado em '${data.caminho_varrido}'.`);
            secaoResultados.classList.add("d-none");
            barraLote.classList.add("d-none");
            logar("WARN", "Nenhum arquivo qualificado.");
            return;
        }

        logar("INFO", `${data.total_arquivos} arquivo(s) encontrado(s) em ${data.caminho_varrido}`);
        if (typeof data.total_elegiveis === "number") {
            logar("INFO", `${data.total_elegiveis} de ${data.total_arquivos} arquivo(s) são elegíveis.`);
        }

        secaoResultados.classList.remove("d-none");
        barraLote.classList.remove("d-none");

        renderizarArvore(arvoreEstrutura);

        metaTotalArquivos.textContent = data.total_arquivos;
        metaTamanhoTotal.textContent  = `${data.tamanho_total_mb} MB`;
        labelCaminhoPai.innerHTML     =
            `<i class="bi bi-folder-symlink me-1"></i> Pasta: <strong class="text-white">${data.caminho_varrido}</strong>`;

        aplicarFiltro("todos");
        renderizarLinhas();
        sincronizarMasterCheckbox();
        atualizarContadores();

        // Metadados básicos
        const idCurto = data.data_busca.replace(/\D/g, "").slice(0, 10) || "—";
        document.getElementById("meta-id").textContent          = idCurto;
        document.getElementById("meta-origem").textContent      = data.caminho_varrido;
        document.getElementById("meta-destino").textContent     = data.caminho_varrido;
        document.getElementById("meta-entrada").textContent     = selectExtensao.value;
        document.getElementById("meta-saida").textContent       =
            document.querySelector('input[name="extensaoLote"]:checked')?.value.toUpperCase() || "—";
        document.getElementById("meta-encontrados").textContent = data.total_arquivos;
    }

    function renderizarArvore(tree) {
        treeContainer.innerHTML = "";
        if (!tree?.length) {
            treeContainer.innerHTML =
                '<p class="text-secondary p-3 mb-0" style="font-size:0.85rem;">Estrutura indisponível.</p>';
            return;
        }
        const root = document.createElement("ul");
        tree.forEach(n => root.appendChild(buildTreeNode(n)));
        treeContainer.appendChild(root);
    }

    function renderizarLinhas() {
        tabelaArquivos.innerHTML = "";
        const filtrados = arquivosVarridos.filter(estaVisivelNoFiltro);

        filtrados.forEach((arq) => {
            const idx = arquivosVarridos.indexOf(arq);
            const tr = document.createElement("tr");
            if (!arq.elegivel) tr.classList.add("row-nao-elegivel");

            const badge = arq.elegivel
                ? ""
                : '<span class="badge-nao-elegivel">não elegível</span>';

            tr.innerHTML = `
                <td class="text-center">
                    <input type="checkbox" class="form-check-input custom-checkbox-lg item-checkbox"
                           data-index="${idx}"
                           ${arq.selecionado ? "checked" : ""}
                           ${arq.elegivel ? "" : "disabled"}>
                </td>
                <td class="fw-bold text-white">${arq.nome}${badge}</td>
                <td class="text-secondary" style="font-size: 0.85rem;">${arq.caminho_completo}</td>
                <td class="text-info">${arq.tamanho_kb} KB</td>
                <td class="text-secondary" style="font-size: 0.85rem;">${arq.modificado_em}</td>
            `;
            tr.addEventListener("click", function (e) {
                if (e.target.type !== "checkbox" && arq.elegivel) {
                    const chk = tr.querySelector(".item-checkbox");
                    chk.checked = !chk.checked;
                    chk.dispatchEvent(new Event("change"));
                }
            });
            tabelaArquivos.appendChild(tr);
        });

        // Um único listener por checkbox (o bloco duplicado antigo foi removido)
        tabelaArquivos.querySelectorAll(".item-checkbox").forEach(chk => {
            chk.addEventListener("change", function () {
                const i = Number.parseInt(this.dataset.index, 10);
                arquivosVarridos[i].selecionado = this.checked;
                atualizarContadores();
                sincronizarMasterCheckbox();
            });
        });

        metaAposFiltros.textContent = filtrados.length;
    }

    function estaVisivelNoFiltro(arq) {
        if (filtroAtivo === "todos") return true;
        if (filtroAtivo === "elegiveis") return !!arq.elegivel;
        if (filtroAtivo === "nao-elegiveis") return !arq.elegivel;
        return true;
    }

    // ============================================================
    // 7. Filtros (chips)
    // ============================================================
    filtrosChips.addEventListener("click", function (e) {
        const btn = e.target.closest(".chip");
        if (!btn) return;

        filtrosChips.querySelectorAll(".chip").forEach(c => c.classList.remove("chip--active"));
        btn.classList.add("chip--active");

        aplicarFiltro(btn.dataset.filtro);
        renderizarLinhas();
        sincronizarMasterCheckbox();
    });

    function aplicarFiltro(f) { filtroAtivo = f; }

    // ============================================================
    // 8. Seleção em massa
    // ============================================================
    checkboxSelecionarTodos.addEventListener("change", function () {
        const { checked } = this;
        arquivosVarridos
            .filter(estaVisivelNoFiltro)
            .forEach(a => { if (a.elegivel) a.selecionado = checked; });
        renderizarLinhas();
        atualizarContadores();
        sincronizarMasterCheckbox();
    });

    function atualizarContadores() {
        const total = arquivosVarridos.filter(a => a.selecionado).length;
        metaSelecionados.textContent = total;
        document.getElementById("meta-sel").textContent = total;
        labelSelecionados.innerHTML =
            `<i class="bi bi-layers-half text-warning me-1"></i> Converter Lote: <strong class="text-info">${total} selecionados</strong>`;
        btnConverter.disabled = total === 0;
    }

    function sincronizarMasterCheckbox() {
        if (!checkboxSelecionarTodos) return;
        const visiveis = arquivosVarridos.filter(estaVisivelNoFiltro);
        checkboxSelecionarTodos.checked =
            visiveis.length > 0 && visiveis.every(a => a.selecionado);
        checkboxSelecionarTodos.indeterminate =
            visiveis.some(a => a.selecionado) && !visiveis.every(a => a.selecionado);
    }

    // ============================================================
    // 9. Processamento em lote (SSE)
    // ============================================================
    btnConverter.addEventListener("click", async function () {
        const selecionados = arquivosVarridos.filter(a => a.selecionado);
        if (!selecionados.length) return;

        const caminhos = selecionados.map(a => a.caminho_completo);
        const extensao = document.querySelector('input[name="extensaoLote"]:checked').value;

        containerProgresso.classList.remove("d-none");
        barraProgresso.style.width = "0%";
        textoPorcentagem.textContent = "0%";
        labelArquivoAtual.innerHTML = "Iniciando processamento...";
        spinnerConversao.classList.remove("d-none");
        btnConverter.disabled = true;
        txtConversao.textContent = "Iniciando...";
        logar("INFO", `Processando ${caminhos.length} arquivo(s) → ${extensao.toUpperCase()}`);

        if (USE_MOCK) {
            await simularProcessamento(caminhos, extensao);
            return;
        }

        try {
            const response = await fetch("/api/processar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    arquivos_selecionados: caminhos,
                    extensao_destino: extensao,
                }),
            });
            if (!response.ok || !response.body) {
                throw new Error("Erro de comunicação com o servidor.");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";
            let concluido = false;

            while (!concluido) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                const blocos = buffer.split("\n\n");
                buffer = blocos.pop();

                blocos.forEach(bloco => bloco.split("\n").forEach(linha => {
                    if (!linha.startsWith("data: ")) return;
                    const dados = JSON.parse(linha.replace("data: ", "").trim());
                    if (dados.erro) throw new Error(dados.erro);

                    barraProgresso.style.width = `${dados.progresso}%`;
                    textoPorcentagem.textContent = `${dados.progresso}%`;
                    labelArquivoAtual.innerHTML =
                        `<i class="bi bi-file-earmark-arrow-down text-info me-1"></i> Processando: <strong class="text-white">${dados.arquivo_atual}</strong>`;
                    logar("INFO", `Processando: <strong>${dados.arquivo_atual}</strong>`);

                    if (dados.concluido) {
                        concluido = true;
                        setTimeout(() => finalizarProcessamento(dados), 600);
                    }
                }));
            }
        } catch (err) {
            console.error("Erro crítico na conversão:", err);
            logar("ERROR", err.message);
            modalCorpoConteudo.innerHTML = `
                <div class="text-center py-3">
                    <span class="fs-1 text-danger">⚠️</span>
                    <h4 class="mt-2 fw-bold text-danger">Erro de Comunicação</h4>
                    <p class="text-secondary-emphasis">${err.message}</p>
                </div>`;
            modalResultados.show();
            containerProgresso.classList.add("d-none");
        } finally {
            spinnerConversao.classList.add("d-none");
            btnConverter.disabled = false;
            txtConversao.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Processar Lote';
        }
    });

    async function simularProcessamento(caminhos, extensao) {
        const total = caminhos.length;
        for (let i = 0; i < total; i++) {
            await new Promise(r => setTimeout(r, 400));
            const pct = Math.round(((i + 1) / total) * 100);
            barraProgresso.style.width = `${pct}%`;
            textoPorcentagem.textContent = `${pct}%`;

            const nome = caminhos[i].split("/").pop();
            labelArquivoAtual.innerHTML =
                `<i class="bi bi-file-earmark-arrow-down text-info me-1"></i> Processando: <strong class="text-white">${nome}</strong>`;
            logar("OK", `${nome} → ${nome.replace(/\.html?$/i, "")}.${extensao}`);
        }
        await new Promise(r => setTimeout(r, 300));
        finalizarProcessamento({
            sucesso: true,
            arquivos_convertidos: caminhos.map((c, i) => ({
                origem: c.split("/").pop(),
                destino: c.split("/").pop().replace(/\.html?$/i, "") + "." + extensao,
                // Valor determinístico — o mock não inventa dados reais
                total_links: 25 + (i * 17) % 60,
            })),
            erros: [],
        });
    }

    function finalizarProcessamento(dados) {
        containerProgresso.classList.add("d-none");
        renderizarModalResultados(dados);

        document.getElementById("meta-saida").textContent =
            document.querySelector('input[name="extensaoLote"]:checked')?.value.toUpperCase() || "—";

        if (dados.erros?.length) {
            dados.erros.forEach(e => logar("ERROR", `${e.arquivo}: ${e.erro}`));
        }
    }

    // ============================================================
    // 10. Modal de resultados
    // ============================================================
    function renderizarModalResultados(data) {
        let html = "";

        if (data.sucesso) {
            html += `
                <div class="text-center py-3">
                    <span class="fs-1 text-success">🎉</span>
                    <h4 class="mt-2 fw-bold text-success">Lote Processado com Sucesso!</h4>
                    <p class="text-secondary-emphasis">Os arquivos convertidos foram gravados na mesma pasta de origem dos HTMLs.</p>
                </div>
                <div class="mt-3">
                    <h6 class="fw-bold border-bottom border-secondary pb-2">
                        <i class="bi bi-files text-success me-1"></i> Arquivos Criados no Disco:
                    </h6>
                    <ul class="list-group list-group-flush bg-transparent">`;
            data.arquivos_convertidos.forEach(arq => {
                html += `
                    <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-0">
                        <div>
                            <span class="text-secondary">${arq.origem}</span>
                            <i class="bi bi-arrow-right mx-2 text-info"></i>
                            <strong class="text-success">${arq.destino}</strong>
                        </div>
                        <span class="badge bg-dark border border-success text-success">${arq.total_links} favoritos</span>
                    </li>`;
            });
            html += "</ul></div>";
        } else {
            html += `
                <div class="text-center py-3">
                    <span class="fs-1 text-danger">⚠️</span>
                    <h4 class="mt-2 fw-bold text-danger">O Lote não pôde ser Processado</h4>
                </div>`;
        }

        if (data.erros?.length) {
            html += `
                <div class="mt-4">
                    <h6 class="fw-bold text-danger border-bottom border-danger pb-2">
                        <i class="bi bi-x-circle me-1"></i> Problemas Identificados (${data.erros.length}):
                    </h6>
                    <div class="alert alert-danger py-2 bg-dark border-danger-subtle text-danger-emphasis">
                        <ul class="mb-0 ps-3">`;
            data.erros.forEach(err => {
                html += `<li>O arquivo <strong class="text-white">${err.arquivo}</strong> falhou: ${err.erro}</li>`;
            });
            html += "</ul></div></div>";
        }

        modalCorpoConteudo.innerHTML = html;
        modalResultados.show();
    }

    // ============================================================
    // 11. Log e metadados (exportação)
    // ============================================================
    btnLimparLog.addEventListener("click", () => {
        logContainer.innerHTML = "";
        logsAcumulados.length = 0;
    });

    btnExportarLog.addEventListener("click", () => {
        const texto = logsAcumulados
            .map(l => `[${l.time}] ${l.nivel} ${l.msg}`)
            .join("\n");
        baixarArquivo("neutron-star-log.txt", texto, "text/plain");
    });

    btnExportarMeta.addEventListener("click", () => {
        const meta = {
            sistema: infoSistemaCache,
            entrada: document.getElementById("meta-entrada").textContent,
            saida: document.getElementById("meta-saida").textContent,
            encontrados: document.getElementById("meta-encontrados").textContent,
            filtrados: document.getElementById("meta-filtrados").textContent,
            selecionados: document.getElementById("meta-sel").textContent,
            modo: USE_MOCK ? "mock" : "backend",
            timestamp: new Date().toISOString(),
        };
        baixarArquivo("neutron-star-meta.json", JSON.stringify(meta, null, 2), "application/json");
    });

    // ============================================================
    // Bootstrap
    // ============================================================
    carregarSistema();
});
