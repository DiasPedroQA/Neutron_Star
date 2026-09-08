document.addEventListener("DOMContentLoaded", function() {
    // Referências de UI
    const selectAtalhos = document.getElementById("selectAtalhos");
    const inputCaminho = document.getElementById("inputCaminho");
    const btnEscanear = document.getElementById("btnEscanear");
    const spinnerBusca = document.getElementById("spinnerBusca");
    const txtBusca = document.getElementById("txtBusca");

    const introWelcome = document.getElementById("intro-welcome");
    const alertaErro = document.getElementById("alerta-erro");
    const alertaErroTexto = document.getElementById("alerta-erro-texto");

    const secaoResultados = document.getElementById("secao-resultados");
    const metaTotalArquivos = document.getElementById("meta-total-arquivos");
    const metaSelecionados = document.getElementById("meta-selecionados");
    const metaTamanhoTotal = document.getElementById("meta-tamanho-total");
    const infoDataBusca = document.getElementById("info-data-busca");

    const tabelaArquivos = document.getElementById("tabelaArquivos").querySelector("tbody");
    const checkboxSelecionarTodos = document.getElementById("checkboxSelecionarTodos");

    const barraLote = document.getElementById("barraLote");
    const labelSelecionados = document.getElementById("label-selecionados");
    const labelCaminhoPai = document.getElementById("label-caminho-pai");
    const btnConverter = document.getElementById("btnConverter");
    const spinnerConversao = document.getElementById("spinnerConversao");
    const txtConversao = document.getElementById("txtConversao");

    // Elementos de Progresso SSE
    const containerProgresso = document.getElementById("container-progresso");
    const barraProgresso = document.getElementById("barra-progresso");
    const textoPorcentagem = document.getElementById("texto-porcentagem");
    const labelArquivoAtual = document.getElementById("label-arquivo-atual");

    const modalResultados = new bootstrap.Modal(document.getElementById("modalResultados"));
    const modalCorpoConteudo = document.getElementById("modalCorpoConteudo");

    let arquivosVarridos = [];

    // 1. Carrega dados do Sistema Operacional ao inicializar
    fetch("/api/sistema")
        .then(res => res.json())
        .then(data => {
            document.getElementById("info-sistema").innerHTML = `
                <span class="badge badge-system rounded-pill text-info me-2">
                    <i class="bi bi-cpu me-1"></i> ${data.so}
                </span>
                <span class="badge badge-system rounded-pill text-success me-2">
                    <i class="bi bi-person me-1"></i> ${data.usuario}
                </span>
                <span class="badge badge-system rounded-pill text-warning">
                    <i class="bi bi-layers me-1"></i> ${data.modo_arquitetura}
                </span>
            `;

            // Popula o seletor de Atalhos Rápidos
            selectAtalhos.innerHTML = "";
            data.atalhos_sugeridos.forEach(item => {
                const opt = document.createElement("option");
                opt.value = item.caminho;
                opt.textContent = item.label;
                selectAtalhos.appendChild(opt);
            });

            // Sincroniza o atalho carregado com o campo de texto
            inputCaminho.value = selectAtalhos.value;
        })
        .catch(err => {
            console.error("Erro ao carregar dados do S.O.:", err);
            selectAtalhos.innerHTML = '<option value="">Erro ao carregar...</option>';
        });

    // 2. Ouvinte do seletor de atalhos rápidos
    selectAtalhos.addEventListener("change", function() {
        if (selectAtalhos.value !== "custom") {
            inputCaminho.value = selectAtalhos.value;
        }
    });

    // 3. Ouvinte de Escaneamento de Diretório
    btnEscanear.addEventListener("click", async function() {
        const caminhoDigitado = inputCaminho.value.trim();
        if (!caminhoDigitado) return;

        // Reset de Estados de UI
        alertaErro.classList.add("d-none");
        introWelcome.classList.add("d-none");
        spinnerBusca.classList.remove("d-none");
        btnEscanear.disabled = true;
        txtBusca.textContent = "Buscando...";

        try {
            const res = await fetch(`/api/escanear?caminho=${encodeURIComponent(caminhoDigitado)}`);
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.erro || "Erro inesperado na busca.");
            }
            arquivosVarridos = data.arquivos || [];
            exibirListaArquivos(data);
        } catch (err) {
            console.error(err);
            mostrarErro(err.message);
            secaoResultados.classList.add("d-none");
            barraLote.classList.add("d-none");
            introWelcome.classList.remove("d-none");
        } finally {
            spinnerBusca.classList.add("d-none");
            btnEscanear.disabled = false;
            txtBusca.textContent = "Escanear Pasta";
        }
    });

