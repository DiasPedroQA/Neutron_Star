# Neutron Star Atoms

O **Neutron Star Atoms** é o núcleo de processamento do ecossistema Neutron Star. Ele foi totalmente reestruturado sob os rígidos princípios da **Arquitetura Hexagonal (Portas e Adaptadores)**, utilizando **Flask** para a camada de controle de rede, validações robustas de payloads de entrada sem dependências pesadas externas e transmissão reativa de progresso de processamento em tempo real por meio do protocolo de streaming **Server-Sent Events (SSE)**.

A aplicação opera sobre caminhos disponíveis no mesmo sistema de arquivos do servidor, com barreiras de segurança física ativas.

---

## 🌌 Arquitetura do Núcleo (`Atoms/`)

Para garantir flexibilidade de componentes e isolamento absoluto das regras de negócio, o código-fonte dentro de `Atoms/src/` é dividido em quatro camadas estritas:

1. **`dominio` (Núcleo Puro):** Define as entidades de dados imutáveis (`Favorito`) e as exceções de negócios corporativas, 100% livres de dependências de frameworks.
2. **`aplicacao` (Casos de Uso e Portas):** Orquestra os fluxos da aplicação (varredura de diretórios, coleta ambiental e processador de lotes por streaming). Define as interfaces abstratas (Portas de Entrada/Saída) que devem ser implementadas pelos adaptadores externos.
3. **`infra` (Adaptadores de Saída):** Implementa os acessos físicos e de baixo nível ao sistema operacional: varreduras eficientes de diretórios, abertura resiliente de codificações de texto (HTML de bookmarks) e escritores sob o padrão *Strategy* para as saídas CSV e JSON.
4. **`adaptadores` (Adaptadores de Entrada):** Expõe as portas de entrada da aplicação. Contém os validadores de contratos (`schemas.py`) e os controladores de rotas HTTP do Flask (`api.py`).

---

## ⚡ Recursos Principais

- **Varredura Inteligente e Segura:** Localiza e detalha metadados de arquivos HTML de favoritos no disco rígido do servidor.
- **Parser BeautifulSoup Altamente Resiliente:** Extrai de forma recursiva toda a estrutura de pastas do padrão Netscape Bookmarks, preservando hierarquias em múltiplos níveis, datas originais de adição e URLs válidas.
- **Mapeador de Saídas Customizáveis:** Converte a árvore de favoritos para JSON estruturado ou CSV com codificação UTF-8 com sinalizador de byte de ordem (BOM) e separadores de ponto e vírgula `;` (otimizado para abertura direta no Microsoft Excel brasileiro).
- **Streaming de Progresso Real (SSE):** Comunicação de via única em tempo real que atualiza a porcentagem e o arquivo sendo processado no exato milissegundo em que a conversão ocorre.
- **Proteção Ativa contra Invasão de Caminhos:** Filtro dinâmico na raiz dos casos de uso contra ataques de *Path Traversal* (bloqueia caminhos fora do diretório HOME do usuário).

---

## 🚀 Executar Localmente

Como as dependências do projeto e o interpretador virtual oculto **`.venv`** ficam localizados na raiz do repositório, execute a aplicação a partir de lá utilizando os atalhos de automação:

```bash
# Navegue até a raiz do repositório
cd /home/diaspedro/Desktop/PyProject/Neutron_Star/

# Configura o .venv e instala todos os pacotes necessários
make setup

# Levanta o servidor Flask com depurador ativo na porta 5000
make run
```

Se preferir rodar manualmente com o seu `.venv` ativo:

```bash
# Ative o .venv na raiz
source .venv/bin/activate

# Entre na pasta Atoms e inicialize o servidor
cd Atoms
export FLASK_DEBUG=1
python3 main.py
```

O painel interativo e a API estarão disponíveis localmente em: **`http://127.0.0.1:5000`**

---

## 📡 Endpoints da API

Todas as comunicações com o backend utilizam o prefixo de rota modular `/api`.

| Método | Rota | Protocolo / Tipo | Finalidade |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `text/html` | Entrega a Single Page Application (SPA) reativa tema *Obsidian*. |
| `GET` | `/api/sistema` | `application/json` | Coleta metadados do sistema operacional hospedeiro e atalhos rápidos. |
| `GET` | `/api/escanear` | `application/json` | Varre de forma rápida caminhos do sistema em busca de HTMLs de favoritos. |
| `POST` | `/api/processar` | `text/event-stream` | Executa a conversão do lote transmitindo o progresso em tempo real (SSE). |

### Exemplo de Requisição de Conversão (Lote por SSE)

```bash
curl -X POST http://127.0.0.1:5000/api/processar \
  -H 'Content-Type: application/json' \
  -d '{
    "arquivos_selecionados": [
      "/home/diaspedro/Documentos/bookmarks_chrome.html",
      "/home/diaspedro/Downloads/favoritos_backup.html"
    ],
    "extensao_destino": "csv"
  }'
```

**Exemplo de Stream de Eventos Recebidos no Terminal:**

```text
data: {"progresso": 50, "arquivo_atual": "bookmarks_chrome.html", "concluido": false}

data: {"progresso": 100, "arquivo_atual": "favoritos_backup.html", "concluido": true, "sucesso": true, "arquivos_convertidos": [...]}
```

---

## 🔒 Segurança

Por motivos de segurança cibernética e privacidade de dados, este aplicativo **nunca deve ser exposto diretamente na internet sem autenticação prévia**.
O backend possui validações profundas:

- **`PathInseguroError` (Retorna 403 Forbidden):** Disparado se o usuário tentar passar caminhos como `../../etc/passwd` ou diretórios fora do diretório home do usuário.
- **`DiretorioInexistenteError` (Retorna 404 Not Found):** Disparado se o diretório requisitado na busca não puder ser fisicamente resolvido pelo sistema de arquivos.

---

## 🧪 Execução de Testes Unitários e de Integração

O ecossistema é validado usando a suíte nativa `unittest` do Python para garantir regressão zero. Os testes cobrem desde validações isoladas do extrator BeautifulSoup até simulações de fluxo de rede HTTP completo no Flask.

Para executar os testes, utilize o atalho do Makefile a partir da raiz do projeto:

```bash
# Executa todos os testes
make test
```

Se preferir rodar de dentro da pasta `Atoms/`:

```bash
cd Atoms/
python3 -m unittest discover -s tests
```
