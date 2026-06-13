# 🧲 Neutron Star

**Localizador e conversor de bookmarks HTML**
Um scanner inteligente que encontra arquivos de favoritos de navegadores em todo o sistema e os converte para **JSON**, **CSV** ou **PDF**.

> ⚠️ **Status:** Em desenvolvimento inicial – funcionalidades principais em implementação.

---

## 📋 Índice

- [Visão geral](#-visão-geral)
- [Funcionalidades planejadas](#-funcionalidades-planejadas)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [CLI de assistente IA](#-cli-de-assistente-ia)
- [Exemplos de uso futuro](#-exemplos-de-uso-futuro-scanner-de-bookmarks)
- [Como contribuir](#-como-contribuir)
- [Licença](#-licença)

---

## 🔭 Visão geral

O Neutron Star vasculha o sistema operacional em busca de arquivos HTML contendo listas de favoritos (bookmarks), extrai os dados estruturados e os exporta nos formatos mais comuns. Ideal para migrações, backups ou análise de links.

---

## ✨ Funcionalidades planejadas

- 🧱 **Arquitetura limpa (Clean Architecture)** – separação clara entre domínio, aplicação, infraestrutura e apresentação.
- 🖥️ **CLI intuitiva** – comandos simples para escanear diretórios, formatar saída e filtrar resultados.
- 🌍 **Multi-plataforma** – Windows, Linux e macOS (Python puro).
- 🤖 **Assistente de IA integrado** – agentes especializados para código, testes, revisão e documentação (via Ollama).

---

## 🧰 Tecnologias

| Categoria          | Ferramentas                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| Linguagem          | Python 3.10+                                                                |
| Dependências       | pip + venv (ou Poetry)                                                      |
| Parsing HTML       | BeautifulSoup4 / lxml                                                       |
| Geração de PDF     | ReportLab                                                                   |
| CLI principal      | argparse                                                                    |
| CLI de IA          | requests + Rich (markdown)                                                  |
| Testes             | pytest + pytest-cov                                                         |
| Arquitetura        | Clean Architecture                                                          |

---

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/DiasPedroQA/Neutron_Star.git
cd Neutron_Star

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# Instale as dependências de desenvolvimento
pip install -r requirements-dev.txt
```

---

## 🤖 CLI de assistente IA

O Neutron Star já conta com um assistente de IA local (via `neutron` CLI) para ajudar no desenvolvimento.
Ele se conecta a um servidor local como [Ollama](https://ollama.com) e oferece agentes especializados.

### Subcomandos disponíveis

| Comando       | Função                                                                 |
|---------------|------------------------------------------------------------------------|
| `ai-code`     | Análise e refatoração de código                                        |
| `ai-tests`    | Sugestões para testes (pytest)                                         |
| `ai-review`   | Revisão geral (código, testes, design)                                 |
| `ai-docs`     | Documentação (docstrings, README, comentários)                         |
| `ai-ci`       | Análise de pipelines, Makefile ou CI/CD                                |
| `ai-apply`    | Aplica automaticamente correções sugeridas (faz backup e roda testes)  |

### Opções comuns

- `file` – caminho do arquivo a ser analisado
- `--model` – nome do modelo local (padrão: `llama3.2:1b`)
- `--base-url` – URL da API local (padrão: `http://localhost:11434`)

### Pré‑requisitos

```bash
# Inicie o servidor Ollama
ollama serve

# Verifique se o modelo desejado está disponível
ollama pull llama3.2:1b
```

### Exemplos de uso da CLI de IA

> ⚠️ Execute sempre a partir da raiz do projeto, com a venv ativada.

```bash
# Análise de código
python -m src.presentation.cli.comandos ai-code src/presentation/cli/comandos.py

# Análise de testes
python -m src.presentation.cli.comandos ai-tests tests/test_infrastructure/test_escaneador_arquivos.py

# Revisão geral
python -m src.presentation.cli.comandos ai-review src/infrastructure/escaneador_arquivos.py

# Sugestões de documentação
python -m src.presentation.cli.comandos ai-docs README.md

# Aplicação automática de correções (cria arquivo.bak)
python -m src.presentation.cli.comandos ai-apply src/presentation/cli/comandos.py
```

> 💡 As respostas da IA são renderizadas com suporte a **Markdown** via biblioteca `Rich`.

---

## 🧪 Exemplos de uso futuro (scanner de bookmarks)

Os comandos abaixo ilustram a interface final que está em desenvolvimento:

```bash
# Buscar arquivos HTML em ~/Downloads e converter para JSON
neutron-star scan ~/Downloads --format json --output favoritos.json

# Varrer todo o sistema (cuidado!) e gerar um PDF
neutron-star scan / --format pdf --output meus_favoritos.pdf

# Apenas listar os arquivos encontrados, sem exportar
neutron-star locate /home/usuario
```

---

## 🤝 Como contribuir

1. **Fork** o projeto.
2. Crie uma **branch** para sua funcionalidade:
   `git checkout -b feature/nova-funcionalidade`
3. **Commit** suas alterações:
   `git commit -m 'Adiciona nova funcionalidade'`
4. **Push** para a branch:
   `git push origin feature/nova-funcionalidade`
5. Abra um **Pull Request**.

### Boas práticas

- Siga o estilo **PEP 8** e mantenha **docstrings consistentes** (Google style).
- Escreva **testes** para novas funcionalidades (pytest).
- Utilize a **CLI de IA** (`ai-code`, `ai-tests` etc.) para revisar seu código antes de abrir o PR.
- Garanta que o `make test` (ou `pytest`) passe com sucesso.

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

---

✨ Desenvolvido com 🐍 e ☕ por [DiasPedroQA](https://github.com/DiasPedroQA)
