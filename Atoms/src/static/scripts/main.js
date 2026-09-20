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
let USE_MOCK = false;

// ============================================================ Helpers puros
function agora() {
    return new Date().toLocaleTimeString("pt-BR", { hour12: false });
}

function agoraCompleto() {
    const d = new Date();
    const data = d.toLocaleDateString("pt-BR");
    const hora = d.toLocaleTimeString("pt-BR", { hour12: false });
    return `${data} ${hora}`;
}

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

function baixarArquivo(nome, conteudo, mime) {
    const blob = new Blob([conteudo], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = nome;
    a.click();
    URL.revokeObjectURL(url);
}

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
    const togglePrefixo         = document.getElementById("togglePrefixo");
    const painelPrefixo         = document.getElementById("painelPrefixo");
    const painelAbsoluto        = document.getElementById("painelAbsoluto");

    const selectAtalhos         = document.getElementById("selectAtalhos");
    const inputPrefixo          = document.getElementById("inputPrefixo");
    const inputCaminho          = document.getElementById("inputCaminho");
    const inputCaminhoAbsoluto  = document.getElementById("inputCaminhoAbsoluto");

    const selectExtensao        = document.getElementById("selectExtensao");
    const inputProfundidade     = document.getElementById("inputProfundidade");
    const toggleSubpastas       = document.getElementById("toggleSubpastas");

    const btnEscanear           = document.getElementById("btnEscanear");
    const spinnerBusca          = document.getElementById("spinnerBusca");
    const txtBusca              = document.getElementById("txtBusca");

    const introWelcome          = document.getElementById("intro-welcome");
    const alertaErro            = document.getElementById("alerta-erro");
    const alertaErroTexto       = document.getElementById("alerta-erro-texto");

    const secaoResultados       = document.getElementById("secao-resultados");
    const treeContainer         = document.getElementById("tree");
    const metaTotalArquivos     = document.getElementById("meta-total-arquivos");
    const metaAposFiltros       = document.getElementById("meta-apos-filtros");
    const metaSelecionados      = document.getElementById("meta-selecionados");
    const metaTamanhoTotal      = document.getElementById("meta-tamanho-total");
    const infoDataBusca         = document.getElementById("info-data-busca");

    const tabelaArquivos        = document.getElementById("tabelaArquivos").querySelector("tbody");
    const checkboxSelecionarTodos = document.getElementById("checkboxSelecionarTodos");
    const filtrosChips          = document.getElementById("filtrosChips");

    const logContainer          = document.getElementById("logContainer");
    const btnLimparLog          = document.getElementById("btnLimparLog");
    const btnExportarLog        = document.getElementById("btnExportarLog");
    const btnExportarMeta       = document.getElementById("btnExportarMeta");

    const destinoCustom         = document.getElementById("destinoCustom");
    const inputPastaSaida       = document.getElementById("inputPastaSaida");

    const btnConverter          = document.getElementById("btnConverter");
    const spinnerConversao      = document.getElementById("spinnerConversao");
    const txtConversao          = document.getElementById("txtConversao");
    const labelSelecionados     = document.getElementById("label-selecionados");

    const containerProgresso    = document.getElementById("container-progresso");
    const barraProgresso        = document.getElementById("barra-progresso");
    const textoPorcentagem      = document.getElementById("texto-porcentagem");
    const labelArquivoAtual     = document.getElementById("label-arquivo-atual");

    const modalResultados       = new bootstrap.Modal(document.getElementById("modalResultados"));
    const modalCorpoConteudo    = document.getElementById("modalCorpoConteudo");

    // ---------------------------------------------------------- Estado local
    let arquivosVarridos = [];
    let arvoreEstrutura  = [];
    let filtroAtivo      = "todos";
    let infoSistemaCache = null;
    let profundidadeMemoria = 5;
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
        line.className = `log__line log__line--${cls}`;
        line.innerHTML = `
            <span class="log__time">[${agoraCompleto()}]</span>
            <span class="log__level log__level--${cls}">${nivel}</span>
            <span class="log__msg">${msg}</span>
        `;
        logContainer.appendChild(line);
        logContainer.scrollTop = logContainer.scrollHeight;
        logsAcumulados.push({ time: agoraCompleto(), nivel, msg });
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
    // 2. Toggle de modo (prefixo ↔ absoluto)
    // ============================================================
    togglePrefixo.addEventListener("change", function () {
        const usarPrefixo = this.checked;
        painelPrefixo.classList.toggle("d-none", !usarPrefixo);
        painelAbsoluto.classList.toggle("d-none", usarPrefixo);

        inputPrefixo.value = usarPrefixo
            ? ((infoSistemaCache?.pasta_home || "/home") + "/")
            : "";

        // Foca o campo relevante do modo ativo
        if (usarPrefixo) {
            inputCaminho.focus();
        } else {
            inputCaminhoAbsoluto.focus();
        }
    });

    // ============================================================
    // 3. Atalhos rápidos → input
    // ============================================================
    selectAtalhos.addEventListener("change", function () {
        const v = selectAtalhos.value;
        // "~/Documents" → "Documents" (o prefixo já cobre a Home)
        inputCaminho.value = v.replace(/^~\//, "").replace(/^~$/, "");
    });

    // ============================================================
    // 4. Lock bidirecional Profundidade ↔ Subpastas
    // ============================================================
    toggleSubpastas.addEventListener("change", function () {
        if (this.checked) {
            inputProfundidade.disabled = false;
            inputProfundidade.value = profundidadeMemoria > 0 ? profundidadeMemoria : 5;
        } else {
            const atual = Number.parseInt(inputProfundidade.value, 10);
            if (atual > 0) profundidadeMemoria = atual;
            inputProfundidade.value = 0;
            inputProfundidade.disabled = true;
        }
    });

    inputProfundidade.addEventListener("input", function () {
        const d = Number.parseInt(this.value, 10);
        if (Number.isNaN(d)) return;

        if (d === 0) {
            toggleSubpastas.checked = false;
        } else {
            toggleSubpastas.checked = true;
            profundidadeMemoria = d;
        }
    });

    // ============================================================
    // 5. Escanear pasta
    // ============================================================
    btnEscanear.addEventListener("click", async function () {
        const caminhoFinal = montarCaminhoFinal();
        if (!caminhoFinal) {
            mostrarErro("Informe um caminho válido.");
            return;
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
            introWelcome.classList.remove("d-none");
        } finally {
            spinnerBusca.classList.add("d-none");
            btnEscanear.disabled = false;
            txtBusca.innerHTML = '<i class="bi bi-search me-1" aria-hidden="true"></i> Escanear';
        }
    });

    function montarCaminhoFinal() {
        if (togglePrefixo.checked) {
            const sufixo = inputCaminho.value.trim().replace(/^\/+/, "");
            if (!sufixo) return "";
            const prefixo = inputPrefixo.value.replace(/\/$/, "");
            return `${prefixo}/${sufixo}`;
        }
        return inputCaminhoAbsoluto.value.trim();
    }

    function construirResultadoDoMock(caminho) {
        const m = infoSistemaCache.__mock_arquivos;
        const arquivos = (m.files || []).map(f => ({
            nome: f.name,
            caminho_completo: `${caminho.replace(/\/$/, "")}/${f.location}${f.name}`,
            tamanho_kb: f.size_kb,
            modificado_em: "--/--/---- --:--:--",
            selecionado: false,
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
    // 6. Renderização
    // ============================================================
    function exibirListaArquivos(data) {
        tabelaArquivos.innerHTML = "";
        infoDataBusca.textContent = `Buscado em: ${data.data_busca}`;

        if (!arquivosVarridos.length) {
            mostrarErro(`Nenhum arquivo encontrado em '${data.caminho_varrido}'.`);
            secaoResultados.classList.add("d-none");
            logar("WARN", "Nenhum arquivo qualificado.");
            return;
        }

        logar("INFO", `${data.total_arquivos} arquivo(s) encontrado(s) em ${data.caminho_varrido}`);
        if (typeof data.total_elegiveis === "number") {
            logar("OK", `${data.total_elegiveis} de ${data.total_arquivos} arquivo(s) são elegíveis.`);
        }

        secaoResultados.classList.remove("d-none");

        renderizarArvore(arvoreEstrutura);

        metaTotalArquivos.textContent = data.total_arquivos;
        metaTamanhoTotal.textContent  = `${data.tamanho_total_mb} MB`;

        aplicarFiltro("todos");
        renderizarLinhas();
        sincronizarMasterCheckbox();
        atualizarContadores();

        // Metadados
        const idCurto = data.data_busca.replace(/\D/g, "").slice(0, 10) || "—";
        document.getElementById("meta-id").textContent          = idCurto;
        document.getElementById("meta-origem").textContent      = data.caminho_varrido;
        document.getElementById("meta-destino").textContent     = "Junto ao original";
        document.getElementById("meta-entrada").textContent     = selectExtensao.value;
        document.getElementById("meta-saida").textContent       =
            document.querySelector('input[name="extensaoLote"]:checked')?.value.toUpperCase() || "—";
        document.getElementById("meta-encontrados").textContent = data.total_arquivos;
    }

    function renderizarArvore(tree) {
        treeContainer.innerHTML = "";
        if (!tree?.length) {
            treeContainer.innerHTML =
                '<p class="text-secondary mb-0" style="font-size:0.85rem;">Estrutura indisponível.</p>';
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
    // 7. Filtros
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

        if (total === 0) {
            labelSelecionados.textContent = "Nenhum arquivo selecionado";
        } else {
            labelSelecionados.innerHTML =
                `<strong class="text-info">${total}</strong> arquivo(s) pronto(s) para processar`;
        }
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
    // 9. Pasta de saída — habilita/desabilita o input
    // ============================================================
    document.querySelectorAll('input[name="modoDestino"]').forEach(radio => {
        radio.addEventListener("change", () => {
            inputPastaSaida.disabled = !destinoCustom.checked;
            document.getElementById("meta-destino").textContent =
                destinoCustom.checked ? (inputPastaSaida.value || "—") : "Junto ao original";
            if (destinoCustom.checked) inputPastaSaida.focus();
        });
    });

    inputPastaSaida.addEventListener("input", () => {
        if (destinoCustom.checked) {
            document.getElementById("meta-destino").textContent = inputPastaSaida.value || "—";
        }
    });

    // ============================================================
    // 10. Processamento (SSE)
    // ============================================================
    btnConverter.addEventListener("click", async function () {
        const selecionados = arquivosVarridos.filter(a => a.selecionado);
        if (!selecionados.length) return;

        const caminhos = selecionados.map(a => a.caminho_completo);
        const extensao = document.querySelector('input[name="extensaoLote"]:checked').value;
        const usarPastaCustom = destinoCustom.checked;
        const pastaSaida = usarPastaCustom ? inputPastaSaida.value.trim() : null;

        if (usarPastaCustom && !pastaSaida) {
            mostrarErro("Informe uma pasta de saída ou volte para 'Junto ao original'.");
            return;
        }

        containerProgresso.classList.remove("d-none");
        barraProgresso.value = 0;
        textoPorcentagem.textContent = "0%";
        labelArquivoAtual.innerHTML = "Iniciando processamento...";
        spinnerConversao.classList.remove("d-none");
        btnConverter.disabled = true;
        txtConversao.textContent = "Iniciando...";
        logar("INFO", `Processando ${caminhos.length} arquivo(s) → ${extensao.toUpperCase()}`);
        if (pastaSaida) logar("INFO", `Pasta de saída: <code>${pastaSaida}</code>`);

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
                    pasta_saida: pastaSaida,
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

                    barraProgresso.value = dados.progresso;
                    textoPorcentagem.textContent = `${dados.progresso}%`;
                    labelArquivoAtual.innerHTML =
                        `<i class="bi bi-file-earmark-arrow-down text-info me-1" aria-hidden="true"></i> Processando: <strong class="text-white">${dados.arquivo_atual}</strong>`;
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
            txtConversao.innerHTML = '<i class="bi bi-arrow-repeat me-1" aria-hidden="true"></i> Processar Lote';
        }
    });

    async function simularProcessamento(caminhos, extensao) {
        const total = caminhos.length;
        for (let i = 0; i < total; i++) {
            await new Promise(r => setTimeout(r, 400));
            const pct = Math.round(((i + 1) / total) * 100);
            barraProgresso.value = pct;
            textoPorcentagem.textContent = `${pct}%`;

            const nome = caminhos[i].split("/").pop();
            labelArquivoAtual.innerHTML =
                `<i class="bi bi-file-earmark-arrow-down text-info me-1" aria-hidden="true"></i> Processando: <strong class="text-white">${nome}</strong>`;
            logar("OK", `${nome} → ${nome.replace(/\.html?$/i, "")}.${extensao}`);
        }
        await new Promise(r => setTimeout(r, 300));
        finalizarProcessamento({
            sucesso: true,
            arquivos_convertidos: caminhos.map((c, i) => ({
                origem: c.split("/").pop(),
                destino: c.split("/").pop().replace(/\.html?$/i, "") + "." + extensao,
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
    // 11. Modal de resultados
    // ============================================================
    function renderizarModalResultados(data) {
        let html = "";

        if (data.sucesso) {
            const destinoMsg = destinoCustom.checked
                ? `Os arquivos foram gravados em <code>${inputPastaSaida.value}</code>.`
                : "Os arquivos foram gravados na mesma pasta de origem dos HTMLs.";

            html += `
                <div class="text-center py-3">
                    <span class="fs-1 text-success">🎉</span>
                    <h4 class="mt-2 fw-bold text-success">Lote Processado com Sucesso!</h4>
                    <p class="text-secondary-emphasis">${destinoMsg}</p>
                </div>
                <div class="mt-3">
                    <h6 class="fw-bold border-bottom border-secondary pb-2">
                        <i class="bi bi-files text-success me-1" aria-hidden="true"></i> Arquivos Criados no Disco:
                    </h6>
                    <ul class="list-group list-group-flush bg-transparent">`;
            data.arquivos_convertidos.forEach(arq => {
                html += `
                    <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-0">
                        <div>
                            <span class="text-secondary">${arq.origem}</span>
                            <i class="bi bi-arrow-right mx-2 text-info" aria-hidden="true"></i>
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
                        <i class="bi bi-x-circle me-1" aria-hidden="true"></i> Problemas Identificados (${data.erros.length}):
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
    // 12. Log / metadados — limpar e exportar
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
            destino: document.getElementById("meta-destino").textContent,
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
