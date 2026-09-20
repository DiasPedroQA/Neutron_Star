# Neutron Star

Projeto robusto para localizar arquivos HTML de favoritos (bookmarks no formato clássico Netscape), extrair seus links e convertê-los de forma inteligente para os formatos CSV (compatível com Microsoft Excel brasileiro) ou JSON, utilizando **Arquitetura Hexagonal (Portas e Adaptadores)** e uma interface web reativa em tempo real.

O núcleo técnico e o código-fonte da aplicação estão isolados na subpasta [`Atoms/`](Atoms/README.md). Consulte esse subdiretório para detalhes internos de implementação técnica e fluxos das camadas.

---

## 🚀 Recursos Principais

- **Arquitetura Hexagonal:** Desacoplamento absoluto entre as regras de negócio de domínio e as tecnologias de entrega (Flask, BeautifulSoup, etc.).
- **Varredura e Escaneamento Rápido:** Busca recursiva otimizada na Home (`~/`) do usuário em busca de arquivos HTML elegíveis de favoritos.
- **Streaming de Progresso Real (SSE):** Monitoramento visual do progresso de conversão de lote milissegundo a milissegundo através de Server-Sent Events no Flask.
- **Segurança Corporativa Ativa:** Tratamento de segurança que impede vulnerabilidades de *Path Traversal*, forçando caminhos seguros e válidos dentro do escopo da Home do usuário.
- **Interface Deep Space Obsidian:** Visual de alto padrão com efeitos de morfismo de vidro fosco (*glassmorphism*), feedback físico de linhas de tabela e barras de progresso dinâmicas.

---

## 📂 Estrutura de Pastas do Repositório

```text
Neutron_Star/
├── .venv/                      # Ambiente virtual oculto do Python (isolado na raiz)
├── Atoms/                      # Código-fonte centralizado da aplicação
│   ├── src/                    # Camadas de Domínio, Aplicação, Infra e Adaptadores
│   │   ├── adaptadores/        # Roteadores HTTP Flask e validação de schemas
│   │   ├── aplicacao/          # Casos de uso e portas de entrada/saída (interfaces)
│   │   ├── dominio/            # Entidades imutáveis e exceções de negócio
│   │   ├── infra/              # Parsers BeautifulSoup, buscadores e escritores CSV/JSON
│   │   ├── montagem/           # Composition Root (Injeção de dependências global)
│   │   └── templates/          # Interface do Usuário (index.html SPA)
│   ├── tests/                  # Suíte de testes unitários e de integração
│   ├── main.py                 # Ponto de partida (Entrypoint) do servidor Flask
│   ├── pyproject.toml          # Configurações do ambiente, linters (Ruff, Pylint, Mypy)
│   └── requirements.txt        # Dependências de execução (Flask, BeautifulSoup4, Flask-WTF)
├── Dockerfile                  # Instruções de build e containerização otimizada
├── docker-compose.yml          # Orquestração local com mapeamento de volumes seguro
├── Makefile                    # Atalhos e automação de comandos de desenvolvimento
├── MANUAL_TESTES.md            # Guia completo de cobertura e execução de testes
├── run_app.sh                  # Script de execução rápida para Linux (1 clique)
└── run_app.bat                 # Script de execução rápida para Windows (1 clique)
```

---

## 🛠️ Desenvolvimento e Execução Rápida

O projeto fornece um **`Makefile`** na raiz para automatizar todo o ciclo de vida do ambiente local usando o interpretador do seu ambiente virtual oculto `.venv`:

### 1. Provisionar o Ambiente (.venv + Dependências)

Cria o ambiente virtual isolado na raiz do projeto e instala todas as dependências necessárias com um único comando:

```bash
make setup
```

### 2. Rodar o Servidor Localmente

Inicia a aplicação Flask em modo de desenvolvimento com hot-reload habilitado em `http://127.0.0.1:5000`:

```bash
make run
```

*(Alternativamente, você também pode usar o executável rápido `./run_app.sh` no seu Linux ou `run_app.bat` no Windows).*

### 3. Rodar a Suíte de Testes Completa

Executa todos os testes unitários (do parser e dos escritores locais) e de integração (testes de chamadas de rotas Flask, barreiras de segurança e streams):

```bash
make tests
```

### 4. Validação Geral e Linters (CI Gate)

Executa a esteira completa de validação estática de tipos, formatação e qualidade de código exigidas no CI/CD (Ruff + Pylint + Mypy + Testes):

```bash
make check
```

---

## 🐳 Execução via Docker Compose

Caso prefira isolar 100% da execução em containers Docker (evitando instalar dependências locais na sua máquina física):

```bash
# Executa o build da imagem Docker otimizada
make docker-build

# Sobe o container em segundo plano
make docker-up
```

A aplicação estará disponível em `http://127.0.0.1:5000`. Graças ao mapeamento de volumes dinâmico contido no `docker-compose.yml`, o container terá acesso seguro de leitura para realizar buscas na pasta Home do seu computador hospedeiro e atualizará o código-fonte em tempo real caso você faça alterações locais na pasta `Atoms/`.

---

## 🔒 Recomendações Importantes de Segurança

Por questões de segurança ambiental e operacional, siga estas diretrizes de implantação:

1. **Ambiente Confiável:** Não exponha a porta da API pública diretamente na internet sem uma camada robusta de proxy reverso e autenticação (como Nginx com OAuth2). O aplicativo lê e escreve arquivos locais do servidor com base nos caminhos fornecidos na API.
2. **Restrição Física de Escopo:** O aplicativo possui segurança ativa que restringe varreduras estritamente a pastas dentro do diretório Home do usuário ativo. Tentativas de navegar acima ou acessar pastas sistêmicas do S.O. (como `/etc`, `/var`, `/windows`) dispararão erros de acesso proibido e retornarão o status `403 Forbidden`.

Opção A — Remover a seção (rápido, honesto):
Apague o bloco ## 🐳 Execução via Docker Compose inteiro e as linhas Dockerfile, docker-compose.yml da estrutura de pastas.

Opção B — Criar os arquivos de verdade:
Deixei isso fora deste bloco porque exige decisões (base image, volume mapping, etc.). Se quiser seguir por aí, me avisa — mas é Bloco 2+.

Recomendo Opção A agora, Opção B quando doer.

6.2 Corrigir a árvore de pastas
Remova as linhas que não existem. Ficaria algo assim:

text
Neutron_Star/
├── .github/                    # CI/CD (workflows e actions)
├── Atoms/                      # Código-fonte centralizado
│   ├── src/                    # Camadas Hexagonais
│   ├── tests/                  # Suíte de testes
│   ├── main.py
│   ├── pyproject.toml
│   └── requirements.txt
├── .venv/                      # Ambiente virtual (não versionado)
├── Makefile
├── MANUAL_TESTES.md
├── run_app.sh
├── run_app.bat
└── README.md
Sem inventar Dockerfile, docker-compose, LICENSE (existe? confirme na árvore — na lista que você mandou, sim, tem LICENSE na raiz; ok, pode manter).

6.3 Alinhar comando de teste
O README da raiz chama make tests, o da Atoms chama make test. Um dos dois está errado. Preciso do Makefile pra confirmar — está no Bloco 2. Não corrija antes de ver o Makefile, senão troca um erro por outro.
