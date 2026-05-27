# Neutron Star

Localizador e conversor de arquivos HTML de exportações de navegadores (favoritos/bookmarks). A aplicação varre o sistema operacional em busca de arquivos HTML com listas de links favoritos, extrai os dados estruturados e os converte para os formatos **JSON**, **CSV** ou **PDF**.

> **Status:** Em desenvolvimento inicial 🚧

---

## Funcionalidades (planejadas)

- 🔍 **Detecção automática** – escaneia diretórios (personalizáveis ou todo o sistema) em busca de arquivos `.html` que contenham favoritos exportados de navegadores (Chrome, Firefox, Edge, etc.).
- 📄 **Parsing robusto** – interpreta diferentes formatos comuns de exportação, como o formato Netscape (padrão de `bookmarks.html`).
- 📁 **Exportação múltipla** – converte a lista de favoritos para:
  - JSON (estrutura hierárquica ou plana)
  - CSV (tabela com colunas: título, URL, data de adição, tags)
  - PDF (relatório formatado)
- 🧩 **Arquitetura limpa (Clean Architecture)** – separação clara entre domínio, aplicação, infraestrutura e apresentação, facilitando manutenção e evolução.
- 🖥️ **Interface de linha de comando (CLI)** – uso simples via terminal, com opções para definir formato de saída, diretório de busca e filtros.
- 🌍 **Multi-plataforma** – funciona em Windows, Linux e macOS (graças ao Python).

---

## Tecnologias previstas

- **Linguagem:** Python 3.10+
- **Gerenciamento de dependências:** pip / venv (ou Poetry)
- **Parsing HTML:** BeautifulSoup4 (ou lxml)
- **Geração de PDF:** ReportLab
- **CLI:** Click (ou argparse)
- **Testes:** pytest
- **Arquitetura:** Clean Architecture

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/DiasPedroQA/Neutron_Star.git
cd Neutron_Star

# Crie e ative um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows

# Instale as dependências
pip install -r requirements.txt
```

---

## Uso (exemplo de CLI futuro)

```bash
# Buscar arquivos HTML no diretório ~/Downloads e converter para JSON
neutron-star scan ~/Downloads --format json --output favoritos.json

# Varrer todo o sistema (cuidado!) e gerar um PDF
neutron-star scan / --format pdf --output meus_favoritos.pdf

# Apenas listar os arquivos encontrados, sem exportar
neutron-star locate /home/usuario
```

*Os comandos acima são ilustrativos; a interface final está em desenvolvimento.*

---

## Como contribuir

Contribuições são bem-vindas!

1. Fork o projeto  
2. Crie uma branch com sua feature (`git checkout -b feature/nova-funcionalidade`)  
3. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)  
4. Push para a branch (`git push origin feature/nova-funcionalidade`)  
5. Abra um Pull Request

Siga o estilo de código PEP 8 e escreva testes para novas funcionalidades.

---

## Licença

Este projeto está sob a licença [MIT](LICENSE). Veja o arquivo `LICENSE` para mais detalhes.

---

## Contato

Dúvidas ou sugestões? Abra uma issue ou entre em contato: **<diaspedro.dev@gmail.com>**.
