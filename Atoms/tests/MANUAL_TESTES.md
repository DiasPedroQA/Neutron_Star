<!-- Atoms/tests/MANUAL_TESTES.md -->

# 🧪 Manual de Testes e Resiliência — App Neutron Star

Este documento consolida as especificações, cenários de validação e comportamentos de resiliência do **App Neutron Star**, servindo como guia de referência técnica para garantir que o sistema opere com altíssima confiabilidade sob qualquer condição de execução.

Com a migração para a **Arquitetura Hexagonal** de produção e a centralização do código na subpasta `Atoms/`, a suíte de testes foi totalmente reestruturada para rodar de forma isolada usando o interpretador oculto `.venv` e a biblioteca **`pytest`** com suporte a **`playwright`** para testes End-to-End.

---

## 🛠️ 1. Suíte de Testes Automatizados

A aplicação conta com uma bateria de testes automatizados cobrindo todas as camadas da arquitetura:

### 📋 Mapeamento de Testes

| Arquivo de Teste | Tipo de Teste | Camada Alvo | Foco do Teste |
| :--- | :--- | :--- | :--- |
| `Atoms/tests/dominio/` | **Unidade** | `dominio` | Entidades imutáveis (`Favorito`), regras de negócio e exceções semânticas. |
| `Atoms/tests/aplicacao/` | **Unidade** | `aplicacao` | Casos de uso, portas abstratas e barreira de segurança contra Path Traversal. |
| `Atoms/tests/infra/` | **Unidade** | `infra` | Leitor HTML com fallback de encodings, parser Netscape BeautifulSoup, buscador de disco e escritores CSV/JSON. |
| `Atoms/tests/adaptadores/` | **Integração** | `adaptadores` | Rotas HTTP do Flask, validações de schemas e streaming de eventos SSE em tempo real. |
| `Atoms/tests/e2e/` | **Ponta a Ponta** | SPA / Web | Testes E2E com Playwright headless simulando o ciclo completo do usuário no navegador. |

---

## 🚀 Como Executar os Testes

Você pode disparar as validações usando os atalhos centralizados do **Makefile** na raiz do projeto:

### Opção A: Executar Testes Unitários e de Integração (Recomendada)

```bash
make test
```

### Opção B: Executar Testes End-to-End (E2E)

```bash
make e2e
```

### Opção C: Executar a Esteira Completa de Validação (CI Gate)

```bash
make ci
```

---

## 🌪️ 2. Cenários de Validação Extrema e Resiliência Física

O motor do Neutron Star foi projetado seguindo princípios de tolerância a falhas e comportamento determinístico. O sistema lida graciosamente com os seguintes cenários adversos:

### 🌐 Cenário A: Dados Internacionais e Codificação Complexa

* **Ameaça:** Favoritos contendo emojis, termos acentuados em português, alfabeto cirílico ou caracteres asiáticos.
* **Comportamento do App:** O leitor HTML abre o arquivo usando UTF-8 e adota fallbacks dinâmicos em cascata (`latin-1` e `cp1252`) em caso de falha de decodificação. A camada de escrita persiste os favoritos com codificação **UTF-8 nativa** e desativa o escape de caracteres ASCII no JSON (`ensure_ascii=False`), mantendo acentuações e emojis (`🚀`) perfeitamente intactos.

### 🕳️ Cenário B: Árvores de Pastas Ultra Profundas (Recursão Segura)

* **Ameaça:** Favoritos aninhados em uma hierarquia extrema de subpastas (ex: 15 ou mais níveis).
* **Comportamento do App:** O parser recursivo BeautifulSoup percorre a árvore HTML acumulando as trilhas de nomes de pastas de forma linear e limpa, formatando o caminho consolidado como `Nível 1 / Nível 2 / Sublink` de forma segura, sem estourar limites de memória ou de recursão.

### 📄 Cenário C: HTMLs Incorretos, Sem Favoritos ou Vazios

* **Ameaça:** O usuário seleciona um arquivo HTML de uma página web comum (que não possui o formato padronizado de favoritos Netscape) ou um arquivo inteiramente vazio (`0 KB`).
* **Comportamento do App:** O parser detecta a ausência de tags `<DT>`, `<H3>` e `<A>` qualificadas de favoritos. Ao invés de quebrar o servidor Flask ou lançar erros de nulo, ele retorna um processamento de lote amigável com status de erro tratado, informando que o arquivo foi lido, mas continha 0 links de favoritos extraídos.

### 🛡️ Cenário D: Tentativas de Ataques de Segurança (Path Traversal)

* **Ameaça:** Um payload malicioso tenta ler caminhos de sistema fora do diretório de usuário permitido (ex: `~/../../etc/passwd` ou diretórios do sistema raiz `/`).
* **Comportamento do App:** A camada de casos de uso resolve o caminho real absoluto do diretório solicitado e o valida estritamente contra as pastas de usuário permitidas (`Path.home()`). Se uma infração for detectada, o sistema dispara a exceção de negócios `PathInseguroError`, que é capturada pela ponte da API e convertida instantaneamente em uma resposta HTTP segura **`403 Forbidden`**.

---

## 🔒 3. Cobertura da API Bridge (Teste de Integração de Rede)

O arquivo `test_api.py` garante que as rotas da API Flask respondam em total conformidade com o protocolo HTTP:

* **Validação de Metadados do S.O. (`/api/sistema`):** Garante retorno `200 OK` estruturado com o sistema operacional, usuário e atalhos rápidos do sistema hospedeiro.
* **Resiliência a Pastas Inexistentes (`/api/escanear`):** Garante retorno `404 Not Found` amigável ao tentar escanear diretórios fisicamente inexistentes na máquina.
* **Contrato de Streaming SSE (`/api/processar`):** Garante que o payload de conversão seja validado e inicie uma conexão com mimetype `text/event-stream`, emitindo chunks formatados contendo o progresso percentual acumulado em tempo real.