// sourcery skip: avoid-function-declarations-in-blocks
    function mostrarErro(mensagem) {
        alertaErroTexto.textContent = mensagem;
        alertaErro.classList.remove("d-none");
    }

    // 4. Renderiza e gerencia a lista física dos arquivos encontrados
    function exibirListaArquivos(data) {
        tabelaArquivos.innerHTML = "";
        infoDataBusca.textContent = `Buscado em: ${data.data_busca}`;

        if (arquivosVarridos.length === 0) {
            mostrarErro(`Nenhum arquivo HTML de favoritos elegível foi encontrado em '${data.caminho_varrido}'.`);
            secaoResultados.classList.add("d-none");
            barraLote.classList.add("d-none");
            return;
        }

        secaoResultados.classList.remove("d-none");
        barraLote.classList.remove("d-none");

        // Preenche os contadores de cabeçalho
        metaTotalArquivos.textContent = data.total_arquivos;
        metaTamanhoTotal.textContent = `${data.tamanho_total_mb} MB`;
        labelCaminhoPai.innerHTML = `<i class="bi bi-folder-symlink me-1"></i> Pasta: <strong class="text-white">${data.caminho_varrido}</strong>`;

        arquivosVarridos.forEach((arq, index) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="text-center">
                    <input type="checkbox" class="form-check-input custom-checkbox-lg item-checkbox" data-index="${index}" ${arq.selecionado ? 'checked' : ''}>
                </td>
                <td class="fw-bold text-white">${arq.nome}</td>
                <td class="text-secondary" style="font-size: 0.85rem;">${arq.caminho_completo}</td>
                <td class="text-info">${arq.tamanho_kb} KB</td>
                <td class="text-secondary" style="font-size: 0.85rem;">${arq.modificado_em}</td>
            `;

            // Permite selecionar marcando a linha da tabela
            tr.addEventListener("click", function(e) {
                if (e.target.type !== 'checkbox') {
                    const chk = tr.querySelector(".item-checkbox");
                    chk.checked = !chk.checked;
                    chk.dispatchEvent(new Event('change'));
                }
            });

            tabelaArquivos.appendChild(tr);
        });

        // Vincula os listeners de mudanças nos checkboxes individuais
        document.querySelectorAll(".item-checkbox").forEach(chk => {
            chk.addEventListener("change", function() {
                const idx = Number.parseInt(this.dataset.index, 10);
                arquivosVarridos[idx].selecionado = this.checked;
                atualizarTextoContadores();
            });
        });

        checkboxSelecionarTodos.checked = true;
        atualizarTextoContadores();
    }

    // Ouvinte do checkbox master de seleção total
    checkboxSelecionarTodos.addEventListener("change", function() {
        const {checked} = this;
        document.querySelectorAll(".item-checkbox").forEach(chk => {
            chk.checked = checked;
            const idx = Number.parseInt(chk.dataset.index, 10);
            arquivosVarridos[idx].selecionado = checked;
        });
        atualizarTextoContadores();
    });

    function atualizarTextoContadores() {
        const totalSelecionados = arquivosVarridos.filter(a => a.selecionado).length;
        metaSelecionados.textContent = totalSelecionados;
        labelSelecionados.innerHTML = `<i class="bi bi-layers-half text-warning me-1"></i> Converter Lote: <strong class="text-info">${totalSelecionados} selecionados</strong>`;
        btnConverter.disabled = totalSelecionados === 0;
    }

    // 5. Motor de Processamento em Lote com Consumo de Streaming SSE em Tempo Real
    btnConverter.addEventListener("click", async function() {
        const selecionados = arquivosVarridos.filter(a => a.selecionado);
        if (selecionados.length === 0) return;

        const caminhos = selecionados.map(a => a.caminho_completo);
        const extensao = document.querySelector('input[name="extensaoLote"]:checked').value;

        // Reset e exibição da barra de progresso
        containerProgresso.classList.remove("d-none");
        barraProgresso.style.width = "0%";
        textoPorcentagem.textContent = "0%";
        labelArquivoAtual.innerHTML = "Iniciando processamento...";

        spinnerConversao.classList.remove("d-none");
        btnConverter.disabled = true;
        txtConversao.textContent = "Iniciando...";

        try {
            const response = await fetch("/api/processar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    arquivos_selecionados: caminhos,
                    extensao_destino: extensao
                })
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
                    labelArquivoAtual.innerHTML = `<i class="bi bi-file-earmark-arrow-down text-info me-1"></i> Processando: <strong class="text-white">${dados.arquivo_atual}</strong>`;
                    if (dados.concluido) {
                        concluido = true;
                        setTimeout(() => {
                            renderizarModalResultados(dados);
                            containerProgresso.classList.add("d-none");
                            btnEscanear.click();
                        }, 600);
                    }
                }));
            }
        } catch (err) {
            console.error("Erro crítico na conversão:", err);
            modalCorpoConteudo.innerHTML = `
                <div class="text-center py-3">
                    <span class="fs-1 text-danger">⚠️</span>
                    <h4 class="mt-2 fw-bold text-danger">Erro de Comunicação</h4>
                    <p class="text-secondary-emphasis">${err.message}</p>
                </div>
            `;
            modalResultados.show();
            containerProgresso.classList.add("d-none");
        } finally {
            spinnerConversao.classList.add("d-none");
            btnConverter.disabled = false;
            txtConversao.textContent = "Processar Lote";
        }
    });

    // 6. Construtor HTML Dinâmico para o Relatório Técnico de Resultados
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
                    <ul class="list-group list-group-flush bg-transparent">
            `;
            data.arquivos_convertidos.forEach(arq => {
                html += `
                    <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-0">
                        <div>
                            <span class="text-secondary">${arq.origem}</span>
                            <i class="bi bi-arrow-right mx-2 text-info"></i>
                            <strong class="text-success">${arq.destino}</strong>
                        </div>
                        <span class="badge bg-dark border border-success text-success">${arq.total_links} favoritos extraídos</span>
                    </li>
                `;
            });
            html += "</ul></div>";
        } else {
            html += `
                <div class="text-center py-3">
                    <span class="fs-1 text-danger">⚠️</span>
                    <h4 class="mt-2 fw-bold text-danger">O Lote não pôde ser Processado</h4>
                    <p class="text-secondary-emphasis">Verifique abaixo o detalhamento técnico dos problemas mapeados.</p>
                </div>
            `;
        }

        if (data.erros && data.erros.length > 0) {
            html += `
                <div class="mt-4">
                    <h6 class="fw-bold text-danger border-bottom border-danger pb-2">
                        <i class="bi bi-x-circle me-1"></i> Problemas Identificados (${data.erros.length}):
                    </h6>
                    <div class="alert alert-danger py-2 bg-dark border-danger-subtle text-danger-emphasis">
                        <ul class="mb-0 ps-3">
            `;
            data.erros.forEach(err => {
                html += `<li>O arquivo <strong class="text-white">${err.arquivo}</strong> falhou: ${err.erro}</li>`;
            });
            html += "</ul></div></div>";
        }

        modalCorpoConteudo.innerHTML = html;
        modalResultados.show();
    }
});
